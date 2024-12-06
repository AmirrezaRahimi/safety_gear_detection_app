import logging
from flask import Flask, render_template
from flask_socketio import SocketIO, emit
from ultralytics import YOLO
import cv2
import numpy as np
import base64
from collections import Counter
import time

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

model = YOLO("../training/models/ppe.pt")
classNames = ['Hardhat', 'Mask', 'NO-Hardhat', 'NO-Mask', 'NO-Safety Vest', 'Person', 'Safety Cone',
              'Safety Vest', 'machinery', 'vehicle']

last_process_time = 0
PROCESS_INTERVAL = 0.1  # Process every 100ms

@app.route('/')
def index():
    logger.info("Serving the index page.")
    return render_template('index.html')

@socketio.on('frame')
def handle_frame(data):
    global last_process_time
    current_time = time.time()
    
    if current_time - last_process_time < PROCESS_INTERVAL:
        return  # Skip this frame
    
    last_process_time = current_time

    try:
        img_data = base64.b64decode(data.split(',')[1])
        np_arr = np.frombuffer(img_data, np.uint8)
        img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

        results = model(img, stream=True, conf=0.5)
        detections = []
        stats = Counter()

        for r in results:
            boxes = r.boxes
            for box in boxes:
                x1, y1, x2, y2 = box.xyxy[0]
                conf = float(box.conf[0])
                cls = int(box.cls[0])
                currentClass = classNames[cls]
                
                detections.append({
                    'class': currentClass,
                    'confidence': conf,
                    'bbox': [int(x1), int(y1), int(x2), int(y2)]
                })

                if currentClass == 'Person':
                    stats['people'] += 1
                elif currentClass in ['Hardhat', 'Safety Vest', 'Mask']:
                    stats[currentClass] += 1
                elif currentClass in ['NO-Hardhat', 'NO-Safety Vest', 'NO-Mask']:
                    stats[currentClass] += 1

        emit('detection_results', {'detections': detections, 'stats': dict(stats)})
        logger.debug("Processed frame and sent detection results.")

    except Exception as e:
        logger.error(f"Error processing frame: {e}")

if __name__ == '__main__':
    logger.info("Starting the Flask server...")
    socketio.run(app, host='0.0.0.0', port=5000, debug=False, use_reloader=False)
