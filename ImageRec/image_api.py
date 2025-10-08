# image_api.py (updated)
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse, StreamingResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import numpy as np
import cv2
import io
import uvicorn
import os
from typing import List, Dict, Any
from ultralytics import YOLO
import time
import threading
import asyncio
from PIL import Image
import shutil

# ============ CONFIG ============
WEIGHTS = "best_roboflow_image_bg.pt"
CONF_THRESH = 0.20    # detection confidence threshold
IMG_SIZE = 640        # YOLO inference imgsz (keeps perf reasonable)
MAX_DETECTIONS = 50
CLASSNAME_TO_IMAGEID = {
    # optional mapping if you need it; you said you already changed SYMBOL_MAP in repo
}
_latest_detections = [] 
# ================================

app = FastAPI(title="YOLO Image-Rec API (MDP)")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

print("Loading YOLO model from:", WEIGHTS)
model = YOLO(WEIGHTS)
print("Model loaded. Names:", model.names)

# Globals used for MJPEG streaming
_latest_frame_jpeg = None          # bytes
_frame_event = threading.Event()
_frame_lock = threading.Lock()

def read_imagefile_to_cv2(file_bytes: bytes):
    arr = np.frombuffer(file_bytes, dtype=np.uint8)
    gray = cv2.imdecode(arr, cv2.IMREAD_GRAYSCALE)
    img = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
    return img

def annotate_image(img: np.ndarray, detections: List[Dict[str, Any]], obstacle_id: str = None) -> np.ndarray:
    """Draw boxes + labels on image (in-place copy) and return annotated image."""
    out = img.copy()
    h, w = out.shape[:2]
    for det in detections:
        x1, y1, x2, y2 = map(int, det["box"])
        cls = det["class"]
        conf = det["conf"]
        # color based on hash of class name (deterministic)
        color = tuple(int((hash(cls) >> (8*i)) & 255) for i in range(3))
        # cv2 uses BGR; color tuple is (B,G,R)
        cv2.rectangle(out, (x1, y1), (x2, y2), color, 2)
        
        # Include obstacle_id in label if provided
        if obstacle_id:
            label = f"ID:{obstacle_id} {cls} {conf:.2f}"
        else:
            label = f"{cls} {conf:.2f}"
        
        # put label background
        (text_w, text_h), baseline = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
        cv2.rectangle(out, (x1, y1 - text_h - baseline - 4), (x1 + text_w + 6, y1), color, -1)
        cv2.putText(out, label, (x1 + 3, y1 - 3), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255), 1, cv2.LINE_AA)
    return out

def predict_image_from_array(img: np.ndarray) -> tuple[str, List[Dict[str, Any]]]:
    """Predict the image with the detections and return the top class and all detections."""
    results = model.predict(source=img, conf=CONF_THRESH, imgsz=IMG_SIZE, verbose=False)
    res = results[0]
    detections: List[Dict[str, Any]] = []
    
    if hasattr(res, "boxes") and res.boxes is not None and len(res.boxes) > 0:
        boxes = res.boxes
        xyxy = boxes.xyxy.tolist() if hasattr(boxes.xyxy, "tolist") else boxes.xyxy
        confs = boxes.conf.tolist() if hasattr(boxes.conf, "tolist") else boxes.conf
        cls_ids = boxes.cls.tolist() if hasattr(boxes.cls, "tolist") else boxes.cls
        
        for b, c, cl in zip(xyxy, confs, cls_ids):
            class_name = str(model.names[int(cl)]) if (model.names and int(cl) in model.names) else str(int(cl))
            detections.append({
                "class": class_name,
                "conf": float(c),
                "box": [float(b[0]), float(b[1]), float(b[2]), float(b[3])]
            })
    
    # Get top prediction
    if detections:
        top = max(detections, key=lambda d: d["conf"])
        top_class = top["class"]
        image_id = CLASSNAME_TO_IMAGEID.get(top_class, top_class)
    else:
        image_id = "NA"
    
    return image_id, detections

