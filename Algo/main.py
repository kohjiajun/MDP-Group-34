import time
import os
import logging
from pathlib import Path
from algo.algo import MazeSolver 
from flask import Flask, request, jsonify
from flask_cors import CORS
from model import *
from helper import command_generator

# Setup logging
LOG_DIR = Path(__file__).resolve().parent / 'logs'
LOG_DIR.mkdir(exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(LOG_DIR / 'backend.log')
    ]
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)
# Defer heavy model loading to avoid long startup times
# model = load_model()
model = None

@app.route('/status', methods=['GET'])
def status():
    """
    This is a health check endpoint to check if the server is running
    :return: a json object with a key "result" and value "ok"
    """
    return jsonify({"result": "ok"})


@app.route('/path', methods=['POST'])
def path_finding():
    """
    This is the main endpoint for the path finding algorithm
    :return: a json object with a key "data" and value a dictionary with keys "distance", "path", and "commands"
    """
    try:
        # Log incoming request
        payload = request.get_json(silent=True)
        logger.info("Received /path request payload: %s", payload)

        if not payload:
            msg = "Empty or invalid JSON payload"
            logger.warning(msg)
            return jsonify({
                "data": {
                    'distance': 0.0,
                    'path': [],
                    'commands': []
                },
                "error": msg
            }), 400

        # Validate required fields
        required = ['obstacles', 'retrying', 'robot_x', 'robot_y', 'robot_dir']
        missing = [k for k in required if k not in payload]
        if missing:
            msg = f"Missing required fields: {missing}"
            logger.warning(msg)
            return jsonify({
                "data": {
                    'distance': 0.0,
                    'path': [],
                    'commands': []
                },
                "error": msg
            }), 400

        # Extract and validate types
        obstacles = payload['obstacles']
        retrying = payload.get('retrying', False)
        try:
            robot_x = int(payload['robot_x'])
            robot_y = int(payload['robot_y'])
            robot_direction = int(payload['robot_dir'])
        except Exception as e:
            msg = f"Invalid robot coordinates or direction: {e}"
            logger.exception(msg)
            return jsonify({
                "data": {
                    'distance': 0.0,
                    'path': [],
                    'commands': []
                },
                "error": msg
            }), 400

        # Initialize MazeSolver
        logger.info("Initializing MazeSolver at x=%s y=%s dir=%s", robot_x, robot_y, robot_direction)
        maze_solver = MazeSolver(20, 20, robot_x, robot_y, robot_direction, big_turn=None)

        # Add obstacles
        if not isinstance(obstacles, list):
            msg = "obstacles must be a list"
            logger.warning(msg)
            return jsonify({
                "data": {
                    'distance': 0.0,
                    'path': [],
                    'commands': []
                },
                "error": msg
            }), 400

        for ob in obstacles:
            try:
                maze_solver.add_obstacle(ob['x'], ob['y'], ob['d'], ob['id'])
            except Exception as e:
                logger.exception("Failed to add obstacle %s: %s", ob, e)
                # continue adding others

        start = time.time()
        # Compute path
        try:
            optimal_path, distance = maze_solver.get_optimal_order_dp(retrying=retrying)
        except Exception as e:
            logger.exception("Path computation failed: %s", e)
            return jsonify({
                "data": {
                    'distance': 0.0,
                    'path': [],
                    'commands': []
                },
                "error": f"Path computation failed: {e}"
            }), 500

        logger.info("Time taken to find shortest path: %s seconds", time.time() - start)
        logger.info("Distance to travel: %s units", distance)

        # Generate commands
        try:
            commands = command_generator(optimal_path, obstacles)
        except Exception as e:
            logger.exception("Command generation failed: %s", e)
            return jsonify({
                "data": {
                    'distance': distance,
                    'path': [p.get_dict() for p in optimal_path] if optimal_path else [],
                    'commands': []
                },
                "error": f"Command generation failed: {e}"
            }), 500

        # Build path results
        try:
            path_results = [optimal_path[0].get_dict()]
            i = 0
            for command in commands:
                if command.startswith("SNAP"):
                    continue
                if command.startswith("FIN"):
                    continue
                elif command.startswith("FW") or command.startswith("FS"):
                    i += int(command[2:]) // 10
                elif command.startswith("BW") or command.startswith("BS"):
                    i += int(command[2:]) // 10
                else:
                    i += 1
                # guard index
                if i < 0 or i >= len(optimal_path):
                    logger.warning("Index out of range while building path_results: i=%s len=%s", i, len(optimal_path))
                    break
                path_results.append(optimal_path[i].get_dict())
        except Exception as e:
            logger.exception("Failed to build path_results: %s", e)
            return jsonify({
                "data": {
                    'distance': distance,
                    'path': [],
                    'commands': commands if 'commands' in locals() else []
                },
                "error": f"Failed to build path results: {e}"
            }), 500

        return jsonify({
            "data": {
                'distance': distance,
                'path': path_results,
                'commands': commands
            },
            "error": None
        })
    except Exception as e:
        logger.exception("Unhandled exception in /path: %s", e)
        return jsonify({
            "data": {
                'distance': 0.0,
                'path': [],
                'commands': []
            },
            "error": str(e)
        }), 500


@app.route('/image', methods=['POST'])
def image_predict():
    """
    This is the main endpoint for the image prediction algorithm
    :return: a json object with a key "result" and value a dictionary with keys "obstacle_id" and "image_id"
    """
    global model
    # lazy-load model to avoid long startup time
    if model is None:
        try:
            logger.info("Lazy-loading model on first /image request")
            model = load_model()
            logger.info("Model loaded successfully")
        except Exception as e:
            logger.exception("Failed to load model: %s", e)
            return jsonify({"error": f"Model load failed: {e}"}), 500

    file = request.files.get('file')
    if file is None:
        return jsonify({"error": "No file provided"}), 400
    filename = file.filename
    file.save(os.path.join('uploads', filename))
    # filename format: "<timestamp>_<obstacle_id>_<signal>.jpeg"
    constituents = file.filename.split("_")
    obstacle_id = constituents[1]

    ## Week 8 ## 
    #signal = constituents[2].strip(".jpg")
    #image_id = predict_image(filename, model, signal)

    ## Week 9 ## 
    # We don't need to pass in the signal anymore
    image_id = predict_image_week_9(filename,model)

    # Return the obstacle_id and image_id
    result = {
        "obstacle_id": obstacle_id,
        "image_id": image_id
    }
    return jsonify(result)

@app.route('/stitch', methods=['GET'])
def stitch():
    """
    This is the main endpoint for the stitching command. Stitches the images using two different functions, in effect creating two stitches, just for redundancy purposes
    """
    img = stitch_image()
    img.show()
    img2 = stitch_image_own()
    img2.show()
    return jsonify({"result": "ok"})

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5002))
    print(f"Starting server on port {port}")
    app.run(host='0.0.0.0', port=port, debug=True)

