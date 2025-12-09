import streamlit as st
from pathlib import Path
import sys
import os
import yaml
sys.path.append(str(Path(__file__).parent.parent))

# Config management functions
def load_config():
    config_path = Path("config/config.yaml")
    if config_path.exists():
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    return {}

def save_config(config):
    config_path = Path("config/config.yaml")
    config_path.parent.mkdir(exist_ok=True)
    with open(config_path, 'w') as f:
        yaml.dump(config, f, default_flow_style=False)

st.set_page_config(page_title="Scanning", page_icon="🔍")

# Setup shared sidebar
from src.sidebar_config import setup_sidebar
setup_sidebar()

st.markdown("""
<style>  
          
/* Secondary buttons - green */
button[kind="secondary"] {
    background-color: green !important;
    color: white !important;
    width: 150px !important;
    border: none !important;
            
}
/* Primary buttons (Navigation) - blue */
button[kind="primary"] {
    background-color: blue !important;
    color: white !important;
    width: 150px !important;
    border: none !important;
    margin-left: 0;   /* optional: flush to edge */
    margin-right: 0;  /* optional: flush to edge */
}

/* Tertiary buttons - white */
button[kind="tertiary"] {
    background-color: white !important;
    color: Blue !important;
    width: 200px !important;
    border: 1px solid #ccc !important;
}
/* White background for all selectboxes */
.stSelectbox > div > div {
    background-color: white !important;
}
  
</style>
""", unsafe_allow_html=True)
# f0f2f6 border: 1px solid #FFE5B4;
st.title("🔍 Scanning")
st.markdown("Run trash detection model on uploaded videos and images to detect marine litter.")

left_col, spacer_col, right_col = st.columns([0.1, 1, 0.1])

with left_col:
    if st.button("◀ Previous",  key="nav_prev", type="primary"):
        st.switch_page("pages/1_Data_Ingestion.py")

with right_col:
    if st.button("Next ▶", key="nav_next", type="primary"):
        st.switch_page("pages/3_Review.py")
# Initialize YOLO inference
@st.cache_resource
def select_model(model_architecture):
    if model_architecture == "yolo":
        from src.yolo_inference import YOLOInference
        return YOLOInference()
    else:
       
        raise ValueError(f"Unsupported model architecture: {model_architecture}")
    
st.markdown('<hr style="margin: 5px 0; border: 1px solid #ddd;">', unsafe_allow_html=True)

models_dir = Path("models")

# Get base models (only original models, not fine-tuned copies)
base_models = []
if models_dir.exists():
    # Get fine-tuned model names to exclude from base models
    models_ft_dir = Path("models_ft")
    ft_model_names = set()
    if models_ft_dir.exists():
        ft_model_names = {f.name for f in models_ft_dir.glob("*.pt")}
    
    # Only include base models that are not fine-tuned copies
    for f in models_dir.glob("*.pt"):
        if f.name not in ft_model_names:
            base_models.append(str(f))

# Get fine-tuned models
ft_models = []
if models_ft_dir.exists():
    ft_models = [str(f) for f in models_ft_dir.glob("*.pt")]

# Combine all models
all_models = base_models + ft_models

# Initialize model_path
model_path = None

