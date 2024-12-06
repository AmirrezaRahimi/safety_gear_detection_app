import cv2
import numpy as np
from ultralytics import YOLO
import base64
from collections import Counter

class ObjectDetector:
    def __init__(self, model_path):
        self.model = YOLO(model_path)
        self.class_names = ['Hardhat', 'Mask', 'NO-Hardhat', 'NO-Mask', 'NO-Safety Vest', 'Person', 'Safety Cone',
                            'Safety Vest', 'machinery', 'vehicle']
        self.confidence_threshold = 0.5

    def process_frame(self, frame_data):
        # Decode base64 image
        img_data = base64.b64decode(frame_data.split(',')[1])
        np_arr = np.frombuffer(img_data, np.uint8)
        img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

        # Perform detection
        results = self.model(img, stream=True, conf=self.confidence_threshold)
        
        detections = []
        stats = Counter()

        for r in results:
            boxes = r.boxes
            for box in boxes:
                x1, y1, x2, y2 = box.xyxy[0]
                conf = float(box.conf[0])
                cls = int(box.cls[0])
                current_class = self.class_names[cls]
                
                detections.append({
                    'class': current_class,
                    'confidence': conf,
                    'bbox': [int(x1), int(y1), int(x2), int(y2)]
                })

                if current_class == 'Person':
                    stats['people'] += 1
                elif current_class in ['Hardhat', 'Safety Vest', 'Mask']:
                    stats[current_class] += 1
                elif current_class in ['NO-Hardhat', 'NO-Safety Vest', 'NO-Mask']:
                    stats[current_class] += 1

        return detections, dict(stats)

    def update_settings(self, new_settings):
        if 'confidence_threshold' in new_settings:
            self.confidence_threshold = float(new_settings['confidence_threshold'])
