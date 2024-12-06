import logging
from flask import Flask, render_template
from flask_socketio import SocketIO, emit
from ultralytics import YOLO
import cv2
import numpy as np
import base64
import time
from collections import Counter

# Flask and SocketIO initialization
app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

# Logger setup
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load YOLO model
model = YOLO("../training/models/ppe.pt")
classNames = ['Hardhat', 'Mask', 'NO-Hardhat', 'NO-Mask', 'NO-Safety Vest', 'Person', 'Safety Cone',
              'Safety Vest', 'machinery', 'vehicle']

# Cache for last detections
last_detections = []
stats = Counter()

@app.route('/')
def index():
    logger.info("Serving the index page.")
    return render_template('index.html')  # Render the webpage

@socketio.on('frame')
def handle_frame(data):
    global last_detections, stats

    try:
        # Decode base64 image from client
        img_data = base64.b64decode(data.split(',')[1])
        np_arr = np.frombuffer(img_data, np.uint8)
        img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

        # Perform YOLO detection
        results = model(img, stream=True, conf=0.5)  # Confidence threshold
        detections = []  # Store detection results
        stats = Counter()  # Reset stats for each frame

        for r in results:
            boxes = r.boxes
            for box in boxes:
                x1, y1, x2, y2 = box.xyxy[0]
                x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
                conf = round(float(box.conf[0]), 2)
                cls = int(box.cls[0])
                currentClass = classNames[cls]
                detections.append(currentClass)

                # Increment stats based on the class
                if currentClass == 'Person':
                    stats['people'] += 1
                elif currentClass in ['Hardhat', 'Safety Vest', 'Mask']:
                    stats[currentClass] += 1
                elif currentClass in ['NO-Hardhat', 'NO-Safety Vest', 'NO-Mask']:
                    stats[currentClass] += 1

                # Draw bounding box
                color = (0, 255, 0) if 'NO-' not in currentClass else (0, 0, 255)
                cv2.rectangle(img, (x1, y1), (x2, y2), color, 3)
                cv2.putText(img, f'{currentClass} {conf}', (x1, max(y1 - 10, 0)), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

        last_detections = detections  # Update the cache

        # Encode the modified image back to base64
        _, buffer = cv2.imencode('.jpg', img)
        encoded_img = base64.b64encode(buffer).decode('utf-8')

        emit('response_frame', f'data:image/jpeg;base64,{encoded_img}')
        emit('dashboard_stats', stats)  # Send stats to dashboard
        logger.debug("Processed frame and updated dashboard stats.")

    except Exception as e:
        logger.error(f"Error processing frame: {e}")

if __name__ == '__main__':
    logger.info("Starting the Flask server...")
    socketio.run(app, host='0.0.0.0', port=5000, debug=False, use_reloader=False)
