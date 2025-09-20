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
    width: 200px !important;
    border: none !important;
}

/* Tertiary buttons - white */
button[kind="tertiary"] {
    background-color: white !important;
    color: Blue !important;
    width: 200px !important;
    border: 1px solid #ccc !important;
}

.stButton > button {
    white-space: nowrap !important;
}
</style>
""", unsafe_allow_html=True)
st.title("🔍 Inference")
st.markdown("Run YOLO object detection on uploaded videos to detect marine litter.")

# Debug: Show current session state
# st.write(f"Debug - nav_video: {st.session_state.get('nav_video', 'Not set')}")

# Navigation buttons
col1, col2, col3 = st.columns([1, 6, 1])
with col1:
    if st.button("◀ Previous", type="primary"):
        st.switch_page("pages/1_📁_Data_Ingestion.py")
with col3:
    if st.button("Next ▶", type="primary"):
        st.switch_page("pages/3_✏️_Curation.py")

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


if all_models:
     # Sort to show latest fine-tuned models first
    all_models.sort(key=lambda x: Path(x).stat().st_mtime, reverse=True)
    
    data_dir = Path("data/videos")
    if data_dir.exists():
        video_files = list(data_dir.glob("*.mp4")) + list(data_dir.glob("*.avi")) + list(data_dir.glob("*.mov")) + list(data_dir.glob("*.mkv")) + list(data_dir.glob("*.tls"))
        if video_files:
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
                    # Video selection
                    st.header("Video Selection")
                    video_names = sorted([v.name for v in video_files] if video_files else [])
                    # Initialize tracking_video_selection if not exists
                    if 'video_selection' not in st.session_state:
                        nav_video = st.session_state.get('nav_video', '')
                        if nav_video:
                            nav_video_full = f"{nav_video}.mp4" if not nav_video.endswith('.mp4') else nav_video
                            st.session_state.video_selection = nav_video_full if nav_video_full in video_names else (video_names[0] if video_names else "")
                        else:
                            st.session_state.video_selection = video_names[0] if video_names else ""
                    
                    def update_nav_video():
                        selected = st.session_state.video_selection
                        st.session_state.nav_video = selected.replace('.mp4', '') if selected.endswith('.mp4') else selected
                    
                    selected_video = st.selectbox(
                        "Select Video",
                        video_names,
                        key="video_selection",
                        on_change=update_nav_video
                    )

                    # Check for existing files
                    model_name = Path(model_path).stem
                    video_name = Path(selected_video).stem
                    
                    existing_files = []
                    results_dir = Path(f"data/results/{model_name}")
                    if (results_dir / f"{video_name}_detections.json").exists():
                        existing_files.append("Detection results")
                    
                    curated_dir = Path(f"data/curated/{model_name}")
                    if (curated_dir / f"{video_name}_curated_detections.json").exists():
                        existing_files.append("Curated data")
                    
                    tracking_dir = Path(f"data/tracking/{model_name}")
                    if (tracking_dir / f"{video_name}_tracking.json").exists():
                        existing_files.append("Tracking data")
                    
                    analysis_dir = Path(f"data/analysis/{model_name}")
                    if any(analysis_dir.glob(f"*{video_name}*")):
                        existing_files.append("Analysis results")
        else:
            st.warning("No videos found. Please upload videos in the Data Ingestion page.")
    else:
        st.warning("No videos found. Please upload videos in the Data Ingestion page.")
else:
    st.error("No models found. Please ensure models are available in 'models' or 'models_ft' directories.")
    model_path = None

# Run inference button - always show (only if model is selected)
if model_path and st.button("Run Inference", type="secondary"):
    # Check for existing files and show warning after button click
    if existing_files and not st.session_state.get('confirmed_overwrite', False):
        st.warning(f"⚠️ Running inference will overwrite existing: {', '.join(existing_files)}")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("⚠️ Proceed & Overwrite", type="tertiary"):
                # Remove existing files
                for file_path in [
                    results_dir / f"{video_name}_detections.json",
                    curated_dir / f"{video_name}_curated_detections.json",
                    tracking_dir / f"{video_name}_tracking.json"
                ]:
                    if file_path.exists():
                        file_path.unlink()
                
                # Remove analysis files
                if analysis_dir.exists():
                    for file_path in analysis_dir.glob(f"*{video_name}*"):
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
                video_path = data_dir / selected_video
                
                # Run inference
                results = yolo_model.run_inference(
                    video_path, 
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
elif (results_dir / f"{video_name}_detections.json").exists():
    import json
    try:
        with open(results_dir / f"{video_name}_detections.json", 'r') as f:
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
