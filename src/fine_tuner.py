from pathlib import Path
import yaml
import shutil
import random
import cv2
import json
import hashlib
import streamlit as st
import torch
import pandas as pd
import time
from io import StringIO
import contextlib
from ultralytics import YOLO
import sys
from src.genai_service import GenAIService
import pandas as pd

def get_dataset_config():
    """Load dataset split configuration from config.yaml"""
    config_path = Path(__file__).parent.parent / "config" / "config.yaml"
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    ft_config = config.get('fine_tuning', {})
    return {
        'train_ratio': ft_config.get('train_ratio', 0.8),
        'include_test': ft_config.get('include_test', True)
    }

def update_dataset_config(train_ratio, include_test):
    """Update dataset split configuration in config.yaml"""
    config_path = Path(__file__).parent.parent / "config" / "config.yaml"
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    if 'fine_tuning' not in config:
        config['fine_tuning'] = {}
    
    config['fine_tuning']['train_ratio'] = train_ratio
    config['fine_tuning']['include_test'] = include_test
    
    with open(config_path, 'w') as f:
        yaml.dump(config, f, default_flow_style=False)
        
def create_curated_dataset(curated_files, videos_dir, class_names, progress_callback=None, status_callback=None):
    """Create curated dataset from curated detection files"""
    # Create curated dataset directories
    curated_dataset_dir = Path("data/curated_dataset")
    images_dir = curated_dataset_dir / "images"
    labels_dir = curated_dataset_dir / "labels"
    
    # Create directories if they don't exist
    images_dir.mkdir(parents=True, exist_ok=True)
    labels_dir.mkdir(parents=True, exist_ok=True)
    
    # Get existing image count to continue numbering
    existing_images = list(images_dir.glob("*.jpg"))
    file_counter = len(existing_images) + 1
    
    # Track existing image hashes to avoid duplicates
    existing_hashes = set()
    for img_path in existing_images:
        try:
            with open(img_path, 'rb') as f:
                img_hash = hashlib.md5(f.read()).hexdigest()
            existing_hashes.add(img_hash)
        except:
            pass
    
    # Process curated files
    processed_count = 0
    background_count = 0
    skipped_duplicates = 0
    total_true_positives = 0
    
    for i, curated_file in enumerate(curated_files):
        video_name = curated_file.stem.replace('_curated_detections', '')
        video_path = videos_dir / f"{video_name}.mp4"
        
        if not video_path.exists():
            continue
        
        if status_callback:
            status_callback(f"Processing {video_name}...")
        
        # Load curated data
        with open(curated_file, 'r') as f:
            curated_data = json.load(f)
        
        # Group detections by frame and separate true/false positives
        frames_with_true_positives = {}
        frames_with_false_positives = set()
        
        for detection in curated_data:
            frame_num = detection['frame']
            if detection.get('is_true_positive', True):
                total_true_positives += 1
                if frame_num not in frames_with_true_positives:
                    frames_with_true_positives[frame_num] = []
                frames_with_true_positives[frame_num].append(detection)
            else:
                frames_with_false_positives.add(frame_num)
        
        # Remove frames with false positives that also have true positives
        frames_with_only_false_positives = frames_with_false_positives - set(frames_with_true_positives.keys())
        
        # Open video
        cap = cv2.VideoCapture(str(video_path))
        
        # Process frames with true positive detections
        for frame_num, detections in frames_with_true_positives.items():
            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_num)
            ret, frame = cap.read()
            
            if ret:
                # Check for duplicate using image hash
                _, frame_encoded = cv2.imencode('.jpg', frame)
                frame_hash = hashlib.md5(frame_encoded.tobytes()).hexdigest()
                
                if frame_hash in existing_hashes:
                    skipped_duplicates += 1
                    continue
                
                # Unique naming convention
                unique_name = f"img_{file_counter:06d}"
                image_path = images_dir / f"{unique_name}.jpg"
                cv2.imwrite(str(image_path), frame)
                
                # Add hash to existing set
                existing_hashes.add(frame_hash)
                
                # Create YOLO format annotations
                h, w = frame.shape[:2]
                label_path = labels_dir / f"{unique_name}.txt"
                
                with open(label_path, 'w') as f:
                    for detection in detections:
                        bbox = detection['bbox']
                        class_name = detection.get('corrected_class', detection.get('class', 'Packaging'))
                        
                        # Map class name to index
                        try:
                            class_id = class_names.index(class_name)
                        except ValueError:
                            class_id = 0  # Default to first class
                        
                        # Convert to YOLO format (normalized)
                        x_center = (bbox[0] + bbox[2] / 2) / w
                        y_center = (bbox[1] + bbox[3] / 2) / h
                        norm_width = bbox[2] / w
                        norm_height = bbox[3] / h
                        
                        # Ensure values are within valid range [0, 1]
                        x_center = max(0, min(1, x_center))
                        y_center = max(0, min(1, y_center))
                        norm_width = max(0, min(1, norm_width))
                        norm_height = max(0, min(1, norm_height))
                        
                        f.write(f"{class_id} {x_center:.6f} {y_center:.6f} {norm_width:.6f} {norm_height:.6f}\n")
                
                processed_count += 1
                file_counter += 1
        
        # Process background frames (frames with only false positives)
        for frame_num in frames_with_only_false_positives:
            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_num)
            ret, frame = cap.read()
            
            if ret:
                # Check for duplicate using image hash
                _, frame_encoded = cv2.imencode('.jpg', frame)
                frame_hash = hashlib.md5(frame_encoded.tobytes()).hexdigest()
                
                if frame_hash in existing_hashes:
                    skipped_duplicates += 1
                    continue
                
                # Unique naming convention
                unique_name = f"img_{file_counter:06d}"
                image_path = images_dir / f"{unique_name}.jpg"
                cv2.imwrite(str(image_path), frame)
                
                # Add hash to existing set
                existing_hashes.add(frame_hash)
                
                # Create empty label file for background
                label_path = labels_dir / f"{unique_name}.txt"
                with open(label_path, 'w') as f:
                    pass  # Empty file for background
                
                background_count += 1
                file_counter += 1
        
        cap.release()
        
        if progress_callback:
            progress_callback((i + 1) / len(curated_files))
    
    total_images = len(list(images_dir.glob("*.jpg")))
    
    return {
        'processed_count': processed_count,
        'background_count': background_count,
        'skipped_duplicates': skipped_duplicates,
        'total_images': total_images,
        'total_true_positives': total_true_positives
    }

