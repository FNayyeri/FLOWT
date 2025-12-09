import cv2
import numpy as np
from pathlib import Path
import json

class ObjectTracker:
    def __init__(self):
        self.tracks = {}
        self.next_track_id = 0
        self.iou_threshold = 0.3
        self.template_threshold = 0.6
    
    def calculate_iou(self, box1, box2):
        """Calculate Intersection over Union of two bounding boxes"""
        x1, y1, x2, y2 = box1
        x3, y3, x4, y4 = box2
        
        xi1, yi1 = max(x1, x3), max(y1, y3)
        xi2, yi2 = min(x2, x4), min(y2, y4)
        
        if xi2 <= xi1 or yi2 <= yi1:
            return 0
        
        inter_area = (xi2 - xi1) * (yi2 - yi1)
        box1_area = (x2 - x1) * (y2 - y1)
        box2_area = (x4 - x3) * (y4 - y3)
        union_area = box1_area + box2_area - inter_area
        
        return inter_area / union_area if union_area > 0 else 0
    
    def extract_template(self, frame, bbox):
        """Extract template from bounding box"""
        x1, y1, x2, y2 = map(int, bbox)
        return frame[y1:y2, x1:x2]
    
    def match_template(self, frame, bbox, template):
        """Match template in bounding box region"""
        x1, y1, x2, y2 = map(int, bbox)
        roi = frame[y1:y2, x1:x2]
        
        if roi.shape[0] == 0 or roi.shape[1] == 0 or template.shape[0] == 0 or template.shape[1] == 0:
            return 0
        
        # Resize template to match ROI if needed
        if roi.shape != template.shape:
            template = cv2.resize(template, (roi.shape[1], roi.shape[0]))
        
        result = cv2.matchTemplate(roi, template, cv2.TM_CCOEFF_NORMED)
        return np.max(result)
    
    def track_objects(self, video_path, curated_detections):
        """Track objects across video frames"""
        cap = cv2.VideoCapture(str(video_path))
        
        # Group detections by frame
        detections_by_frame = {}
        for detection in curated_detections:
            if detection.get('is_true_positive', True):
                frame_num = detection['frame']
                if frame_num not in detections_by_frame:
                    detections_by_frame[frame_num] = []
                detections_by_frame[frame_num].append(detection)
        
        tracked_objects = []
        frame_count = 0
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            current_detections = detections_by_frame.get(frame_count, [])
            
            # Match detections to existing tracks
            for detection in current_detections:
                bbox = detection['bbox']
                class_name = detection.get('corrected_class', detection.get('class'))
                
                best_track_id = None
                best_score = 0
                
<<<<<<< HEAD
                # Find best matching track using IoU and template matching
                for track_id, track_info in self.tracks.items():
                    if track_info['class'] == class_name:
                        # Calculate IoU score
                        iou_score = self.calculate_iou(bbox, track_info['last_bbox'])
                        
                        # Template matching
                        template_score = self.match_template(frame, bbox, track_info['template'])
                        
                        # Use IoU OR template matching when not timelapse, only template for timelapse
                        if self.iou_threshold > 0:
                            # Non-timelapse: use IoU OR template matching (either can match)
                            iou_match = iou_score > self.iou_threshold
                            template_match = template_score > self.template_threshold
                            threshold_met = iou_match or template_match
                            combined_score = max(iou_score, template_score)
                        else:
                            # Timelapse: only template matching
                            combined_score = template_score
                            threshold_met = template_score > self.template_threshold
                        
                        if combined_score > best_score and threshold_met:
                            best_score = combined_score
=======
                # Find best matching track using only template matching
                for track_id, track_info in self.tracks.items():
                    if track_info['class'] == class_name:
                        # Template matching only
                        template_score = self.match_template(frame, bbox, track_info['template'])
                        
                        if template_score > best_score and template_score > self.template_threshold:
                            best_score = template_score
>>>>>>> 72b8e1e1f0a7e01f097607743d6e659c209801f9
                            best_track_id = track_id
                
                # Create new track or update existing
                if best_track_id is None:
                    # New track
                    track_id = self.next_track_id
                    self.next_track_id += 1
                    
                    template = self.extract_template(frame, bbox)
                    self.tracks[track_id] = {
                        'class': class_name,
                        'template': template,
                        'last_bbox': bbox,
                        'last_frame': frame_count,
                        'total_frames': 1
                    }
                else:
                    # Update existing track
                    self.tracks[best_track_id]['last_bbox'] = bbox
                    self.tracks[best_track_id]['last_frame'] = frame_count
                    self.tracks[best_track_id]['total_frames'] += 1
                
                # Add to tracked objects with final track_id
                final_track_id = best_track_id if best_track_id is not None else track_id
                tracked_objects.append({
                    'track_id': final_track_id,
                    'frame': frame_count,
                    'bbox': bbox,
                    'class': class_name,
                    'confidence': detection.get('confidence', 0)
                })
                
                # Update detection with track_id for video generation
                detection['track_id'] = final_track_id
            
            frame_count += 1
        
        cap.release()
        return tracked_objects
    
    def get_tracking_stats(self, tracked_objects):
        """Get tracking statistics"""
        tracks_by_class = {}
        unique_tracks = set()
        
        for obj in tracked_objects:
            class_name = obj['class']
            track_id = obj['track_id']
            
            if class_name not in tracks_by_class:
                tracks_by_class[class_name] = set()
            
            tracks_by_class[class_name].add(track_id)
            unique_tracks.add(track_id)
        
        stats = {
            'total_unique_objects': len(unique_tracks),
            'objects_by_class': {cls: len(tracks) for cls, tracks in tracks_by_class.items()},
            'total_detections': len(tracked_objects)
        }
        
        return stats