def stitch_image():
    """
    Stitches all the images captured during the robot run and saves it to the uploads/stitched folder.
    Images are sorted by obstacle_id extracted from filename format: <timestamp>_<obstacle_id>_<signal>.jpg
    Returns the path to the stitched image.
    """

    try:
        # Create directories if they don't exist
        uploads_folder = 'uploads'
        stitched_folder = os.path.join(uploads_folder, 'stitched')
        originals_folder = os.path.join(uploads_folder, 'originals')
        os.makedirs(stitched_folder, exist_ok=True)
        os.makedirs(originals_folder, exist_ok=True)

        # Get all .jpg files from uploads directory
        all_files = os.listdir(uploads_folder)
        img_files = [f for f in all_files if f.endswith('.jpg')]
        
        if not img_files:
            print("No images found to stitch")
            return None
        
        # Sort images by obstacle_id (extracted from filename)
        def extract_obstacle_id(filename):
            try:
                # Format: <timestamp>_<obstacle_id>_<signal>.jpg
                parts = filename.split('_')
                if len(parts) >= 2:
                    return int(parts[1])  # obstacle_id
                return 0
            except:
                return 0
        
        img_files.sort(key=extract_obstacle_id)
        
        # Create full paths for images
        img_paths = [os.path.join(uploads_folder, f) for f in img_files]
        
        print(f"Found {len(img_paths)} images to stitch")
        
        # Open all images
        images = [Image.open(x) for x in img_paths]
        
        # Get the width and height of each image
        widths, heights = zip(*(i.size for i in images))
        
        # Calculate the total width and max height (stitching horizontally)
        total_width = sum(widths)
        max_height = max(heights)
        
        # Create a new blank image with the calculated dimensions
        stitched_img = Image.new('RGB', (total_width, max_height))
        
        # Paste images horizontally
        x_offset = 0
        for im in images:
            stitched_img.paste(im, (x_offset, 0))
            x_offset += im.size[0]
        
        # Save the stitched image with timestamp
        stitched_filename = f'stitched-{int(time.time())}.jpg'
        stitched_path = os.path.join(stitched_folder, stitched_filename)
        stitched_img.save(stitched_path, quality=95)
        
        print(f"Stitched image saved to: {stitched_path}")
        
        # Move original images to originals subdirectory
        for img_path in img_paths:
            dest_path = os.path.join(originals_folder, os.path.basename(img_path))
            shutil.move(img_path, dest_path)
        
        print(f"Moved {len(img_paths)} original images to {originals_folder}")
        
        return stitched_path
    
    except Exception as e:
        print(f"Error in stitch_image: {e}")
        return None

@app.post("/snap_image")
async def snap_image(file: UploadFile = File(...)):
    """
    This is the main endpoint for the image snap 
    :return: a json object with keys "obstacle_id", "image_id", and "detections"
    """
    # Create uploads directory if it doesn't exist
    os.makedirs("uploads", exist_ok=True)
    
    try:
        content = await file.read()
        img = read_imagefile_to_cv2(content)
        if img is None:
            raise HTTPException(status_code=400, detail="Could not decode image")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to read image: {e}")

    filename = file.filename
    
    # filename format: "<timestamp>_<obstacle_id>_<signal>.jpeg"
    constituents = filename.split("_")
    obstacle_id = constituents[1]
    
    # Predict using the numpy array and get detections (unpack the tuple correctly)
    image_id, detections = predict_image_from_array(img)
    
    # Annotate the image with bounding boxes and labels (including obstacle_id)
    annotated_img = annotate_image(img, detections, obstacle_id=obstacle_id)
    
    # Save the annotated image
    file_path = os.path.join('uploads', filename)
    cv2.imwrite(file_path, annotated_img)
    
    print(f"✓ Saved annotated image: {file_path} (Detected: {image_id})")

    # Return the obstacle_id, image_id, and detections
    result = {
        "obstacle_id": obstacle_id,
        "image_id": image_id,
        "detections": detections
    }
    return JSONResponse(result)

@app.get("/status")
def status():
    return JSONResponse({"status": "ok", "timestamp": time.time()})

@app.get("/stitch")
def stitch():
    """
    Endpoint to trigger image stitching of all captured images from the current robot run.
    """
    try:
        stitched_path = stitch_image()
        
        if stitched_path:
            return JSONResponse({
                "status": "success",
                "message": "Images stitched successfully",
                "stitched_image_path": stitched_path
            })
        else:
            return JSONResponse({
                "status": "no_images",
                "message": "No images found to stitch"
            })
    except Exception as e:
        return JSONResponse({
            "status": "error",
            "message": f"Error stitching images: {str(e)}"
        }, status_code=500)