def get_system_info():
    """Get system information for training"""
    try:
        
        gpu_available = torch.cuda.is_available()
        gpu_count = torch.cuda.device_count() if gpu_available else 0
        gpu_name = torch.cuda.get_device_name(0) if gpu_available else "N/A"
    except:
        gpu_available = False
        gpu_count = 0
        gpu_name = "N/A"
    
    return {
        'gpu_available': gpu_available,
        'gpu_count': gpu_count,
        'gpu_name': gpu_name
    }

def get_training_config():
    """Load training configuration from config.yaml"""
    config_path = Path(__file__).parent.parent / "config" / "config.yaml"
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    ft_config = config.get('fine_tuning', {})
    return {
        'frozen_layers': ft_config.get('frozen_layers', 9),
        'epochs': ft_config.get('epochs', 50),
        'batch_size': ft_config.get('batch_size', 16),
        'conf_threshold': ft_config.get('conf_threshold', 0.25),
        'augment': ft_config.get('augment', True),
        'device': ft_config.get('device', 'auto')
    }

def update_training_config(frozen_layers, epochs, batch_size, conf_threshold, augment, device):
    """Update training configuration in config.yaml"""
    config_path = Path(__file__).parent.parent / "config" / "config.yaml"
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    if 'fine_tuning' not in config:
        config['fine_tuning'] = {}
    
    config['fine_tuning']['frozen_layers'] = frozen_layers
    config['fine_tuning']['epochs'] = epochs
    config['fine_tuning']['batch_size'] = batch_size
    config['fine_tuning']['conf_threshold'] = conf_threshold
    config['fine_tuning']['augment'] = augment
    config['fine_tuning']['device'] = device
    
    with open(config_path, 'w') as f:
        yaml.dump(config, f, default_flow_style=False)