if all_models:
     # Sort to show latest fine-tuned models first
    all_models.sort(key=lambda x: Path(x))
    
    # Get both videos and images
    videos_dir = Path("data/videos")
    images_dir = Path("data/images")
    
    media_files = []
    if videos_dir.exists():
        video_files = list(videos_dir.glob("*.mp4")) + list(videos_dir.glob("*.avi")) + list(videos_dir.glob("*.mov")) + list(videos_dir.glob("*.mkv")) + list(videos_dir.glob("*.tls"))
        media_files.extend(video_files)
    if images_dir.exists():
        image_files = list(images_dir.glob("*.jpg")) + list(images_dir.glob("*.jpeg")) + list(images_dir.glob("*.png")) + list(images_dir.glob("*.bmp")) + list(images_dir.glob("*.tiff"))
        media_files.extend(image_files)
    
    st.header("🔧 Configuration")
    media_type = None
    confidence_threshold = 0.5
    selected_media = None
    col_model, col_video = st.columns([1, 1])
    if media_files:
        with col_model:

            # Use nav_model if available
            nav_model = st.session_state.get('nav_model', '')
            default_model = nav_model if nav_model in all_models else (all_models[0] if all_models else "")
            
            model_path = st.selectbox(
                "Select Model",
                all_models,
                index=all_models.index(default_model) if default_model in all_models else 0,
                help="Choose your pre-trained or fine-tuned model"
            )
            
            # Update nav_model to match current selection
            st.session_state.nav_model = model_path
            
            if "ft" in model_path.lower():
                st.info("💡 Fine-tuned models often work better with lower confidence thresholds (0.1-0.3) - Double-check the Configuration Setting!")
        with col_video:    
                # Media selection
                col1, col2 = st.columns([1, 4])
                with col1:
                    # Media type selection
                    # media_type = st.radio("Select Media Type", ["Video", "Image"], horizontal=True)
                    media_type = st.radio("Select Media Type", ["Video"], horizontal=True)
                with col2:
                # Filter files based on media type
                    if media_type == "Video":
                        filtered_files = [f for f in media_files if f.suffix.lower() in ['.mp4', '.avi', '.mov', '.mkv', '.tls']]
                    else:
                        filtered_files = [f for f in media_files if f.suffix.lower() in ['.jpg', '.jpeg', '.png', '.bmp', '.tiff']]
                    
                    if filtered_files:
                        media_names = sorted([m.name for m in filtered_files])
                        
                        # Initialize media_selection if not exists
                        if 'media_selection' not in st.session_state:
                            nav_video = st.session_state.get('nav_video', '')
                            if nav_video:
                                # Try different extensions
                                for ext in ['.mp4', '.jpg', '.jpeg', '.png']:
                                    nav_media_full = f"{nav_video}{ext}" if not nav_video.endswith(ext) else nav_video
                                    if nav_media_full in media_names:
                                        st.session_state.media_selection = nav_media_full
                                        break
                                else:
                                    st.session_state.media_selection = media_names[0] if media_names else ""
                            else:
                                st.session_state.media_selection = media_names[0] if media_names else ""
                        
                        def update_nav_media():
                            selected = st.session_state.media_selection
                            # Remove common extensions for nav_video
                            for ext in ['.mp4', '.jpg', '.jpeg', '.png', '.bmp', '.tiff']:
                                if selected.endswith(ext):
                                    st.session_state.nav_video = selected.replace(ext, '')
                                    break
                            else:
                                st.session_state.nav_video = selected
                        
                        selected_media = st.selectbox(
                            "Select Media File",
                            media_names,
                            key="media_selection",
                            on_change=update_nav_media
                        )
                    else:
                        st.warning(f"No {media_type.lower()} files found.")
                        selected_media = None

    else:
        st.warning("No media files found. Please upload videos or images in the Data Ingestion page.")
else:
    st.error("No models found. Please ensure models are available in 'models' or 'models_ft' directories.")
    model_path = None
with st.expander("🔧 Configuration Settings", expanded=False):
    col1, col2 = st.columns([1,2])
    #     # Adjust default confidence based on model type

    default_conf = 0.25 if model_path and ("ft" in model_path.lower() or "fine" in model_path.lower()) else 0.5
    with col1:
        confidence_threshold = st.slider(
            "Confidence Threshold",
            min_value=0.1,
            max_value=1.0,
            value=default_conf,
            step=0.05,
            help="Adjust the confidence threshold for detection (0.1-1.0)"
        )
# Check for existing files and clear results if selection changed
if model_path and selected_media:
    model_name = Path(model_path).stem
    media_name = Path(selected_media).stem
    
    # Clear results if model or media selection changed
    current_selection = f"{model_name}_{media_name}"
    if st.session_state.get('last_selection') != current_selection:
        st.session_state.inference_completed = False
        if 'inference_results' in st.session_state:
            del st.session_state.inference_results
        st.session_state.last_selection = current_selection
    
    existing_files = []
    results_dir = Path(f"data/results/{model_name}")
    if (results_dir / f"{media_name}_detections.json").exists():
        existing_files.append("Detection results")
    
    curated_dir = Path(f"data/curated/{model_name}")
    if (curated_dir / f"{media_name}_curated_detections.json").exists():
        existing_files.append("Curated data")
    
    tracking_dir = Path(f"data/tracking/{model_name}")
    if (tracking_dir / f"{media_name}_tracking.json").exists():
        existing_files.append("Tracking data")
    
    analysis_dir = Path(f"data/analysis/{model_name}")
    if any(analysis_dir.glob(f"*{media_name}*")):
        existing_files.append("Analysis results")
