#!/usr/bin/env python3
import time, requests
from settings import API_IP, API_PORT
from logger import prepare_logger

logger = prepare_logger()
url = f"http://{API_IP}:{API_PORT}/latest_detections"

while True:
    try:
        r = requests.get(url, timeout=2)
        if r.status_code == 200:
            data = r.json()
            detections = data.get("detections", [])
            if detections:
                top = max(detections, key=lambda d: d["conf"])
                logger.info(f"Detected: {top['class']} ({top['conf']:.2f})")
            else:
                logger.info("No detections")
    except Exception as e:
        logger.error(f"Error polling: {e}")
    time.sleep(0.5)
