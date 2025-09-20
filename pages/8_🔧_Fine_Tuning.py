import streamlit as st
from pathlib import Path
import sys
import json
import cv2
import shutil
import yaml
import pandas as pd
import platform
import psutil
import time
sys.path.append(str(Path(__file__).parent.parent))

st.set_page_config(page_title="Fine Tuning", page_icon="🔧", layout="wide")

# Setup shared sidebar
from src.sidebar_config import setup_sidebar
setup_sidebar()

st.markdown("""
<style>
button[kind="secondary"] {
    background-color: green !important;
    color: white !important;
    width: 150px !important;
    border: none !important;
}
button[kind="primary"] {
    background-color: blue !important;
    color: white !important;
    width: 200px !important;
    border: none !important;
}
button[kind="tertiary"] {
    background-color: white !important;
    color: Red !important;
    width: 100px !important;
    border: none !important;
}
.stButton > button {
    white-space: nowrap !important;
}
</style>
""", unsafe_allow_html=True)

st.title("🔧 Fine Tuning")
st.markdown("Fine-tune baseline models using curated detection data.")

# Navigation buttons
col1, col2, col3 = st.columns([1, 6, 1])
with col1:
    if st.button("◀ Previous", type="primary"):
        st.switch_page("pages/7_🤖_Analysis_AI.py")
with col3:
    if st.button("Next ▶", type="primary"):
        st.switch_page("pages/1_📁_Data_Ingestion.py")

st.markdown('<hr style="margin: 5px 0; border: 1px solid #ddd;">', unsafe_allow_html=True)

# Configuration
st.header("Dataset")

curated_base_dir = Path("data/curated")
videos_dir = Path("data/videos")
models_dir = Path("models")
models_ft_dir = Path("models_ft")

# Get training history
training_log_path = Path("data/training_log.json")
if training_log_path.exists():
    with open(training_log_path, 'r') as f:
        training_history = json.load(f)
    
    # Clean up training history - remove entries for deleted models
    if models_ft_dir.exists():
        existing_models = [f.name for f in models_ft_dir.glob("*.pt")]
        original_count = len(training_history)
        training_history = [h for h in training_history if h['model_name'] in existing_models]
        
        # Save cleaned history if changes were made
        if len(training_history) != original_count:
            with open(training_log_path, 'w') as f:
                json.dump(training_history, f, indent=2)
else:
    training_history = []