def calculate_ratios(train_ratio, include_test):
    """Calculate val and test ratios based on train ratio and test checkbox"""
    if include_test:
        remaining = 1 - train_ratio
        val_ratio = remaining / 2
        test_ratio = remaining / 2
    else:
        val_ratio = 1 - train_ratio
        test_ratio = 0
    
    return train_ratio, val_ratio, test_ratio

def prepare_ft_dataset(curated_dataset_dir, ft_dataset_dir, class_names, train_ratio, include_test):
    """Delete existing ft_dataset and create new one with specified configuration"""
    # Calculate actual ratios
    train_ratio, val_ratio, test_ratio = calculate_ratios(train_ratio, include_test)
    
    # Delete existing ft_dataset
    if ft_dataset_dir.exists():
        shutil.rmtree(ft_dataset_dir)
    
    # Create ft_dataset directories
    splits = ['train', 'val']
    if include_test:
        splits.append('test')
    
    for split in splits:
        (ft_dataset_dir / split / "images").mkdir(parents=True, exist_ok=True)
        (ft_dataset_dir / split / "labels").mkdir(parents=True, exist_ok=True)
    
    # Get all image files from curated dataset
    image_files = list((curated_dataset_dir / "images").glob("*.jpg"))
    random.shuffle(image_files)
    
    # Calculate split indices
    total_images = len(image_files)
    train_end = int(total_images * train_ratio)
    
    # Split files
    train_files = image_files[:train_end]
    remaining_files = image_files[train_end:]
    
    if include_test:
        val_end = len(remaining_files) // 2
        val_files = remaining_files[:val_end]
        test_files = remaining_files[val_end:]
    else:
        val_files = remaining_files
        test_files = []
    
    # Copy files to respective directories
    file_splits = [('train', train_files), ('val', val_files)]
    if include_test:
        file_splits.append(('test', test_files))
    
    for split_name, files in file_splits:
        for img_file in files:
            # Copy image
            dst_img = ft_dataset_dir / split_name / "images" / img_file.name
            shutil.copy2(img_file, dst_img)
            
            # Copy corresponding label
            label_file = curated_dataset_dir / "labels" / img_file.with_suffix('.txt').name
            if label_file.exists():
                dst_label = ft_dataset_dir / split_name / "labels" / label_file.name
                shutil.copy2(label_file, dst_label)
    
    # Create dataset.yaml for ft_dataset
    dataset_yaml = ft_dataset_dir / "dataset.yaml"
    yaml_content = {
        'path': str(ft_dataset_dir.absolute()),
        'train': 'train/images',
        'val': 'val/images',
        'nc': len(class_names),
        'names': class_names
    }
    
    if include_test:
        yaml_content['test'] = 'test/images'
    
    with open(dataset_yaml, 'w') as f:
        yaml.dump(yaml_content, f, default_flow_style=False)
    
    return len(train_files), len(val_files), len(test_files)

