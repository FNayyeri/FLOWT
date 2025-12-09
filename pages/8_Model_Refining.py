import streamlit as st
from pathlib import Path
import sys
import json
import yaml
import pandas as pd
import psutil
import time

sys.path.append(str(Path(__file__).parent.parent))
from src import sidebar_config, fine_tuner


st.set_page_config(page_title="Fine Tuning", page_icon="🔧", layout="wide")

# Setup shared sidebar
sidebar_config.setup_sidebar()

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
    width: 150px !important;
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
/* White background for all selectboxes */
.stSelectbox > div > div {
    background-color: white !important;
}
</style>
""", unsafe_allow_html=True)

st.title("🔧 Model Refining")
st.markdown("Fine-tune baseline models using curated detection data.")

# Navigation buttons
left_col, spacer_col, right_col = st.columns([0.1, 1, 0.1])
with left_col:
    if st.button("◀ Previous", type="primary"):
        st.switch_page("pages/7_AI_Insight.py")
with right_col:
    if st.button("Next ▶", type="primary"):
        st.switch_page("pages/2_Inference.py")

st.markdown('<hr style="margin: 5px 0; border: 1px solid #ddd;">', unsafe_allow_html=True)

# Configuration
st.header("Step 1 - Create Curated Dataset")

curated_base_dir = Path("data/curated")
videos_dir = Path("data/videos")
models_dir = Path("models")
models_ft_dir = Path("models_ft")

# Get training history
training_log_path = Path("data/training_log")
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
        
        with col2:
            st.write("")  # Spacer
            curated_dataset_dir = Path("data/curated_dataset")
            if curated_dataset_dir.exists() and (curated_dataset_dir / "images").exists():
                images_count = len(list((curated_dataset_dir / "images").glob("*.jpg")))
                if images_count > 0:
                    st.info(f"Curated dataset: {images_count} images")
                else:
                    st.info("Curated dataset exists but no images found")
            else:
                images_count = 0
                st.info("No curated dataset found")

        # Initialize variables before usage (moved outside columns)
        curated_files = list((curated_base_dir / selected_model_dir).glob("*.json"))
        
        # Load class names and fine-tuning parameters from config
        config_path = Path(__file__).parent.parent / "config" / "config.yaml"
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        class_names = config.get('detection_classes', {}).get('names', [])
            
        with col3:
            st.write("")  # Spacer
            ft_dataset_dir = Path("data/ft_dataset")
            if ft_dataset_dir.exists():
                train_count = len(list((ft_dataset_dir / "train" / "images").glob("*.jpg"))) if (ft_dataset_dir / "train" / "images").exists() else 0
                val_count = len(list((ft_dataset_dir / "val" / "images").glob("*.jpg"))) if (ft_dataset_dir / "val" / "images").exists() else 0
                test_count = len(list((ft_dataset_dir / "test" / "images").glob("*.jpg"))) if (ft_dataset_dir / "test" / "images").exists() else 0
                if train_count + val_count + test_count > 0:
                    st.info(f"Prepared dataset: {train_count + val_count + test_count} images\n(train: {train_count}, val: {val_count}, test: {test_count})")
                else:
                    st.info("Prepared dataset exists but no images found")
            else:
                st.info("No prepared dataset found")

        if st.button("Create Dataset", type="secondary"):
            with st.spinner("Creating curated dataset..."):
                try:
                    
                    
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    # Create dataset using the function
                    result = fine_tuner.create_curated_dataset(
                        curated_files, 
                        videos_dir, 
                        class_names,
                        progress_callback=progress_bar.progress,
                        status_callback=status_text.text
                    )
                    
                    progress_bar.progress(1.0)
                    status_text.text("Dataset creation completed!")
                    
                    st.success(f"Curated dataset updated: {result['processed_count']} positive images, {result['background_count']} background images added")
                    st.info(f"Total curated dataset size: {result['total_images']} images ({result['skipped_duplicates']} duplicates skipped)")
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"Dataset creation failed: {str(e)}")

        # Step 2 - Prepare Fine-tuning Dataset
        st.header("Step 2 - Prepare Fine-tuning Dataset")
        
        # Get current config from config
        dataset_config = fine_tuner.get_dataset_config()
        
        with st.expander("🔧 Configuration", expanded=False):
            col1, col2 = st.columns(2)
            with col1:
                train_ratio = st.slider("Train Ratio", 0.5, 0.95, dataset_config['train_ratio'], 0.05, key="train_ratio")
                include_test = st.checkbox("Test Set Include", value=dataset_config['include_test'], key="include_test")
            with col2:
                actual_train, actual_val, actual_test = fine_tuner.calculate_ratios(train_ratio, include_test)
                test_info = f"{actual_test:.1%}" if include_test else "Not included"
                st.write(f"**Resulting Split:**")
                st.info(f"""
                    - Train: {actual_train:.1%}
                    - Validation: {actual_val:.1%}
                    - Test: {test_info}
                    """)

            # Update config if changed
            if (train_ratio != dataset_config['train_ratio'] or 
                include_test != dataset_config['include_test']):
                fine_tuner.update_dataset_config(train_ratio, include_test)
                st.rerun()
        if curated_dataset_dir.exists() and images_count > 0:
            if st.button("Prepare Data", type="secondary"):
                with st.spinner("Preparing fine-tuning dataset..."):
                    try:
                        ft_dataset_dir = Path("data/ft_dataset")
                        train_count, val_count, test_count = fine_tuner.prepare_ft_dataset(
                            curated_dataset_dir, ft_dataset_dir, class_names, 
                            train_ratio, include_test
                        )
                        
                        if include_test:
                            st.success(f"Fine-tuning dataset prepared!\n- Train: {train_count} images\n- Val: {val_count} images\n- Test: {test_count} images")
                        else:
                            st.success(f"Fine-tuning dataset prepared!\n- Train: {train_count} images\n- Val: {val_count} images\n- Test: Not included")
                        time.sleep(2)
                        st.rerun()
                        
                    except Exception as e:
                        st.error(f"Error preparing dataset: {str(e)}")
        else:
            st.info("Create curated dataset first")
else:
    st.warning("No curated data or baseline models found.")

# st.markdown("---")
st.markdown('<hr style="margin: 5px 0; border: 1px solid #ddd;">', unsafe_allow_html=True)
st.header("Step 3 - Fine-Tuning")
dataset_exists = Path("data/ft_dataset").exists()

if dataset_exists and images_count > 0:
    
    
    # Get system and configuration info
    system_info = fine_tuner.get_system_info()
    training_config = fine_tuner.get_training_config()
  
    # Calculate current iteration
    current_iteration = len([h for h in training_history if h['base_model'] == selected_model_dir]) + 1

            
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
    
    with st.expander("System Information", expanded=False):
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("CPU Cores", psutil.cpu_count())
        with col2:
            st.metric("Memory", f"{round(psutil.virtual_memory().total / (1024**3), 1)} GB")
        with col3:
            if system_info['gpu_available']:
                gpu_name = system_info['gpu_name']
                st.metric("GPU", f"{system_info['gpu_count']}x {gpu_name.split()[-1] if gpu_name != 'N/A' else 'Available'}")
            else:
                st.metric("GPU", "CPU Only")
    
    with st.expander("Fine-Tuning Configuration", expanded=False):
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            epochs = st.number_input("Epochs", min_value=2, max_value=200, value=training_config['epochs'], step=1, key="epochs_number")
            conf_threshold = st.slider("Detection Threshold", 0.1, 0.9, training_config['conf_threshold'], 0.05)
        with col2:
            frozen_layers = st.number_input("Frozen Layers", min_value=0, max_value=15, value=training_config['frozen_layers'], step=1, key="frozen_number")
            augment = st.checkbox("Data Augmentation", value=training_config['augment'], help="Apply data augmentation during training")
        with col3:
            batch_sizes = [8, 16, 32, 64]
            default_batch_idx = batch_sizes.index(training_config['batch_size']) if training_config['batch_size'] in batch_sizes else 1
            batch_size = st.selectbox("Batch Size", batch_sizes, index=default_batch_idx)
        with col4:
            device_options = ["auto", "cpu"] + (["gpu"] if system_info['gpu_available'] else [])
            device_idx = device_options.index(training_config['device']) if training_config['device'] in device_options else 0
            device = st.selectbox("Training Device", device_options, index=device_idx)
        
    if st.button("Start Fine-Tuning", type="secondary", disabled=not dataset_exists):
        with st.spinner("Fine-tuning model..."):
            try:
                
                
                # Run fine-tuning
                training_metrics, ft_model_name = fine_tuner.run_fine_tuning(
                    selected_model_dir, selected_baseline, current_iteration, class_names,
                    epochs, batch_size, frozen_layers, conf_threshold, augment, device, system_info
                )
                
                # Create training entry for history
                training_entry = {
                    "timestamp": pd.Timestamp.now().strftime("%Y%m%d_%H%M%S"),
                    "iteration": current_iteration,
                    "base_model": selected_model_dir,
                    "baseline_used": selected_baseline,
                    "model_name": ft_model_name,
                    "parameters": {
                        "epochs": epochs,
                        "batch_size": batch_size,
                        "frozen_layers": frozen_layers,
                        "conf_threshold": conf_threshold,
                        "augment": augment,
                        "device": device
                    },
                    "dataset_info": {
                        "total_images": images_count,
                        "classes": len(class_names),
                        "class_names": class_names
                    },
                    "training_metrics": training_metrics
                }
                
                # Add to training history
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

    # Save parameters to config when changed
    if 'frozen_layers' in locals() and 'epochs' in locals() and 'batch_size' in locals() and 'conf_threshold' in locals() and 'augment' in locals() and 'device' in locals():
        if (frozen_layers != training_config['frozen_layers'] or 
            epochs != training_config['epochs'] or 
            batch_size != training_config['batch_size'] or
            conf_threshold != training_config['conf_threshold'] or
            augment != training_config['augment'] or
            device != training_config['device']):
            
            fine_tuner.update_training_config(frozen_layers, epochs, batch_size, conf_threshold, augment, device)
            st.rerun()

else:
    st.warning("Curated data or models directory not found.")
    # Still show AI Analysis section even if no current training
    st.markdown('<hr style="margin: 5px 0; border: 1px solid #ddd;">', unsafe_allow_html=True)
    st.header("Model Versions")
    st.info("No models available for version management.")
    


st.markdown('<hr style="margin: 5px 0; border: 1px solid #ddd;">', unsafe_allow_html=True)

# Display existing fine-tuned models with performance
st.header("Model Versions")
fine_tuner.display_model_versions(models_ft_dir, models_dir, training_history, training_log_path)

# AI Analysis Section
fine_tuner.display_ai_analysis()