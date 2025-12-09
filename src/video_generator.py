import cv2
import json
import numpy as np
from pathlib import Path
from .bbox_drawer import BBoxDrawer

class VideoGenerator:
    def __init__(self):
        self.base_output_dir = Path("data/output")
        self.base_output_dir.mkdir(parents=True, exist_ok=True)
        self.bbox_drawer = BBoxDrawer()
    
    def load_curated_data(self, curated_file):
        """Load curated detection data"""
        with open(curated_file, 'r') as f:
            return json.load(f)
    
    def draw_options(self, frame, detection, options):
        """Draw detection on frame"""
        if not detection.get('is_true_positive', False):
            return frame
        
        bbox = detection['bbox']
        x1, y1, x2, y2 = map(int, bbox)
        
        # Parse color
        color_hex = options.get('bbox_color', '#FF0000')
        color_rgb = tuple(int(color_hex[i:i+2], 16) for i in (1, 3, 5))
        color_bgr = (color_rgb[2], color_rgb[1], color_rgb[0])  # Convert to BGR
        
        thickness = options.get('bbox_thickness', 2)
        
        # Draw bounding box
        if options.get('show_bboxes', True):
            cv2.rectangle(frame, (x1, y1), (x2, y2), color_bgr, thickness)
        
        # Draw label, confidence, and track ID
        if options.get('show_labels', True) or options.get('show_confidence', True):
            label_parts = []
            
            if options.get('show_labels', True):
                class_name = detection.get('corrected_class', detection.get('class', 'Unknown'))
                track_id = detection.get('track_id')
                if track_id is not None:
                    label_parts.append(f"{class_name} ID:{track_id}")
                else:
                    label_parts.append(class_name)
            
            if options.get('show_confidence', True):
                confidence = detection.get('confidence', 0)
                label_parts.append(f"{confidence:.2f}")
            
            label = " ".join(label_parts)
            
            # Calculate text size
            font = cv2.FONT_HERSHEY_SIMPLEX
            font_scale = options.get('font_size', 0.6)
            text_thickness = 1
            (text_width, text_height), _ = cv2.getTextSize(label, font, font_scale, text_thickness)
            
            # Draw text background
            cv2.rectangle(frame, (x1, y1 - text_height - 10), (x1 + text_width, y1), color_bgr, -1)
            
            # Draw text
            text_color_hex = options.get('text_color', '#FFFFFF')
            text_color_rgb = tuple(int(text_color_hex[i:i+2], 16) for i in (1, 3, 5))
            text_color_bgr = (text_color_rgb[2], text_color_rgb[1], text_color_rgb[0])
            
            cv2.putText(frame, label, (x1, y1 - 5), font, font_scale, text_color_bgr, text_thickness)
        
        return frame
    
    def generate_video(self, video_path, tracking_data_path, output_name, output_format, options, model_name=None):
        """Generate video from tracking data with track IDs"""
        import json
        
        # Load tracking data
        with open(tracking_data_path, 'r') as f:
            tracking_data = json.load(f)
        
        tracked_objects = tracking_data['tracked_objects']
        
        # Group detections by frame
        detections_by_frame = {}
        for obj in tracked_objects:
            frame_num = obj.get('frame', 0)
            if frame_num not in detections_by_frame:
                detections_by_frame[frame_num] = []
            detections_by_frame[frame_num].append(obj)
        
        # Open input video
        cap = cv2.VideoCapture(str(video_path))
        
        # Get video properties
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        # Set up model-specific output directory
        if model_name:
            output_dir = self.base_output_dir / model_name
            output_dir.mkdir(parents=True, exist_ok=True)
        else:
            output_dir = self.base_output_dir
        
        # Set up output video
        output_path = output_dir / f"{output_name}.{output_format}"
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(str(output_path), fourcc, fps, (width, height))
        
        frame_count = 0
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            # Draw tracked objects for current frame using draw_options
            if frame_count in detections_by_frame:
                for obj in detections_by_frame[frame_count]:
                    # Convert tracking object to detection format
                    detection = {
                        'bbox': obj['bbox'],
                        'class': obj.get('class', 'Unknown'),
                        'corrected_class': obj.get('class', 'Unknown'),
                        'confidence': obj.get('confidence', 0),
                        'is_true_positive': True,
                        'track_id': obj.get('track_id')
                    }
                    
                    frame = self.draw_options(frame, detection, options)
            
            # Write frame
            out.write(frame)
            frame_count += 1
        
        # Release resources
        cap.release()
        out.release()
        
        return output_path
    