def run_fine_tuning(selected_model_dir, selected_baseline, current_iteration, class_names, 
                   epochs, batch_size, frozen_layers, conf_threshold, augment, device, system_info):
    """Execute YOLO fine-tuning with given parameters"""

    
    # Setup paths
    models_dir = Path("models")
    models_ft_dir = Path("models_ft")
    training_logs_dir = Path("data/training_logs")
    
    # Create directories
    models_ft_dir.mkdir(exist_ok=True)
    training_logs_dir.mkdir(exist_ok=True)
    
    # Generate versioned model name
    timestamp = pd.Timestamp.now().strftime("%Y%m%d_%H%M%S")
    ft_model_name = f"{selected_baseline}_{current_iteration}_{timestamp}.pt"
    ft_model_path = models_ft_dir / ft_model_name
    
    dataset_yaml = Path("data/ft_dataset/dataset.yaml")
    
    # Load baseline model
    if selected_baseline.startswith("ft/"):
        base_model_path = models_ft_dir / f"{selected_baseline[3:]}.pt"
    else:
        base_model_path = models_dir / f"{selected_baseline}.pt"
    
    start_time = time.time()
    
    # Load model first to get summary
    model = YOLO(str(base_model_path))
    
    # Set device for training
    if device == "gpu" and system_info['gpu_available']:
        train_device = 0
    elif device == "cpu":
        train_device = "cpu"
    else:  # device == "auto"
        train_device = 0 if system_info['gpu_available'] else "cpu"
    
    # Capture training output
    training_output = StringIO()
    model_summary = ""
    class_distribution = ""
    epoch_logs = []
    
    # Get model info before training
    try:
        with contextlib.redirect_stdout(training_output):
            model.info()
        model_summary = training_output.getvalue()
        training_output = StringIO()  # Reset for training
    except Exception:
        pass
    
    # Custom callback to capture epoch information
    def on_train_epoch_end(trainer):
        if hasattr(trainer, 'epoch') and hasattr(trainer, 'loss_items'):
            epoch_info = {
                'epoch': trainer.epoch,
                'gpu_mem': getattr(trainer, 'gpu_mem', 'N/A'),
                'box_loss': trainer.loss_items.get('train/box_loss', 0) if hasattr(trainer.loss_items, 'get') else 0,
                'cls_loss': trainer.loss_items.get('train/cls_loss', 0) if hasattr(trainer.loss_items, 'get') else 0,
                'dfl_loss': trainer.loss_items.get('train/dfl_loss', 0) if hasattr(trainer.loss_items, 'get') else 0
            }
            epoch_logs.append(epoch_info)
    
    # Train model with output capture
    with contextlib.redirect_stdout(training_output):
        results = model.train(
            data=str(dataset_yaml), 
            epochs=epochs, 
            batch=batch_size, 
            freeze=frozen_layers,
            conf=conf_threshold,
            augment=augment,
            device=train_device,
            save_period=1,
            plots=True,
            val=True
        )
    
    model.save(str(ft_model_path))
    
    # Get training log content
    training_log_content = training_output.getvalue()
    
    # Parse class distribution from training output
    lines = training_log_content.split('\n')
    for i, line in enumerate(lines):
        if 'all' in line and any(cls in line for cls in class_names):
            # Capture class distribution table
            class_dist_lines = []
            for j in range(max(0, i-2), min(len(lines), i+len(class_names)+3)):
                if lines[j].strip():
                    class_dist_lines.append(lines[j])
            class_distribution = '\n'.join(class_dist_lines)
            break
    
    # Extract metrics
    training_metrics = {
        "final_metrics": {},
        "per_class_metrics": {},
        "training_curves": {}
    }
    
    if hasattr(results, 'results_dict'):
        metrics_dict = results.results_dict
        training_metrics["final_metrics"] = {
            "mAP50": metrics_dict.get('metrics/mAP50(B)', 0),
            "mAP50-95": metrics_dict.get('metrics/mAP50-95(B)', 0),
            "precision": metrics_dict.get('metrics/precision(B)', 0),
            "recall": metrics_dict.get('metrics/recall(B)', 0),
            "val_loss": metrics_dict.get('val/box_loss', 0),
            "val_cls_loss": metrics_dict.get('val/cls_loss', 0)
        }
    
    # Per-class metrics
    try:
        if hasattr(results, 'maps'):
            class_maps = results.maps
            if len(class_maps) == len(class_names):
                training_metrics["per_class_metrics"] = {
                    class_names[i]: {
                        "mAP50": float(class_maps[i]) if i < len(class_maps) else 0.0
                    } for i in range(len(class_names))
                }
    except Exception:
        pass
    
    # Copy training plots and analysis filesysis files
    plots_dest = None
    analysis_dest = None
    plots_dir = Path("runs/detect/train")
    if plots_dir.exists():
        train_dirs = [d for d in plots_dir.parent.iterdir() if d.name.startswith('train')]
        if train_dirs:
            latest_train_dir = max(train_dirs, key=lambda x: x.stat().st_mtime)
            
            # Create analysis directory
            analysis_dest = Path("data/analysis/model_ft") / ft_model_name.replace('.pt', '')
            analysis_dest.mkdir(parents=True, exist_ok=True)
            
            # Copy analysis files
            analysis_files = ['args.yaml', 'results.csv']
            for analysis_file in analysis_files:
                src_file = latest_train_dir / analysis_file
                if src_file.exists():
                    shutil.copy2(src_file, analysis_dest / analysis_file)
            
            # Create comprehensive training analysis JSON
            analysis_json_path = analysis_dest / "training_analysis.json"
            
            # Parse model summary for structured data
            model_info = {}
            if model_summary:
                for line in model_summary.split('\n'):
                    if 'Model summary' in line:
                        parts = line.split(': ')
                        if len(parts) > 1:
                            summary_parts = parts[1].split(', ')
                            for part in summary_parts:
                                if 'layers' in part:
                                    model_info['layers'] = int(part.split()[0])
                                elif 'parameters' in part:
                                    model_info['parameters'] = int(part.split()[0].replace(',', ''))
                                elif 'GFLOPs' in part:
                                    model_info['gflops'] = float(part.split()[0])
            
            # Parse class distribution
            class_dist_data = {}
            if class_distribution:
                lines = class_distribution.split('\n')
                for line in lines:
                    parts = line.strip().split()
                    if len(parts) >= 2 and parts[0] in class_names:
                        class_dist_data[parts[0]] = {
                            'total': int(parts[1]) if parts[1].isdigit() else 0,
                            'train': int(parts[2]) if len(parts) > 2 and parts[2].isdigit() else 0
                        }
            
            analysis_data = {
                "metadata": {
                    "model_name": ft_model_name,
                    "timestamp": timestamp,
                    "base_model": selected_model_dir,
                    "baseline": selected_baseline,
                    "iteration": current_iteration,
                    "training_duration_seconds": time.time() - start_time
                },
                "model_info": model_info,
                "training_parameters": {
                    "epochs": epochs,
                    "batch_size": batch_size,
                    "frozen_layers": frozen_layers,
                    "confidence_threshold": conf_threshold,
                    "augmentation": augment,
                    "device": str(train_device)
                },
                "dataset_info": {
                    "classes": class_names,
                    "class_distribution": class_dist_data
                },
                "system_info": system_info,
                "training_progress": epoch_logs,
                "final_metrics": training_metrics["final_metrics"],
                "per_class_metrics": training_metrics["per_class_metrics"],
                "raw_output": training_log_content
            }
            
            with open(analysis_json_path, 'w') as f:
                
                json.dump(analysis_data, f, indent=2, default=str)
    
    # Clean up runs folder to save disk space
    runs_dir = Path("runs")
    if runs_dir.exists():
        shutil.rmtree(runs_dir)
    
    return training_metrics, ft_model_name