@app.post("/image")
async def predict_image(file: UploadFile = File(...)):
    """
    Accept multipart file upload, run YOLO, return JSON (image_id + detections).
    Also update the latest annotated JPEG for the MJPEG stream.
    """
    global _latest_frame_jpeg, _frame_event

    try:
        content = await file.read()
        img = read_imagefile_to_cv2(content)
        if img is None:
            raise HTTPException(status_code=400, detail="Could not decode image")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to read image: {e}")

    # Run inference
    try:
        results = model.predict(source=img, conf=CONF_THRESH, imgsz=IMG_SIZE, verbose=False)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Model inference error: {e}")

    res = results[0]
    detections: List[Dict[str, Any]] = []

    if hasattr(res, "boxes") and res.boxes is not None and len(res.boxes) > 0:
        boxes = res.boxes
        xyxy = boxes.xyxy.tolist() if hasattr(boxes.xyxy, "tolist") else boxes.xyxy
        confs = boxes.conf.tolist() if hasattr(boxes.conf, "tolist") else boxes.conf
        cls_ids = boxes.cls.tolist() if hasattr(boxes.cls, "tolist") else boxes.cls

        for b, c, cl in zip(xyxy, confs, cls_ids):
            class_name = str(model.names[int(cl)]) if (model.names and int(cl) in model.names) else str(int(cl))
            detections.append({
                "class": class_name,
                "conf": float(c),
                "box": [float(b[0]), float(b[1]), float(b[2]), float(b[3])]
            })

    if detections:
        top = max(detections, key=lambda d: d["conf"])
        top_class = top["class"]
        image_id = CLASSNAME_TO_IMAGEID.get(top_class, top_class)
    else:
        image_id = "NA"
    
    global _latest_detections
    _latest_detections = detections

    # Annotate and encode latest frame to JPEG for viewer
    annotated = annotate_image(img, detections, obstacle_id=1)
    success, jpeg = cv2.imencode('.jpg', annotated, [int(cv2.IMWRITE_JPEG_QUALITY), 85])
    if success:
        with _frame_lock:
            _latest_frame_jpeg = jpeg.tobytes()
            _frame_event.set()

    payload = {"image_id": image_id, "detections": detections}
    return JSONResponse(payload)

@app.get("/latest_detections")
def latest_detections():
    global _latest_detections
    return JSONResponse({"detections": _latest_detections})

async def mjpeg_generator():
    """
    Safe MJPEG generator: yields frames when available, else keeps last frame.
    """
    global _latest_frame_jpeg, _frame_event
    while True:
        try:
            await asyncio.wait_for(asyncio.to_thread(_frame_event.wait), timeout=5.0)
            event_set = True
        except asyncio.TimeoutError:
            event_set = False

        with _frame_lock:
            frame = _latest_frame_jpeg

        # if no frame yet, use blank image
        if frame is None:
            blank = 255 * np.ones((480, 640, 3), dtype=np.uint8)
            _, jpeg = cv2.imencode(".jpg", blank)
            frame = jpeg.tobytes()

        yield (b"--frame\r\n"
               b"Content-Type: image/jpeg\r\n\r\n" + frame + b"\r\n")

        if event_set:
            _frame_event.clear()

        await asyncio.sleep(0.01)

@app.get("/video_feed")
async def video_feed():
    """
    MJPEG stream of the latest annotated frames.
    """
    return StreamingResponse(
        mjpeg_generator(),
        media_type="multipart/x-mixed-replace; boundary=frame"
    )

@app.get("/view")
def view_page():
    html = """
    <!doctype html>
    <html>
      <head>
        <title>YOLO Live View</title>
        <style>
          body { background:#111; color:#eee; font-family:sans-serif; }
          #stream { max-width:100%; height:auto; border:3px solid #333; }
          #detections { margin-top: 20px; font-size: 1rem; }
        </style>
      </head>
      <body>
        <h2>YOLO Live View</h2>
        <p>Stream below:</p>
        <img id="stream" src="/video_feed"/>
        <div id="detections">
          <h3>Latest Detections:</h3>
          <ul id="det_list"></ul>
        </div>

        <script>
          async function updateDetections() {
            try {
              const resp = await fetch('/latest_detections');
              const data = await resp.json();
              const ul = document.getElementById('det_list');
              ul.innerHTML = '';
              if (data.detections && data.detections.length > 0) {
                data.detections.forEach(d => {
                  const li = document.createElement('li');
                  li.textContent = `${d.class} (conf: ${d.conf.toFixed(2)})`;
                  ul.appendChild(li);
                });
              } else {
                ul.innerHTML = '<li>None</li>';
              }
            } catch(e) {
              console.error(e);
            }
          }
          setInterval(updateDetections, 500); // update every 0.5s
        </script>
      </body>
    </html>
    """
    return HTMLResponse(content=html)


if __name__ == "__main__":
    uvicorn.run("image_api:app", host="0.0.0.0", port=5003, log_level="info", reload=True)