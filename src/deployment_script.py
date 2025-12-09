#!/usr/bin/env python3
import cv2
import numpy as np
from ultralytics import YOLO
import time

class EdgeDetector:
    def __init__(self, model_path, conf_threshold={conf_threshold}):
        self.model = YOLO(model_path)
        self.conf_threshold = conf_threshold
        
    def detect_stream(self, camera_id=0):
        cap = cv2.VideoCapture(camera_id)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, {input_size.split('x')[0]})
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, {input_size.split('x')[1]})
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
                
            results = self.model(frame, conf=self.conf_threshold)
            annotated_frame = results[0].plot()
            
            cv2.imshow('Marine Litter Detection', annotated_frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
                
        cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    detector = EdgeDetector("student_model.pt")
    detector.detect_stream(0)