def display_model_versions(models_ft_dir, models_dir, training_history, training_log_path):
    """Display existing fine-tuned models with delete functionality"""
    
    if models_ft_dir.exists():
        ft_models = list(models_ft_dir.glob("*.pt"))
        if ft_models:
            # Sort by creation time (newest first)
            ft_models.sort(key=lambda x: x.stat().st_mtime, reverse=True)
            
            for model in ft_models:
                # Find corresponding training entry
                model_entry = next((h for h in training_history if h['model_name'] == model.name), None)
                
                col1, col2, col3, col4, col5 = st.columns([2, 1, 1, 1, 1])
                with col1:
                    st.write(f"🤖 {model.name}")
                with col2:
                    if model_entry:
                        dataset_info = model_entry.get('dataset_info', {})
                        st.write(f"Images: {dataset_info.get('total_images', 'N/A')}")
                    else:
                        st.write("No info")
                with col3:
                    st.write(f"{model.stat().st_size / (1024*1024):.1f} MB")
                with col4:
                    if model_entry:
                        st.write(f"v{model_entry['iteration']}")
                with col5:
                    if st.button("🗑️ Delete", key=f"delete_{model.name}", help="Delete this model version", type="tertiary"):
                        # Delete model files from both locations
                        model.unlink()  # Delete from models_ft
                        
                        # Delete from models directory if exists
                        models_copy = models_dir / model.name
                        if models_copy.exists():
                            models_copy.unlink()
                        
                        # Remove from training history
                        if model_entry:
                            updated_history = [h for h in training_history if h['model_name'] != model.name]
                            with open(training_log_path, 'w') as f:
                                json.dump(updated_history, f, indent=2)
                        
                        st.success(f"Deleted {model.name} from both directories")
                        st.rerun()
        else:
            st.info("No fine-tuned models yet.")
    else:
        st.info("No fine-tuned models directory found.")



