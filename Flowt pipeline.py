import streamlit as st
from pathlib import Path
st.markdown("""
<style>

/* Primary buttons (Navigation) - blue */
button[kind="primary"] {
    background-color: blue !important;
    color: white !important;
    width: 200px !important;
    border: none !important;
}
</style>
""", unsafe_allow_html=True)
# Configure page
st.set_page_config(
    page_title="Flowt pipeline",
    page_icon="🌊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Main page
st.title("🌊 FLOWT - Floating Litter Observation & Waste Tracking")
st.markdown("### Marine Litter Detection Pipeline")

st.markdown("""
Welcome to FLOWT, a comprehensive pipeline for floating litter detection using YOLO models.

**Pipeline Components:**
- 📁 **Data Ingestion** - Upload and manage video datasets
- 🔍 **Inference** - YOLO-based trash detection
- ✏️ **Curation** - Review and correct detections
- 👁️ **Tracking** - Assign Tracking ID to unique detected trash 
- 🎬 **Video Generation** - Generate corrected videos
- 📊 **Analysis** - Statistical insights and metrics
- 🤖 **AI-Powered Analysis** - Using LLM for insights and metrics analysis
- 🎯 **Fine-tuning** - Retrain models with curated data

Use the sidebar to navigate between different components of the pipeline.
""")

# Setup shared sidebar
from src.sidebar_config import setup_sidebar
setup_sidebar()

# Status indicators
col1, col2, col3, col4 = st.columns(4)

# Count models
models_dir = Path("models")
model_count = len(list(models_dir.glob("*.pt"))) if models_dir.exists() else 0

# Count processed videos (tracking files)
tracking_dir = Path("data/tracking")
video_count = 0
if tracking_dir.exists():
    for model_dir in tracking_dir.iterdir():
        if model_dir.is_dir():
            video_count += len(list(model_dir.glob("*_tracking.json")))

# Count uploaded videos
videos_dir = Path("data/videos")
uploaded_count = len(list(videos_dir.glob("*.mp4")) + list(videos_dir.glob("*.avi")) + list(videos_dir.glob("*.mov")) + list(videos_dir.glob("*.mkv")) + list(videos_dir.glob("*.tls"))) if videos_dir.exists() else 0

# Count curated detections
curated_dir = Path("data/curated")
curated_count = 0
if curated_dir.exists():
    for model_dir in curated_dir.iterdir():
        if model_dir.is_dir():
            curated_count += len(list(model_dir.glob("*_curated_detections.json")))

with col1:
    st.metric("Models Loaded", model_count)
with col2:
    st.metric("Videos Uploaded", uploaded_count)
with col3:
    st.metric("Videos Processed", video_count)
with col4:
    st.metric("Detections Curated", curated_count)