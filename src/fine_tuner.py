import json
import yaml
import shutil
from pathlib import Path
from ultralytics import YOLO
import cv2
import numpy as np
from sklearn.model_selection import train_test_split

class FineTuner:
    def __init__(self):
        self.training_dir = Path("data/training")
        self.models_dir = Path("models/fine_tuned")
        self.models_dir.mkdir(parents=True, exist_ok=True)
        
    def prepare_dataset(self, curated_files, train_split=0.8, val_split=0.15, augmentation_config=None):
        """Convert curated data to YOLO training format"""
        # Create training directory structure
        dataset_dir = self.training_dir
        dataset_dir.mkdir(parents=True, exist_ok=True)
        
        for split in ['train', 'val', 'test']:
            (dataset_dir / split / 'images').mkdir(parents=True, exist_ok=True)
            (dataset_dir / split / 'labels').mkdir(parents=True, exist_ok=True)
        
        # Load all curated data
        all_detections = []
        for curated_file in curated_files:
            with open(f"data/curated/{curated_file}.json", 'r') as f:
                detections = json.load(f)
                # Filter only true positives
                true_positives = [d for d in detections if d.get('is_true_positive', False)]
                all_detections.extend(true_positives)
        
        # Group detections by video/frame
        frames_data = {}
        for detection in all_detections:
            frame_key = f"{detection.get('video', 'unknown')}_{detection.get('frame', 0)}"
            if frame_key not in frames_data:
                frames_data[frame_key] = []
            frames_data[frame_key].append(detection)
        
        # Split data
        frame_keys = list(frames_data.keys())
        train_keys, temp_keys = train_test_split(frame_keys, train_size=train_split, random_state=42)
        val_keys, test_keys = train_test_split(temp_keys, train_size=val_split/(1-train_split), random_state=42)
        
        splits = {
            'train': train_keys,
            'val': val_keys,
            'test': test_keys
        }
        
        # Create class mapping
        all_classes = set()
        for detections in frames_data.values():
            for detection in detections:
                class_name = detection.get('corrected_class', detection.get('class', 'unknown'))
                all_classes.add(class_name)
        
        class_to_id = {cls: idx for idx, cls in enumerate(sorted(all_classes))}
        
        # Process each split
        dataset_info = {}
        for split_name, split_keys in splits.items():
            count = 0
            for frame_key in split_keys:
                detections = frames_data[frame_key]
                
                # Create dummy image (in real implementation, extract from video)
                img_name = f"{frame_key}.jpg"
                img_path = dataset_dir / split_name / 'images' / img_name
                
                # Create dummy 640x640 image (replace with actual frame extraction)
                dummy_img = np.zeros((640, 640, 3), dtype=np.uint8)
                cv2.imwrite(str(img_path), dummy_img)
                
                # Create YOLO label file
                label_path = dataset_dir / split_name / 'labels' / f"{frame_key}.txt"
                with open(label_path, 'w') as f:
                    for detection in detections:
                        class_name = detection.get('corrected_class', detection.get('class', 'unknown'))
                        class_id = class_to_id[class_name]
                        
                        # Convert bbox to YOLO format (normalized center x, y, width, height)
                        bbox = detection['bbox']
                        x1, y1, x2, y2 = bbox
                        
                        # Normalize coordinates (assuming 640x640 image)
                        img_w, img_h = 640, 640
                        center_x = ((x1 + x2) / 2) / img_w
                        center_y = ((y1 + y2) / 2) / img_h
                        width = (x2 - x1) / img_w
                        height = (y2 - y1) / img_h
                        
                        f.write(f"{class_id} {center_x} {center_y} {width} {height}\n")
                
                count += 1
            
            dataset_info[f'{split_name}_count'] = count
        
        # Create dataset.yaml
        dataset_yaml = {
            'path': str(dataset_dir.absolute()),
            'train': 'train/images',
            'val': 'val/images',
            'test': 'test/images',
            'nc': len(class_to_id),
            'names': list(class_to_id.keys())
        }
        
        with open(dataset_dir / 'dataset.yaml', 'w') as f:
            yaml.dump(dataset_yaml, f)
        
        return dataset_info
    
    def start_training(self, config, progress_callback=None):
        """Start YOLO model fine-tuning"""
        # Load base model
        model = YOLO(config['base_model'])
        
        # Training arguments
        train_args = {
            'data': str(self.training_dir / 'dataset.yaml'),
            'epochs': config['epochs'],
            'batch': config['batch_size'],
            'lr0': config['learning_rate'],
            'imgsz': config['image_size'],
            'patience': config['patience'],
            'save_period': config['save_period'],
            'optimizer': config['optimizer'],
            'weight_decay': config['weight_decay'],
            'momentum': config['momentum'],
            'warmup_epochs': config['warmup_epochs'],
            'project': str(self.models_dir),
            'name': 'fine_tuned_model',
            'exist_ok': True
        }
        
        # Start training
        results = model.train(**train_args)
        
        # Copy best model to models directory
        best_model_path = self.models_dir / 'fine_tuned_model' / 'weights' / 'best.pt'
        final_model_path = self.models_dir / f"marine_litter_model_{config['epochs']}epochs.pt"
        
        if best_model_path.exists():
            shutil.copy(best_model_path, final_model_path)
        
        return final_model_path
    
    def get_training_results(self):
        """Get training results and metrics"""
        results_file = self.models_dir / 'fine_tuned_model' / 'results.csv'
        if results_file.exists():
            import pandas as pd
            df = pd.read_csv(results_file)
            return df.to_dict('records')
        return None
    
    def validate_model(self, model_path, test_data_path):
        """Validate fine-tuned model on test data"""
        model = YOLO(model_path)
        
        # Run validation
        results = model.val(data=str(self.training_dir / 'dataset.yaml'))
        
        return {
            'mAP50': results.box.map50,
            'mAP50-95': results.box.map,
            'precision': results.box.mp,
            'recall': results.box.mr
        }
    
    def export_model(self, model_path, export_format='onnx'):
        """Export model to different formats"""
        model = YOLO(model_path)
        
        export_path = model.export(format=export_format)
        return export_path