def display_ai_analysis():
    """Display AI analysis section with model selection and analysis generation"""
    st.header("🤖 AI Analysis")
    
    analysis_dir = Path("data/analysis/model_ft")
    if not analysis_dir.exists():
        st.info("No analysis data found. Complete a fine-tuning session first.")
        return
    
    analysis_models = [d.name for d in analysis_dir.iterdir() if d.is_dir()]
    if not analysis_models:
        st.info("No fine-tuned models found for analysis. Complete a fine-tuning session first.")
        return
    
    col1, col2 = st.columns(2)
    with col1:
        selected_analysis_model = st.selectbox(
            "Select Model for Analysis",
            analysis_models,
            help="Choose a fine-tuned model to analyze"
        )
    
    with col2:
        analysis_type = st.selectbox(
            "Analysis Type",
            ["Training Performance Analysis", "Parameter Optimization", "Custom Query"]
        )
    
    if st.button("Generate AI Analysis", type="secondary"):
        with st.spinner("Analyzing training data with AI..."):
            try:
                
                from src.genai_service import GenAIService
                
                ai_service = GenAIService()
                
                # Load analysis data for selected model
                model_analysis_dir = analysis_dir / selected_analysis_model
                analysis_data = {}
                
                # Load training_analysis.json
                json_file = model_analysis_dir / "training_analysis.json"
                if json_file.exists():
                    with open(json_file, 'r') as f:
                        analysis_data = json.load(f)
                
                # Load additional files if they exist
                args_file = model_analysis_dir / "args.yaml"
                if args_file.exists():
                    with open(args_file, 'r') as f:
                        analysis_data['training_args'] = yaml.safe_load(f)
                
                results_file = model_analysis_dir / "results.csv"
                if results_file.exists():
                    df = pd.read_csv(results_file)
                    analysis_data['training_results'] = df.to_dict('records')
                
                project_context = """Project: Flowt Pipeline - Floating Litter Observation & Waste Tracking
Purpose: YOLO fine-tuning for automated detection of plastic and floating debris in waterways to protect aquatic ecosystems.
Litter Classes (26 categories): Packaging, Other_packaging, S_bubblewrap, S_label, S_squeeze, S_straw, PS_string, P_cardboard, P_foodcontainer, PH_cup, H_packaging, H_beveragebottle, H_otherbottle, H_plate/bowl, H_utensil, DH_lid, D_polystyrene, M_beveragecan, M_foodcan/tin, M_aerosol, R_ball/balloon, G_beveragebottle, F_facemask, T_wood/timber, Other.
Materials: Soft/Hard Plastic, Cardboard, Paper, Aluminium, Polystyrene, Metal, Rubber, Glass, Fabric, Timber - each with different detection challenges."""
                
                if analysis_type == "Training Performance Analysis":
                    prompt = f"""{project_context}
Analyze this YOLO fine-tuning result for marine litter detection:
Model: {selected_analysis_model}
Training Data: {json.dumps(analysis_data, indent=2)}
Provide analysis on:
1. Training performance trends across the 26 litter classes
2. Model convergence and loss patterns
3. Recommendations for improving detection of specific litter categories
4. Performance insights based on the training metrics
Focus on practical actionable insights for environmental monitoring."""
                
                elif analysis_type == "Parameter Optimization":
                    prompt = f"""{project_context}
Analyze these YOLO fine-tuning parameters for marine litter detection:
Model: {selected_analysis_model}
Training Data: {json.dumps(analysis_data, indent=2)}
Provide specific recommendations for:
1. Optimal epochs, batch size, frozen layers for 26 litter classes
2. Learning rate adjustments for different material types
3. Data augmentation strategies for floating debris
4. Training schedule improvements for marine environment
Be specific with numerical recommendations considering the environmental application."""
                
                else:  # Custom Query
                    custom_query = st.text_area(
                        "Enter your custom analysis question:",
                        placeholder="e.g., Why is my model not improving? What does the loss pattern indicate?"
                    )
                    if custom_query:
                        prompt = f"""{project_context}
Model: {selected_analysis_model}
Training Data: {json.dumps(analysis_data, indent=2)}
User Question: {custom_query}
Provide a detailed analysis based on the training data and marine litter detection context."""
                    else:
                        st.warning("Please enter a custom query.")
                        prompt = None
                
                if prompt:
                    available_providers = ai_service.get_available_providers()
                    provider = available_providers[0] if available_providers else "google"
                    analysis_result = ai_service.generate_analysis(prompt, provider)
                    
                    if analysis_result:
                        st.subheader(f"AI Analysis Results for {selected_analysis_model}")
                        st.markdown(analysis_result)
                    else:
                        st.error("AI analysis failed. Please check your API configuration.")
            
            except ImportError:
                st.warning("AI analysis not available. Please install required dependencies (google-generativeai, openai).")
            except Exception as e:
                st.error(f"AI analysis error: {str(e)}")
