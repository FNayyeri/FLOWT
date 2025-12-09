import cv2
import json
from pathlib import Path
from ultralytics import YOLO
import numpy as np
from .bbox_drawer import BBoxDrawer

class YOLOInference:
    def __init__(self):
        self.model = None
        self.results_dir = Path("data/results")
        self.results_dir.mkdir(parents=True, exist_ok=True)
        self.bbox_drawer = BBoxDrawer()
    
    def load_model(self, model_path):
        """Load YOLO model from path"""
        try:
            self.model = YOLO(model_path)
            return True
        except Exception as e:
            print(f"Error loading model: {e}")
            return False
    
    def run_inference(self, video_path, model_path, confidence_threshold=0.5):
        """Run YOLO inference on video"""
        if not self.load_model(model_path):
            raise Exception("Failed to load YOLO model")
        
        # Create model-specific directories
        model_name = Path(model_path).stem
        video_name = Path(video_path).stem
        model_results_dir = self.results_dir / model_name
        model_results_dir.mkdir(exist_ok=True)
        frames_dir = model_results_dir / f"{video_name}_frames"
        frames_dir.mkdir(exist_ok=True)
        
        cap = cv2.VideoCapture(str(video_path))
        detections = []
        frame_count = 0
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            # Run inference with lower confidence for fine-tuned models
            inference_conf = confidence_threshold
            if "ft" in model_path.lower() or "fine" in model_path.lower():
                inference_conf = max(0.1, confidence_threshold * 0.5)  # Lower threshold for fine-tuned models
            
            results = self.model(frame, conf=inference_conf)
            
            # Debug: Print detection info for first few frames
            if frame_count < 5:
                print(f"Frame {frame_count}: Using conf={inference_conf}, Found {len(results[0].boxes) if results[0].boxes is not None else 0} detections")
            
            # Process results and save frames with detections
            frame_has_detections = False
            frame_copy = frame.copy()
            
            for result in results:
                boxes = result.boxes
                if boxes is not None and len(boxes) > 0:
                    for box in boxes:
                        model_class_name = self.model.names[int(box.cls)]
                        confidence = float(box.conf)
                        bbox = box.xyxy[0].tolist()
                        
                        # Map model class to config class (use model class if not in config)
                        if model_class_name in self.bbox_drawer.class_names:
                            config_class_name = model_class_name
                        else:
                            # Use first config class as fallback
                            config_class_name = self.bbox_drawer.class_names[0] if self.bbox_drawer.class_names else model_class_name
                        
                        detection = {
                            'frame': frame_count,
                            'class': config_class_name,
                            'confidence': confidence,
                            'bbox': bbox,
                            'is_true_positive': True,
                            'tags': [],
                            'frame_image': f"results/{model_name}/{video_name}_frames/frame_{frame_count}.jpg"
                        }
                        detections.append(detection)
                        
                        # Draw bounding box using config class for consistent colors
                        frame_copy = self.bbox_drawer.draw_bbox(frame_copy, bbox, config_class_name, confidence, show_label=False)
                        frame_has_detections = True
            
            # Save annotated frame if it has detections
            if frame_has_detections:
                frame_path = frames_dir / f"frame_{frame_count}.jpg"
                cv2.imwrite(str(frame_path), frame_copy)
            
            frame_count += 1
        
        cap.release()
        
        # Save results
        video_name = Path(video_path).stem
        results_file = model_results_dir / f"{video_name}_detections.json"
        with open(results_file, 'w') as f:
            json.dump(detections, f, indent=2)
        
        return detections
    
    def get_model_info(self, model_path):
        """Get information about the model"""
        if self.load_model(model_path):
            return {
                'classes': list(self.model.names.values()),
                'num_classes': len(self.model.names)
            }
        return None