if curated_base_dir.exists() and models_dir.exists():
    # Get available models and curated data
    model_dirs = [d for d in curated_base_dir.iterdir() if d.is_dir()]
    baseline_models = [f.stem for f in models_dir.glob("*.pt")]
    
    # Add fine-tuned models as baseline options
    if models_ft_dir.exists():
        ft_models = [f"ft/{f.stem}" for f in models_ft_dir.glob("*.pt")]
        baseline_models.extend(ft_models)
    
    if model_dirs and baseline_models:
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # Use nav_model if available
            model_names = [d.name for d in model_dirs]
            nav_model = st.session_state.get('nav_model', '')
            # Extract model name from path if nav_model is a full path
            nav_model_name = Path(nav_model).stem if nav_model else ''
            default_model = nav_model_name if nav_model_name in model_names else (model_names[0] if model_names else "")
            
            selected_model_dir = st.selectbox(
                "Curated Data Model", 
                model_names,
                index=model_names.index(default_model) if default_model in model_names else 0
            )
            
            # Update nav_model to match current selection
            st.session_state.nav_model = f"models/{selected_model_dir}.pt"
        
        # Initialize variables before usage
        curated_files = list((curated_base_dir / selected_model_dir).glob("*.json"))
        total_true_positives = 0
        
        # Load class names and fine-tuning parameters from config
        config_path = Path(__file__).parent.parent / "config" / "config.yaml"
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        class_names = config.get('detection_classes', {}).get('names', [])
        
        # Get fine-tuning defaults from config
        ft_config = config.get('fine_tuning', {})
        default_frozen_layers = ft_config.get('frozen_layers', 9)
        default_epochs = ft_config.get('epochs', 50)
        default_batch_size = ft_config.get('batch_size', 16)
        default_conf_threshold = ft_config.get('conf_threshold', 0.25)
        default_augment = ft_config.get('augment', True)
        default_device = ft_config.get('device', 'auto')
        
        # Count total true positive detections for dataset size
        for curated_file in curated_files:
            with open(curated_file, 'r') as f:
                data = json.load(f)
            for detection in data:
                if detection.get('is_true_positive', True):
                    total_true_positives += 1

        try:
            import torch
            gpu_available = torch.cuda.is_available()
            gpu_count = torch.cuda.device_count() if gpu_available else 0
            gpu_name = torch.cuda.get_device_name(0) if gpu_available else "N/A"
        except:
            gpu_available = False
            gpu_count = 0
            gpu_name = "N/A"
        
        # Calculate current iteration
        current_iteration = len([h for h in training_history if h['base_model'] == selected_model_dir]) + 1
        
        # with col2:
        if st.button("Create Dataset", type="secondary"):
            with st.spinner("Creating training dataset..."):
                try:
                    # Create dataset directories
                    dataset_dir = Path("data/fine_tuning_dataset")
                    images_dir = dataset_dir / "images"
                    labels_dir = dataset_dir / "labels"
                    
                    # Create directories if they don't exist
                    images_dir.mkdir(parents=True, exist_ok=True)
                    labels_dir.mkdir(parents=True, exist_ok=True)
                    
                    # Get existing image count to continue numbering (start from 1)
                    existing_images = list(images_dir.glob("*.jpg"))
                    file_counter = len(existing_images) + 1
                    
                    # Track existing image hashes to avoid duplicates
                    existing_hashes = set()
                    for img_path in existing_images:
                        try:
                            import hashlib
                            with open(img_path, 'rb') as f:
                                img_hash = hashlib.md5(f.read()).hexdigest()
                            existing_hashes.add(img_hash)
                        except:
                            pass
                    
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    # Process curated files
                    processed_count = 0
                    background_count = 0
                    skipped_duplicates = 0
                    
                    for i, curated_file in enumerate(curated_files):
                        video_name = curated_file.stem.replace('_curated_detections', '')
                        video_path = videos_dir / f"{video_name}.mp4"
                        
                        if not video_path.exists():
                            continue
                        
                        status_text.text(f"Processing {video_name}...")
                        
                        # Load curated data
                        with open(curated_file, 'r') as f:
                            curated_data = json.load(f)
                        
                        # Group detections by frame and separate true/false positives
                        frames_with_true_positives = {}
                        frames_with_false_positives = set()
                        
                        for detection in curated_data:
                            frame_num = detection['frame']
                            if detection.get('is_true_positive', True):
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
                                import hashlib
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
                                        
                                        # Convert to YOLO format (normalized) - fix bbox format
                                        # bbox format: [x, y, width, height]
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
                                import hashlib
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
                        progress_bar.progress((i + 1) / len(curated_files))
                    
                    # Create dataset.yaml
                    dataset_yaml = dataset_dir / "dataset.yaml"
                    with open(dataset_yaml, 'w') as f:
                        f.write(f"""path: {dataset_dir.absolute()}
                                train: images
                                val: images

                                nc: {len(class_names)}
                                names: {class_names}
                                """)
                    
                    progress_bar.progress(1.0)
                    status_text.text("Dataset creation completed!")
                    
                    total_images = len(list(images_dir.glob("*.jpg")))
                    st.success(f"Dataset updated: {processed_count} positive images, {background_count} background images added")
                    st.info(f"Total dataset size: {total_images} images ({skipped_duplicates} duplicates skipped)")
                    
                except Exception as e:
                    st.error(f"Dataset creation failed: {str(e)}")
        
        # st.markdown('<hr style="margin: 5px 0; border: 1px solid #ddd;">', unsafe_allow_html=True)
        if total_true_positives > 0:
            # Fine-tuning parameters
            st.header("Fine-Tuning Parameters")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                 # Prioritize latest fine-tuned model for iterative training
                latest_ft_model = None
                if training_history:
                    latest_ft_model = f"ft/{training_history[-1]['model_name'].replace('.pt', '')}"
                
                if latest_ft_model and latest_ft_model in baseline_models:
                    default_idx = baseline_models.index(latest_ft_model)
                elif selected_model_dir in baseline_models:
                    default_idx = baseline_models.index(selected_model_dir)
                else:
                    default_idx = 0
                
                selected_baseline = st.selectbox("Baseline Model", baseline_models, index=default_idx)
            with col3:
                st.metric("Training Iteration", current_iteration)
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                epochs = st.number_input("Epochs", min_value=2, max_value=200, value=default_epochs, step=1, key="epochs_number")
                conf_threshold = st.slider("Detection Threshold", 0.1, 0.9, default_conf_threshold, 0.05)
                
            with col2:
                frozen_layers = st.number_input("Frozen Layers", min_value=0, max_value=15, value=default_frozen_layers, step=1, key="frozen_number")
                augment = st.checkbox("Data Augmentation", value=default_augment, help="Apply data augmentation during training")
            with col3:    
                batch_sizes = [8, 16, 32, 64]
                default_batch_idx = batch_sizes.index(default_batch_size) if default_batch_size in batch_sizes else 1
                batch_size = st.selectbox("Batch Size", batch_sizes, index=default_batch_idx)
            with col4:
                
                # Device selection
                device_options = ["auto", "cpu"] + (["gpu"] if gpu_available else [])
                device_idx = device_options.index(default_device) if default_device in device_options else 0
                device = st.selectbox("Training Device", device_options, index=device_idx)

            # Create Dataset and Fine-Tuning buttons
            # col1, col2, col3 = st.columns(3)
            
            # with col1:
            dataset_exists = Path("data/fine_tuning_dataset").exists()
            
            if st.button("Start Fine-Tuning", type="secondary", disabled=not dataset_exists):
                if not dataset_exists:
                    # st.error("Please create dataset first!")
                    st.error("Create dataset first to enable fine-tuning")
                else:
                    with st.spinner("Fine-tuning model..."):
                        try:
                            # Fine-tune model
                            models_ft_dir = Path("models_ft")
                            models_ft_dir.mkdir(exist_ok=True)
                            
                            # Generate versioned model name
                            timestamp = pd.Timestamp.now().strftime("%Y%m%d_%H%M%S")
                            ft_model_name = f"{selected_model_dir}_{current_iteration}_{timestamp}.pt"
                            ft_model_path = models_ft_dir / ft_model_name
                            
                            dataset_yaml = Path("data/fine_tuning_dataset/dataset.yaml")
                            
                            # Load baseline model (original or fine-tuned)
                            if selected_baseline.startswith("ft/"):
                                base_model_path = models_ft_dir / f"{selected_baseline[3:]}.pt"
                            else:
                                base_model_path = models_dir / f"{selected_baseline}.pt"
                            
                            # Get system info before training
                            import platform
                            import psutil
                            import time
                            
                            start_time = time.time()
                            
                            # Capture training output
                            import subprocess
                            import sys
                            from io import StringIO
                            import contextlib
                            
                            # Capture stdout for training logs
                            training_output = StringIO()
                            
                            # Actual YOLO training with output capture
                            from ultralytics import YOLO
                            model = YOLO(str(base_model_path))
                            
                            # Set device for training - fix auto device issue
                            if device == "gpu" and gpu_available:
                                train_device = 0
                            elif device == "cpu":
                                train_device = "cpu"
                            else:  # device == "auto"
                                train_device = 0 if gpu_available else "cpu"
                            
                            # Capture training output
                            with contextlib.redirect_stdout(training_output):
                                results = model.train(
                                    data=str(dataset_yaml), 
                                    epochs=epochs, 
                                    batch=batch_size, 
                                    freeze=frozen_layers,
                                    conf=conf_threshold,
                                    augment=augment,
                                    device=train_device
                                )
                            
                            model.save(str(ft_model_path))
                            
                            # Get training log content
                            training_log_content = training_output.getvalue()
                            
                            end_time = time.time()
                            training_duration = end_time - start_time
                            
                            # Also copy to models directory for easy access in inference
                            import shutil
                            models_copy_path = models_dir / ft_model_name
                            shutil.copy2(ft_model_path, models_copy_path)
                            
                            # Get device info
                            try:
                                import torch
                                device_info = {
                                    "cuda_available": torch.cuda.is_available(),
                                    "cuda_device_count": torch.cuda.device_count() if torch.cuda.is_available() else 0,
                                    "cuda_device_name": torch.cuda.get_device_name(0) if torch.cuda.is_available() else None
                                }
                            except:
                                device_info = {"cuda_available": False, "cuda_device_count": 0, "cuda_device_name": None}
                            
                            # Save detailed training log
                            training_logs_dir = Path("data/training_logs")
                            training_logs_dir.mkdir(exist_ok=True)
                            log_file_path = training_logs_dir / f"{ft_model_name.replace('.pt', '')}_training.log"
                            
                            with open(log_file_path, 'w') as f:
                                f.write(f"Training Log for {ft_model_name}\n")
                                f.write(f"Timestamp: {timestamp}\n")
                                f.write(f"Parameters: Epochs={epochs}, Batch={batch_size}, Frozen={frozen_layers}\n")
                                f.write("="*50 + "\n")
                                f.write(training_log_content)
                            
                            # Log training results
                            training_entry = {
                                "timestamp": timestamp,
                                "iteration": current_iteration,
                                "base_model": selected_model_dir,
                                "baseline_used": selected_baseline,
                                "model_name": ft_model_name,
                                "log_file": str(log_file_path),
                                "parameters": {
                                    "epochs": epochs,
                                    "batch_size": batch_size,
                                    "frozen_layers": frozen_layers,
                                    "conf_threshold": conf_threshold,
                                    "augment": augment,
                                    "device": device
                                },
                                "dataset_info": {
                                    "total_images": total_true_positives,
                                    "classes": len(class_names)
                                },
                                "training_specs": {
                                    "duration_seconds": round(training_duration, 2),
                                    "duration_formatted": f"{int(training_duration//3600):02d}:{int((training_duration%3600)//60):02d}:{int(training_duration%60):02d}",
                                    "system": {
                                        "platform": platform.system(),
                                        "platform_version": platform.version(),
                                        "processor": platform.processor(),
                                        "cpu_count": psutil.cpu_count(),
                                        "memory_gb": round(psutil.virtual_memory().total / (1024**3), 2)
                                    },
                                    "device": device_info
                                },
                                "training_output": training_log_content[-2000:]  # Last 2000 chars for analysis
                            }
                            
                            training_history.append(training_entry)
                            
                            # Save training log
                            training_log_path.parent.mkdir(exist_ok=True)
                            with open(training_log_path, 'w') as f:
                                json.dump(training_history, f, indent=2)
                            
                            st.success(f"Fine-tuning completed! Model saved as {ft_model_name}")
                            st.info(f"💡 Use this model for next inference to continue iterative improvement")
                            
                            # Display results
                            col1, col2, col3, col4 = st.columns(4)
                            with col1:
                                st.metric("Epochs", epochs)
                            with col2:
                                st.metric("Batch Size", batch_size)
                            with col3:
                                st.metric("Device", device.upper())
                            with col4:
                                st.metric("Augmentation", "ON" if augment else "OFF")
                            
                        except Exception as e:
                            st.error(f"Fine-tuning failed: {str(e)}")

        else:
            st.warning("No true positive detections found in curated data.")
            
        
        st.markdown('<hr style="margin: 5px 0; border: 1px solid #ddd;">', unsafe_allow_html=True)        
        # System Information
        st.header("System Information")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            # Show actual dataset size from fine_tuning_dataset
            dataset_dir = Path("data/fine_tuning_dataset")
            if dataset_dir.exists() and (dataset_dir / "images").exists():
                actual_dataset_size = len(list((dataset_dir / "images").glob("*.jpg")))
                st.metric("Dataset Size", f"{actual_dataset_size} images")
            else:
                st.metric("Dataset Size", "0 images")
        with col2:
            st.metric("CPU Cores", psutil.cpu_count())
        with col3:
            st.metric("Memory", f"{round(psutil.virtual_memory().total / (1024**3), 1)} GB")
        with col4:
            if gpu_available:
                st.metric("GPU", f"{gpu_count}x {gpu_name.split()[-1] if gpu_name != 'N/A' else 'Available'}")
            else:
                st.metric("GPU", "CPU Only")

        # Show dataset status
        dataset_dir = Path("data/fine_tuning_dataset")
        if dataset_dir.exists() and (dataset_dir / "images").exists():
            images_count = len(list((dataset_dir / "images").glob("*.jpg")))
            if images_count > 0:
                st.info(f"Existing dataset found with {images_count} images")
            else:
                st.info("Dataset directory exists but no images found. Create dataset first.")
        else:
            st.info("No dataset found. Create dataset first.")
        
        # Save parameters to config when changed (only if variables are defined)
        if 'frozen_layers' in locals() and 'epochs' in locals() and 'batch_size' in locals() and 'conf_threshold' in locals() and 'augment' in locals() and 'device' in locals():
            if (frozen_layers != default_frozen_layers or 
                epochs != default_epochs or 
                batch_size != default_batch_size or
                conf_threshold != default_conf_threshold or
                augment != default_augment or
                device != default_device):
                
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
                
                st.rerun()
        # Training Progress Monitoring
        if training_history:
            st.header("Training Progress")
            
            # Show training iterations
            iterations = [h['iteration'] for h in training_history if h['base_model'] == selected_model_dir]
            
            if len(iterations) > 1:
                st.info(f"Completed {len(iterations)} training iterations for model {selected_model_dir}")
            else:
                st.info(f"Training iteration {len(iterations)} for model {selected_model_dir}")
            
            # Show recent training history
            st.subheader("Recent Training Sessions")
            recent_history = training_history[-5:]  # Last 5 sessions
            for entry in reversed(recent_history):
                specs = entry.get('training_specs', {})
                duration = specs.get('duration_formatted', 'N/A')
                dataset_info = entry.get('dataset_info', {})
                with st.expander(f"v{entry['iteration']} - {entry['timestamp']} - {duration}"):
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.write(f"**Model:** {entry['model_name']}")
                        st.write(f"**Baseline:** {entry['baseline_used']}")
                        st.write(f"**Epochs:** {entry['parameters']['epochs']}")
                        st.write(f"**Batch Size:** {entry['parameters']['batch_size']}")
                    with col2:
                        st.write(f"**Dataset Size:** {dataset_info.get('total_images', 'N/A')} images")
                        st.write(f"**Classes:** {dataset_info.get('classes', 'N/A')}")
                        st.write(f"**Augmentation:** {'ON' if entry['parameters'].get('augment', True) else 'OFF'}")
                        st.write(f"**Device:** {entry['parameters'].get('device', 'auto').upper()}")
                    with col3:
                        if specs:
                            st.write(f"**Duration:** {specs.get('duration_formatted', 'N/A')}")
                            system = specs.get('system', {})
                            device = specs.get('device', {})
                            st.write(f"**CPU:** {system.get('cpu_count', 'N/A')} cores")
                            st.write(f"**Memory:** {system.get('memory_gb', 'N/A')} GB")
                            if device.get('cuda_available'):
                                st.write(f"**GPU:** {device.get('cuda_device_name', 'CUDA Available')}")
                            else:
                                st.write("**GPU:** CPU Only")
    else:
        st.warning("No curated data or baseline models found.")
