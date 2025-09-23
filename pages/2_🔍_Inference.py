import streamlit as st
from pathlib import Path
import sys
import os
sys.path.append(str(Path(__file__).parent.parent))
from src.yolo_inference import YOLOInference

st.set_page_config(page_title="Inference", page_icon="🔍")

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
st.title("🔍 Inference")
st.markdown("Run YOLO object detection on uploaded videos and images to detect marine litter.")

left_col, spacer_col, right_col = st.columns([0.1, 1, 0.1])

with left_col:
    if st.button("◀ Previous",  key="nav_prev", type="primary"):
        st.switch_page("pages/1_📁_Data_Ingestion.py")

with right_col:
    if st.button("Next ▶", key="nav_next", type="primary"):
        st.switch_page("pages/3_✏️_Curation.py")
# Navigation buttons in gray row
# col1, col2, col3 = st.columns([1, 5, 1])
# with col1:
#     if st.button("◀ Previous", type="primary", key=prev_button_key):
#         st.switch_page("pages/1_📁_Data_Ingestion.py")
# with col3:
#     if st.button("Next ▶", type="primary", key=next_button_key):
#         st.switch_page("pages/3_✏️_Curation.py")
# st.markdown('</div>', unsafe_allow_html=True)

# Initialize YOLO inference
@st.cache_resource
def load_yolo_model():
    return YOLOInference()
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
    all_models.sort(key=lambda x: Path(x).stat().st_mtime, reverse=True)
    
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
    
    if media_files:
        col_model, col_video = st.columns([1, 1])
        with col_model:
            # Model selection
            st.header("Model Configuration")
            
            # Use nav_model if available
            nav_model = st.session_state.get('nav_model', '')
            # Extract model name from path if nav_model is a full path
            nav_model_name = Path(nav_model).stem if nav_model else ''
            default_model = nav_model_name if nav_model_name in all_models else (all_models[0] if all_models else "")
            
            model_path = st.selectbox(
                "Select Model",
                all_models,
                index=all_models.index(default_model) if default_model in all_models else 0,
                help="Choose your pre-trained or fine-tuned YOLO model"
            )
            st.session_state.nav_model = model_path
            
            # st.session_state.nav_model = f"models/{selected_model}.pt"

            # # nav_model = st.session_state.get('nav_model', '')
            # default_model = nav_model if nav_model in all_models else (all_models[0] if all_models else "")
            
            # model_path = st.selectbox(
            #     "Select YOLO Model", 
            #     all_models,
            #     index=all_models.index(default_model) if default_model in all_models else 0,
            #     help="Choose your pre-trained or fine-tuned YOLO model"
            # )
            
            # Always update nav_model to match current selection
            # st.session_state.nav_model = model_path
        
            confidence_threshold = st.slider("Confidence Threshold", 0.1, 1.0, 0.5, 0.05)
        with col_video:
                
                # Media selection
                st.header("Media Selection")
                col1, col2 = st.columns([1, 4])
                with col1:
                    # Media type selection
                    media_type = st.radio("Select Media Type", ["Video", "Image"], horizontal=True)
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

                # Check for existing files
                if selected_media:
                    model_name = Path(model_path).stem
                    media_name = Path(selected_media).stem
                    
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
    else:
        st.warning("No media files found. Please upload videos or images in the Data Ingestion page.")
else:
    st.error("No models found. Please ensure models are available in 'models' or 'models_ft' directories.")
    model_path = None

# Run inference button - always show (only if model and media are selected)
if model_path and selected_media and st.button("Run Inference", type="secondary"):
    # Check for existing files and show warning after button click
    if existing_files and not st.session_state.get('confirmed_overwrite', False):
        st.warning(f"⚠️ Running inference will overwrite existing: {', '.join(existing_files)}")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("⚠️ Proceed & Overwrite", type="tertiary"):
                # Remove existing files
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
                st.rerun()
        
        with col2:
            if st.button("❌ Cancel", type="tertiary"):
                st.info("Inference cancelled.")
    else:
        # Clear confirmation flag and run inference
        if 'confirmed_overwrite' in st.session_state:
            del st.session_state.confirmed_overwrite
        
        with st.spinner("Running YOLO inference..."):
            try:
                yolo_model = load_yolo_model()
                
                # Determine media path based on file type
                media_file = Path(selected_media)
                if media_file.suffix.lower() in ['.jpg', '.jpeg', '.png', '.bmp', '.tiff']:
                    media_path = images_dir / selected_media
                else:
                    media_path = videos_dir / selected_media
                
                # Run inference
                results = yolo_model.run_inference(
                    media_path, 
                    model_path, 
                    confidence_threshold
                )
                
                # Store results in session state
                st.session_state.inference_results = results
                st.session_state.inference_completed = True
                
                st.success(f"Inference completed! Detected {len(results)} objects.")

            except Exception as e:
                st.error(f"Inference failed: {str(e)}")

st.markdown('<hr style="margin: 5px 0; border: 1px solid #ddd;">', unsafe_allow_html=True)
# Display results if available (from current session or existing files)
results = None

# Check if we have results from current session
if hasattr(st.session_state, 'inference_completed') and st.session_state.inference_completed:
    results = st.session_state.inference_results

# If no current session results, try to load existing results
elif 'media_name' in locals() and (results_dir / f"{media_name}_detections.json").exists():
    import json
    try:
        with open(results_dir / f"{media_name}_detections.json", 'r') as f:
            results = json.load(f)
    except Exception as e:
        st.error(f"Error loading existing results: {str(e)}")

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
