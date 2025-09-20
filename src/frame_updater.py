import cv2
import json
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