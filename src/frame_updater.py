import cv2
import yaml
from pathlib import Path
from .bbox_drawer import BBoxDrawer

class FrameUpdater:
    def __init__(self):
        self.bbox_drawer = BBoxDrawer()
    
    def update_frame_with_curated_class(self, frame_path, detection, curated_class):
        """Update frame with new bounding box color based on curated class"""
        frame = cv2.imread(str(frame_path))
        if frame is None:
            return False
        
        # Draw new bounding box with curated class color
        bbox = detection['bbox']
        confidence = detection['confidence']
        
        updated_frame = self.bbox_drawer.draw_bbox(
            frame, bbox, curated_class, confidence, show_label=False
        )
        
        # Save updated frame
        cv2.imwrite(str(frame_path), updated_frame)
        return True
    
    def update_frame_with_detection_id(self, frame_path, detection, curated_class, detection_id):
        """Update frame with detection ID and class color"""
        frame = cv2.imread(str(frame_path))
        if frame is None:
            return False

        bbox = detection['bbox']
        curated_class = detection.get('corrected_class', detection.get('class', 'Unknown'))
        confidence = detection.get('confidence', 0)
 
        # Draw with labels and track ID for video generation
        frame = self.bbox_drawer.draw_bbox(frame, bbox, curated_class, confidence, show_label=False)
        cv2.imwrite(str(frame_path), frame)





        # # Draw bounding box
        # cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)

        # config_path = Path(__file__).parent.parent / "config" / "config.yaml"
        # with open(config_path, 'r') as f:
        #     config = yaml.safe_load(f)
        
        # bbox_styling = config['styling']['bbox'] 
        # font_scale = bbox_styling.get('font_scale', 0.6)
        # text_thickness = bbox_styling.get('text_thickness', 2)
        # thickness = bbox_styling.get('thickness', 2)
       
        

        # label = f"#{detection_id}"
        
        # (text_width, text_height), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, font_scale, text_thickness)
        # cv2.rectangle(frame, (x1, y1 - text_height - 10), (x1 + text_width, y1), color, thickness)
        # cv2.putText(frame, label, (x1, y1 - 5), cv2.FONT_HERSHEY_SIMPLEX, font_scale, text_thickness)
        
        # Save updated frame
        
        return True