else:
    existing_files = []
    model_name = None
    media_name = None

# Initialize session state flags
if 'show_overwrite_warning' not in st.session_state:
    st.session_state.show_overwrite_warning = False
if 'run_inference_now' not in st.session_state:
    st.session_state.run_inference_now = False
# Run inference button - always show (only if model and media are selected)
run_inference_clicked = model_path and selected_media and st.button("Run Scanning", type="secondary")

# Handle overwrite confirmation
if run_inference_clicked:
    if existing_files and not st.session_state.get('confirmed_overwrite', False):
        st.session_state.show_overwrite_warning = True
    else:
        st.session_state.run_inference_now = True

# Show overwrite warning if needed
if st.session_state.get('show_overwrite_warning', False):
    st.warning(f"⚠️ Running scanning will overwrite existing: {', '.join(existing_files)}")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("⚠️ Proceed & Overwrite", type="tertiary"):
            import shutil
            
            # Remove frames folder
            frames_dir = Path(f"data/results/{model_name}/{media_name}_frames")
            if frames_dir.exists():
                shutil.rmtree(frames_dir)
            
            # Remove JSON files
            for file_path in [
                results_dir / f"{media_name}_detections.json",
                curated_dir / f"{media_name}_curated_detections.json",
                tracking_dir / f"{media_name}_tracking.json"
            ]:
                if file_path.exists():
                    file_path.unlink()
            
            # Remove analysis files
            if analysis_dir.exists():
                for file_path in analysis_dir.glob(f"*{media_name}*"):
                    file_path.unlink()
            
            st.session_state.confirmed_overwrite = True
            st.session_state.show_overwrite_warning = False
            st.session_state.run_inference_now = True
            st.rerun()
    
    with col2:
        if st.button("❌ Cancel", type="tertiary"):
            st.session_state.show_overwrite_warning = False
            st.info("Scanning cancelled.")

# Run inference if approved
if st.session_state.get('run_inference_now', False):
    # Clear flags
    st.session_state.run_inference_now = False
    if 'confirmed_overwrite' in st.session_state:
        del st.session_state.confirmed_overwrite
    
    with st.spinner("Running Scanning..."):
        try:
            selected_model = select_model('yolo')
            
            # Determine media path based on file type
            media_file = Path(selected_media)
            if media_file.suffix.lower() in ['.jpg', '.jpeg', '.png', '.bmp', '.tiff']:
                media_path = images_dir / selected_media
            else:
                media_path = videos_dir / selected_media
            
            # Run inference
            results = selected_model.run_inference(
                media_path, 
                model_path, 
                confidence_threshold
            )
            
            # Store results in session state
            st.session_state.inference_results = results
            st.session_state.inference_completed = True
            
            st.success(f"Scanning completed! Detected {len(results)} objects.")

        except Exception as e:
            st.error(f"Scanning failed: {str(e)}")

st.markdown('<hr style="margin: 5px 0; border: 1px solid #ddd;">', unsafe_allow_html=True)
# Display results if available (from current session or existing files)
results = None

# Check if we have results from current session
if hasattr(st.session_state, 'inference_completed') and st.session_state.inference_completed:
    results = st.session_state.inference_results

# If no current session results, try to load existing results
elif model_name and media_name and (results_dir / f"{media_name}_detections.json").exists():
    import json
    try:
        with open(results_dir / f"{media_name}_detections.json", 'r') as f:
            results = json.load(f)
    except Exception as e:
        st.error(f"Error loading existing results: {str(e)}")
        results = None

# Display results if we have any
if results:
    st.header("Detection Results")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Detections", len(results))
    with col2:
        classes = [r['class'] for r in results]
        st.metric("Unique Classes", len(set(classes)))
    with col3:
        avg_conf = sum(r['confidence'] for r in results) / len(results) if results else 0
        st.metric("Avg Confidence", f"{avg_conf:.2f}")
    
    # Show detection details
    if st.checkbox("Show Detection Details", value=True, key="show_results"):
        # Filter out unwanted columns
        filtered_results = []
        for result in results:
            filtered_result = {k: v for k, v in result.items() 
                            if k not in ['bbox', 'is_true_positive', 'tags']}
            filtered_results.append(filtered_result)
        
        # Center the dataframe with appropriate width
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.dataframe(filtered_results)
