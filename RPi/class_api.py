# image_api.py (fixed)
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse, StreamingResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import numpy as np
import cv2
import io
import uvicorn
import os
from typing import List, Dict, Any, Optional
from ultralytics import YOLO
import time
import threading
import asyncio
import requests  # used if PUSH_TO_RPI True
import traceback

# ============ CONFIG ============
WEIGHTS = "/Users/garv/Desktop/MDP/yolov8_custom/weights/best.pt"
CONF_THRESH = 0.25    # detection confidence threshold
IMG_SIZE = 640        # YOLO inference imgsz
MAX_DETECTIONS = 50
CAMERA_IDX = 0        # change if your webcam is at another index
PUSH_TO_RPI = False   # set True if you want PC to POST results back to RPi
RPI_PUSH_URL = "http://<RPi-IP>:<RPi-port>/process_detections"  # set if PUSH_TO_RPI True
CLASSNAME_TO_IMAGEID = {}  # optional mapping as you had
# ================================

app = FastAPI(title="YOLO Image-Rec API (MDP)")

# ---- Globals (initialized BEFORE starting webcam thread) ----
print("Loading YOLO model from:", WEIGHTS)
model = YOLO(WEIGHTS)
print("Model loaded. Names:", model.names if hasattr(model, "names") else "UNKNOWN")

_latest_frame_jpeg: Optional[bytes] = None
_frame_event = threading.Event()
_frame_lock = threading.Lock()
_latest_detections: List[Dict[str, Any]] = []
_webcam_ok = False
_last_frame_time = 0.0

# ---------------- Helper functions ----------------
def read_imagefile_to_cv2(file_bytes: bytes):
    arr = np.frombuffer(file_bytes, dtype=np.uint8)
    img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    return img

def annotate_image(img: np.ndarray, detections: List[Dict[str, Any]]) -> np.ndarray:
    out = img.copy()
    h, w = out.shape[:2]
    for det in detections:
        x1, y1, x2, y2 = map(int, det["box"])
        cls = det["class"]
        conf = det["conf"]
        color = tuple(int((hash(cls) >> (8*i)) & 255) for i in range(3))
        cv2.rectangle(out, (x1, y1), (x2, y2), color, 2)
        label = f"{cls} {conf:.2f}"
        (text_w, text_h), baseline = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
        cv2.rectangle(out, (x1, y1 - text_h - baseline - 4), (x1 + text_w + 6, y1), color, -1)
        cv2.putText(out, label, (x1 + 3, y1 - 3), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255), 1, cv2.LINE_AA)
    return out

def _safe_post_to_rpi(payload: dict):
    """Post detections to RPi in a fire-and-forget background thread (non-blocking)."""
    if not PUSH_TO_RPI:
        return
    def _post():
        try:
            requests.post(RPI_PUSH_URL, json=payload, timeout=1.0)
        except Exception as e:
            print("Warning: failed to push to RPi:", e)
    threading.Thread(target=_post, daemon=True).start()

# ---------------- Webcam thread ----------------
def webcam_loop():
    global _latest_frame_jpeg, _frame_event, _latest_detections, _webcam_ok, _last_frame_time
    cap = cv2.VideoCapture(CAMERA_IDX)
    if not cap.isOpened():
        print(f"ERROR: Cannot open webcam index {CAMERA_IDX}")
        _webcam_ok = False
        return
    _webcam_ok = True
    print(f"Webcam opened (index={CAMERA_IDX}). Starting capture loop...")

    while True:
        try:
            ret, frame = cap.read()
            if not ret or frame is None:
                # small sleep to avoid busy spin if camera disconnects temporarily
                time.sleep(0.1)
                continue

            _last_frame_time = time.time()

            # Run YOLO inference (non-verbose)
            try:
                results = model.predict(source=frame, conf=CONF_THRESH, imgsz=IMG_SIZE, verbose=False)
            except Exception as e:
                print("Model inference error in webcam_loop:", e)
                traceback.print_exc()
                time.sleep(0.1)
                continue

            res = results[0]
            detections: List[Dict[str, Any]] = []

            if hasattr(res, "boxes") and res.boxes is not None and len(res.boxes) > 0:
                boxes = res.boxes
                # boxes.* might be tensors or lists depending on ultralytics version
                xyxy = boxes.xyxy.tolist() if hasattr(boxes.xyxy, "tolist") else list(boxes.xyxy)
                confs = boxes.conf.tolist() if hasattr(boxes.conf, "tolist") else list(boxes.conf)
                cls_ids = boxes.cls.tolist() if hasattr(boxes.cls, "tolist") else list(boxes.cls)
                for b, c, cl in zip(xyxy, confs, cls_ids):
                    class_name = str(model.names[int(cl)]) if (getattr(model, "names", None) and int(cl) in model.names) else str(int(cl))
                    detections.append({
                        "class": class_name,
                        "conf": float(c),
                        "box": [float(b[0]), float(b[1]), float(b[2]), float(b[3])]
                    })

            # update shared detection state
            with _frame_lock:
                _latest_detections = detections  # NOTE: rebind - safe since guarded by lock below when used
            # annotate and update frame for MJPEG
            annotated = annotate_image(frame, detections)
            success, jpeg = cv2.imencode('.jpg', annotated, [int(cv2.IMWRITE_JPEG_QUALITY), 85])
            if success:
                with _frame_lock:
                    _latest_frame_jpeg = jpeg.tobytes()
                    _frame_event.set()

            # optionally push to RPi asynchronously
            if PUSH_TO_RPI:
                payload = {"image_id": CLASSNAME_TO_IMAGEID.get(detections[0]["class"], detections[0]["class"]) if detections else "NA",
                           "detections": detections}
                _safe_post_to_rpi(payload)

            # small sleep to regulate CPU (adjust as needed)
            time.sleep(0.03)

        except Exception as e:
            print("Exception in webcam_loop:", e)
            traceback.print_exc()
            time.sleep(0.5)

