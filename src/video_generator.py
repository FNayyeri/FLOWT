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
    
<<<<<<< HEAD
    def draw_options(self, frame, detection, options):
=======
    def draw_detection(self, frame, detection, options):
>>>>>>> 72b8e1e1f0a7e01f097607743d6e659c209801f9
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
        
<<<<<<< HEAD
        # Draw label, confidence, and track ID
=======
        # Draw label and confidence
>>>>>>> 72b8e1e1f0a7e01f097607743d6e659c209801f9
        if options.get('show_labels', True) or options.get('show_confidence', True):
            label_parts = []
            
            if options.get('show_labels', True):
                class_name = detection.get('corrected_class', detection.get('class', 'Unknown'))
<<<<<<< HEAD
                track_id = detection.get('track_id')
                if track_id is not None:
                    label_parts.append(f"{class_name} ID:{track_id}")
                else:
                    label_parts.append(class_name)
=======
                label_parts.append(class_name)
>>>>>>> 72b8e1e1f0a7e01f097607743d6e659c209801f9
            
            if options.get('show_confidence', True):
                confidence = detection.get('confidence', 0)
                label_parts.append(f"{confidence:.2f}")
            
            label = " ".join(label_parts)
            
            # Calculate text size
            font = cv2.FONT_HERSHEY_SIMPLEX
<<<<<<< HEAD
            font_scale = options.get('font_size', 0.6)
=======
            font_scale = 0.6
>>>>>>> 72b8e1e1f0a7e01f097607743d6e659c209801f9
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
    
<<<<<<< HEAD
    def generate_video(self, video_path, tracking_data_path, output_name, output_format, options, model_name=None):
=======
    def generate_video_from_tracking(self, video_path, tracking_data_path, output_name, output_format, options, model_name=None):
>>>>>>> 72b8e1e1f0a7e01f097607743d6e659c209801f9
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
            
<<<<<<< HEAD
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
=======
            # Draw tracked objects for current frame with track IDs
            if frame_count in detections_by_frame:
                for obj in detections_by_frame[frame_count]:
                    bbox = obj['bbox']
                    class_name = obj.get('class', 'Unknown')
                    confidence = obj.get('confidence', 0)
                    track_id = obj.get('track_id')
                    
                    # Parse styling options
                    thickness = options.get('bbox_thickness', None)
                    text_color_hex = options.get('text_color', '#FFFFFF')
                    text_color_rgb = tuple(int(text_color_hex[i:i+2], 16) for i in (1, 3, 5))
                    text_color = (text_color_rgb[2], text_color_rgb[1], text_color_rgb[0])  # Convert to BGR
                    
                    # Only draw if bounding boxes are enabled
                    if options.get('show_bboxes', True):
                        # Determine what to show in labels
                        show_any_label = options.get('show_labels', True) or options.get('show_confidence', True)
                        
                        # Prepare label components based on options
                        display_class = class_name if options.get('show_labels', True) else None
                        display_confidence = confidence if options.get('show_confidence', True) else None
                        display_track_id = track_id if options.get('show_labels', True) else None
                        
                        # Use custom color only when labels are disabled
                        custom_color = None
                        if not options.get('show_labels', True):
                            color_hex = options.get('bbox_color', '#FF0000')
                            color_rgb = tuple(int(color_hex[i:i+2], 16) for i in (1, 3, 5))
                            custom_color = (color_rgb[2], color_rgb[1], color_rgb[0])  # Convert to BGR
                            print(f"DEBUG: Using custom color {custom_color} from hex {color_hex}")
                        
                        frame = self.bbox_drawer.draw_bbox_with_options(
                            frame, bbox, display_class, display_confidence, 
                            display_track_id, show_any_label, thickness, text_color, custom_color
                        )
>>>>>>> 72b8e1e1f0a7e01f097607743d6e659c209801f9
            
            # Write frame
            out.write(frame)
            frame_count += 1
        
        # Release resources
        cap.release()
        out.release()
        
        return output_path
<<<<<<< HEAD
    
=======
    
    def generate_video(self, video_path, curated_data_path, output_name, output_format, options, model_name=None):
        """Generate video with corrected detections"""
        # Load curated data
        curated_data = self.load_curated_data(curated_data_path)
        
        # Group detections by frame
        detections_by_frame = {}
        for detection in curated_data:
            frame_num = detection.get('frame', 0)
            if frame_num not in detections_by_frame:
                detections_by_frame[frame_num] = []
            detections_by_frame[frame_num].append(detection)
        
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
            
            # Draw detections for current frame with labels and track IDs
            if frame_count in detections_by_frame:
                for detection in detections_by_frame[frame_count]:
                    if detection.get('is_true_positive', True):  # Only draw valid detections
                        bbox = detection['bbox']
                        class_name = detection.get('corrected_class', detection.get('class', 'Unknown'))
                        confidence = detection.get('confidence', 0)
                        track_id = detection.get('track_id')
                        
                        # Draw with labels and track ID for video generation
                        frame = self.bbox_drawer.draw_bbox(frame, bbox, class_name, confidence, track_id, show_label=True)
            
            # Write frame
            out.write(frame)
            frame_count += 1
        
        # Release resources
        cap.release()
        out.release()
        
        return output_path
    
    def create_comparison_video(self, original_video, corrected_video, output_name):
        """Create side-by-side comparison video"""
        cap1 = cv2.VideoCapture(str(original_video))
        cap2 = cv2.VideoCapture(str(corrected_video))
        
        # Get video properties
        fps = int(cap1.get(cv2.CAP_PROP_FPS))
        width = int(cap1.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap1.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        # Set up output video (double width for side-by-side)
        output_path = self.output_dir / f"{output_name}_comparison.mp4"
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(str(output_path), fourcc, fps, (width * 2, height))
        
        while True:
            ret1, frame1 = cap1.read()
            ret2, frame2 = cap2.read()
            
            if not ret1 or not ret2:
                break
            
            # Create side-by-side frame
            combined_frame = np.hstack((frame1, frame2))
            
            # Add labels
            cv2.putText(combined_frame, "Original", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
            cv2.putText(combined_frame, "Corrected", (width + 10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
            
            out.write(combined_frame)
        
        cap1.release()
        cap2.release()
        out.release()
        
        return output_path
>>>>>>> 72b8e1e1f0a7e01f097607743d6e659c209801f9