#                             provider = available_providers[0] if available_providers else "google"
#                             analysis_result = ai_service.generate_analysis(prompt, provider)
                            
#                             if analysis_result:
#                                 st.subheader("AI Analysis Results")
#                                 st.markdown(analysis_result)
#                             else:
#                                 st.error("AI analysis failed. Please check your API configuration.")
                    
#                     except Exception as e:
#                         st.error(f"AI analysis error: {str(e)}")
            
#             # Training Log Chat
#             st.subheader("Training Log Chat")
            
#             # Select training session for chat
#             if training_history:
#                 session_options = [f"v{h['iteration']} - {h['timestamp']} ({h.get('dataset_info', {}).get('total_images', 'N/A')} images)" 
#                                  for h in training_history]
#                 selected_session_idx = st.selectbox(
#                     "Select Training Session",
#                     range(len(session_options)),
#                     format_func=lambda x: session_options[x]
#                 )
                
#                 selected_training = training_history[selected_session_idx]
                
#                 # Chat interface
#                 user_question = st.text_input(
#                     "Ask about this training session:",
#                     placeholder="e.g., Why did the loss not decrease? What does mAP50 of 0.003 mean?"
#                 )
                
#                 if st.button("Ask AI", type="secondary") and user_question:
#                     with st.spinner("Getting AI response..."):
#                         try:
#                             # Prepare training session data
#                             session_data = {
#                                 "training_session": selected_training,
#                                 "training_output": selected_training.get('training_output', 'No training output available'),
#                                 "log_file": selected_training.get('log_file', 'No training output available')
#                             }
                            
#                             project_context = """Project: Flowt Pipeline - Floating Litter Observation & Waste Tracking
# Purpose: YOLO fine-tuning for automated detection of plastic and floating debris in waterways to protect aquatic ecosystems.
# Litter Classes (26 categories): Packaging (colorful branded), Other_packaging (plain/metallic), S_bubblewrap, S_label, S_squeeze, S_straw, PS_string, P_cardboard, P_foodcontainer, PH_cup, H_packaging, H_beveragebottle, H_otherbottle, H_plate/bowl, H_utensil, DH_lid, D_polystyrene, M_beveragecan, M_foodcan/tin, M_aerosol, R_ball/balloon, G_beveragebottle, F_facemask, T_wood/timber, Other.
# Materials: Soft/Hard Plastic, Cardboard, Paper, Aluminium, Polystyrene, Metal, Rubber, Glass, Fabric, Timber - each with different detection challenges."""
                            
#                             chat_prompt = f"""{project_context}
# Training Session Data: {json.dumps(session_data, indent=2)}
# User Question: {user_question}
# Provide a detailed explanation based on the training data and output. Focus on YOLO-specific metrics and marine litter detection context for the 26 litter classes."""
                            
#                             available_providers = ai_service.get_available_providers()
#                             provider = available_providers[0] if available_providers else "google"
#                             response = ai_service.generate_analysis(chat_prompt, provider)
                            
#                             if response:
#                                 st.markdown("**AI Response:**")
#                                 st.markdown(response)
#                             else:
#                                 st.error("Failed to get AI response. Please check your API configuration.")
                        
#                         except Exception as e:
#                             st.error(f"Chat error: {str(e)}")
        
#         except ImportError:
#             st.warning("AI analysis not available. Please install required dependencies (google-generativeai, openai).")
#         except Exception as e:
#             st.error(f"AI service initialization failed: {str(e)}")