else:
    st.warning("Curated data or models directory not found.")

st.markdown('<hr style="margin: 5px 0; border: 1px solid #ddd;">', unsafe_allow_html=True)

# Display existing fine-tuned models with performance
st.header("Model Versions")
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
                        training_history = [h for h in training_history if h['model_name'] != model.name]
                        with open(training_log_path, 'w') as f:
                            json.dump(training_history, f, indent=2)
                    
                    st.success(f"Deleted {model.name} from both directories")
                    st.rerun()
    else:
        st.info("No fine-tuned models yet.")
else:
    st.info("No fine-tuned models directory found.")

# AI Analysis Section
if training_history:
    st.header("🤖 AI-Powered Training Results Analysis")
    
    # Import AI service
    try:
        sys.path.append(str(Path(__file__).parent.parent))
        from src.genai_service import GenAIService
        
        # Initialize AI service
        ai_service = GenAIService()
        
        # AI Analysis Options
        analysis_type = st.selectbox(
            "Analysis Type",
            ["Training Performance Analysis", "Parameter Optimisation", "Custom Query"]
        )
        
        if st.button("Generate AI Analysis", type="secondary"):
            with st.spinner("Analysing training data with AI..."):
                try:
                    # Prepare training data for analysis
                    recent_training = training_history[-3:] if len(training_history) >= 3 else training_history
                    
                    analysis_data = {
                        "training_sessions": len(training_history),
                        "recent_results": recent_training,
                        "current_model": selected_model_dir if 'selected_model_dir' in locals() else "unknown",
                        "dataset_size": total_true_positives if 'total_true_positives' in locals() else 0
                    }
                    
                    # Project context
                    project_context = """Project: Flowt Pipeline - Floating Litter Observation & Waste Tracking
Purpose: YOLO fine-tuning for automated detection of plastic and floating debris in waterways to protect aquatic ecosystems.

Litter Classes (26 categories): Packaging (colorful branded), Other_packaging (plain/metallic), S_bubblewrap, S_label, S_squeeze, S_straw, PS_string, P_cardboard, P_foodcontainer, PH_cup, H_packaging, H_beveragebottle, H_otherbottle, H_plate/bowl, H_utensil, DH_lid, D_polystyrene, M_beveragecan, M_foodcan/tin, M_aerosol, R_ball/balloon, G_beveragebottle, F_facemask, T_wood/timber, Other.

Materials: Soft/Hard Plastic, Cardboard, Paper, Aluminium, Polystyrene, Metal, Rubber, Glass, Fabric, Timber - each with different detection challenges."""
                    
                    if analysis_type == "Training Performance Analysis":
                        prompt = f"""{project_context}

Analyze these YOLO fine-tuning results for marine litter detection:

Training Data:
{json.dumps(analysis_data, indent=2)}

Provide analysis on:
1. Training performance trends across the 26 litter classes
2. Model convergence issues for different material types
3. Recommendations for improving detection of specific litter categories
4. Parameter optimization for marine debris detection

Focus on practical actionable insights for environmental monitoring."""
                    
                    elif analysis_type == "Parameter Optimisation":
                        prompt = f"""{project_context}

Analyze these YOLO fine-tuning parameters for marine litter detection:

Current Results:
{json.dumps(analysis_data, indent=2)}

Provide specific recommendations for:
1. Optimal epochs, batch size, frozen layers for 26 litter classes
2. Learning rate adjustments for different material types
3. Data augmentation strategies for floating debris
4. Training schedule improvements for marine environment

Be specific with numerical recommendations considering the environmental application."""
                    
                    else:  # Custom Query
                        custom_query = st.text_area("Enter your custom analysis question:", 
                                                   placeholder="e.g., Why is my model not improving after iteration 3?")
                        if custom_query:
                            prompt = f"""{project_context}

Training Data:
{json.dumps(analysis_data, indent=2)}

User Question: {custom_query}

Provide a detailed analysis based on the training data and marine litter detection context."""
                        else:
                            st.warning("Please enter a custom query.")
                            prompt = None
                    
                    if prompt:
                        # Get AI analysis
                        available_providers = ai_service.get_available_providers()
                        provider = available_providers[0] if available_providers else "google"
                        analysis_result = ai_service.generate_analysis(prompt, provider)
                        
                        if analysis_result:
                            st.subheader("AI Analysis Results")
                            st.markdown(analysis_result)
                        else:
                            st.error("AI analysis failed. Please check your API configuration.")
                
                except Exception as e:
                    st.error(f"AI analysis error: {str(e)}")
        
        # Training Log Chat
        st.subheader("Training Log Chat")
        
        # Select training session for chat
        if training_history:
            session_options = [f"v{h['iteration']} - {h['timestamp']} ({h.get('dataset_info', {}).get('total_images', 'N/A')} images)" 
                             for h in training_history]
            selected_session_idx = st.selectbox(
                "Select Training Session",
                range(len(session_options)),
                format_func=lambda x: session_options[x]
            )
            
            selected_training = training_history[selected_session_idx]
            
            # Chat interface
            user_question = st.text_input(
                "Ask about this training session:",
                placeholder="e.g., Why did the loss not decrease? What does mAP50 of 0.003 mean?"
            )
            
            if st.button("Ask AI", type="secondary") and user_question:
                with st.spinner("Getting AI response..."):
                    try:
                        # Prepare training session data
                        session_data = {
                            "training_session": selected_training,
                            "training_output": selected_training.get('training_output', 'No training output available'),
                            "log_file": selected_training.get('log_file', 'No training output available')
                        }
                        
                        chat_prompt = f"""{project_context}

Training Session Data:
{json.dumps(session_data, indent=2)}

User Question: {user_question}

Provide a detailed explanation based on the training data and output. Focus on YOLO-specific metrics and marine litter detection context for the 26 litter classes."""
                        
                        available_providers = ai_service.get_available_providers()
                        provider = available_providers[0] if available_providers else "google"
                        response = ai_service.generate_analysis(chat_prompt, provider)
                        
                        if response:
                            st.markdown("**AI Response:**")
                            st.markdown(response)
                        else:
                            st.error("Failed to get AI response. Please check your API configuration.")
                    
                    except Exception as e:
                        st.error(f"Chat error: {str(e)}")
    
    except ImportError:
        st.warning("AI analysis not available. Please install required dependencies (google-generativeai, openai).")
    except Exception as e:
        st.error(f"AI service initialization failed: {str(e)}")