# start webcam thread (after model & globals defined)
threading.Thread(target=webcam_loop, daemon=True).start()

# ---------------- Web endpoints ----------------
@app.get("/status")
def status():
    return JSONResponse({
        "status": "ok",
        "timestamp": time.time(),
        "webcam_ok": _webcam_ok,
        "last_frame_age_s": time.time() - _last_frame_time if _last_frame_time else None,
        "model_names_count": len(model.names) if getattr(model, "names", None) else None
    })

@app.get("/stitch")
def stitch():
    return JSONResponse({"status": "stitch_received"})

@app.post("/image")
async def predict_image(file: UploadFile = File(...)):
    """
    Accept multipart file upload, run YOLO, return JSON (image_id + detections).
    Also update the latest annotated JPEG for the MJPEG stream.
    """
    global _latest_frame_jpeg, _frame_event, _latest_detections

    try:
        content = await file.read()
        img = read_imagefile_to_cv2(content)
        if img is None:
            raise HTTPException(status_code=400, detail="Could not decode image")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to read image: {e}")

    try:
        results = model.predict(source=img, conf=CONF_THRESH, imgsz=IMG_SIZE, verbose=False)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Model inference error: {e}")

    res = results[0]
    detections: List[Dict[str, Any]] = []
    if hasattr(res, "boxes") and res.boxes is not None and len(res.boxes) > 0:
        boxes = res.boxes
        xyxy = boxes.xyxy.tolist() if hasattr(boxes.xyxy, "tolist") else list(boxes.xyxy)
        confs = boxes.conf.tolist() if hasattr(boxes.conf, "tolist") else list(boxes.conf)
        cls_ids = boxes.cls.tolist() if hasattr(boxes.cls, "tolist") else list(boxes.cls)
        for b, c, cl in zip(xyxy, confs, cls_ids):
            class_name = str(model.names[int(cl)]) if (getattr(model, "names", None) and int(cl) in model.names) else str(int(cl))
            detections.append({
                "class": class_name,
                "conf": float(c),
                "box": [float(b[0]), float(b[1]), float(b[2]), float(b[3])]
            })

    image_id = CLASSNAME_TO_IMAGEID.get(detections[0]["class"], detections[0]["class"]) if detections else "NA"

    with _frame_lock:
        _latest_detections = detections
    # update latest annotated frame for viewer (so both upload and webcam go through same viewer)
    annotated = annotate_image(img, detections)
    success, jpeg = cv2.imencode('.jpg', annotated, [int(cv2.IMWRITE_JPEG_QUALITY), 85])
    if success:
        with _frame_lock:
            _latest_frame_jpeg = jpeg.tobytes()
            _frame_event.set()

    payload = {"image_id": image_id, "detections": detections}
    return JSONResponse(payload)

@app.get("/latest_detections")
def latest_detections():
    with _frame_lock:
        return JSONResponse({"detections": _latest_detections})

async def mjpeg_generator():
    """
    Safe MJPEG generator: yields frames when available, else keeps last frame.
    """
    global _latest_frame_jpeg, _frame_event
    boundary = b"--frame\r\n"
    while True:
        try:
            # wait up to 5s for a new frame, else proceed to send last (or blank)
            try:
                await asyncio.wait_for(asyncio.to_thread(_frame_event.wait), timeout=5.0)
                event_set = True
            except asyncio.TimeoutError:
                event_set = False

            with _frame_lock:
                frame = _latest_frame_jpeg

            if frame is None:
                # send a blank gray frame so the client gets a valid JPEG
                blank = 127 * np.ones((480, 640, 3), dtype=np.uint8)
                _, jpeg = cv2.imencode(".jpg", blank)
                frame = jpeg.tobytes()

            yield (boundary +
                   b"Content-Type: image/jpeg\r\n\r\n" + frame + b"\r\n")

            if event_set:
                _frame_event.clear()

            await asyncio.sleep(0.01)
        except asyncio.CancelledError:
            break
        except Exception as e:
            print("Exception in mjpeg_generator:", e)
            traceback.print_exc()
            await asyncio.sleep(0.5)

@app.get("/video_feed")
async def video_feed():
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
    uvicorn.run("class_api:app", host="0.0.0.0", port=5000, log_level="info", reload=True)
