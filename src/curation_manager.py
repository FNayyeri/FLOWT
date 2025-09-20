import json
from pathlib import Path
import pandas as pd

class CurationManager:
    def __init__(self, model_name=None):
        self.model_name = model_name
        base_dir = Path("data/curated")
        if model_name:
            self.curated_dir = base_dir / model_name
        else:
            self.curated_dir = base_dir
        self.curated_dir.mkdir(parents=True, exist_ok=True)
        self.current_detections = []
        self.curations = {}
    
    def load_detections(self, results_file):
        """Load detection results for curation"""
        with open(results_file, 'r') as f:
            self.current_detections = json.load(f)
        
        # Try to load existing curated data if available
        # First try video-specific curated file
        video_name = Path(results_file).stem.replace('_detections', '')
        curated_file = self.curated_dir / f"{video_name}_curated_detections.json"
        
        if curated_file.exists():
            with open(curated_file, 'r') as f:
                curated_data = json.load(f)
            # Merge curated data back into current detections
            for i, detection in enumerate(self.current_detections):
                if i < len(curated_data):
                    detection.update(curated_data[i])
        
        return self.current_detections
    
    def save_curation(self, detection_idx, curation_data, auto_export=True, video_name=None):
        """Save curation for a specific detection"""
        self.curations[detection_idx] = curation_data
        
        # Update the detection with curation data
        if detection_idx < len(self.current_detections):
            self.current_detections[detection_idx].update(curation_data)
        
        # Auto-export to file only if video_name is provided
        if auto_export and video_name:
            self.export_curated_data(video_name)
    
    def bulk_mark_true_positive(self, start_idx=None, end_idx=None):
        """Mark detections as true positive"""
        if start_idx is None:
            start_idx = 0
        if end_idx is None:
            end_idx = len(self.current_detections)
        
        for i in range(start_idx, min(end_idx, len(self.current_detections))):
            self.current_detections[i]['is_true_positive'] = True
            self.curations[i] = {'is_true_positive': True}
    
    def bulk_mark_false_positive(self, start_idx=None, end_idx=None):
        """Mark detections as false positive"""
        if start_idx is None:
            start_idx = 0
        if end_idx is None:
            end_idx = len(self.current_detections)
        
        for i in range(start_idx, min(end_idx, len(self.current_detections))):
            self.current_detections[i]['is_true_positive'] = False
            self.curations[i] = {'is_true_positive': False}
    
    def export_curated_data(self, video_name=None):
        """Export curated detections to file"""
        # Apply all curations
        for idx, curation in self.curations.items():
            if idx < len(self.current_detections):
                self.current_detections[idx].update(curation)
        
        # Save curated data with video name (required)
        if not video_name:
            raise ValueError("video_name is required for exporting curated data")
        
        curated_file = self.curated_dir / f"{video_name}_curated_detections.json"
        
        with open(curated_file, 'w') as f:
            json.dump(self.current_detections, f, indent=2)
        
        return curated_file
    
    def get_curation_stats(self):
        """Get statistics about current curation session"""
        total = len(self.current_detections)
        curated = len(self.curations)
        true_positives = sum(1 for c in self.curations.values() if c.get('is_true_positive', False))
        
        return {
            'total_detections': total,
            'curated_count': curated,
            'true_positives': true_positives,
            'false_positives': curated - true_positives,
            'progress': curated / total if total > 0 else 0
        }
    
    def validate_curations(self):
        """Validate curation data for consistency"""
        issues = []
        
        for idx, curation in self.curations.items():
            if curation.get('is_true_positive') and not curation.get('corrected_class'):
                issues.append(f"Detection {idx}: True positive without corrected class")
        
        return issues