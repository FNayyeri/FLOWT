import streamlit as st
from pathlib import Path
st.markdown("""
<style>
/* Classic Sidebar Styling */
.css-1d391kg {
    background-color: #f8f9fa !important;
    border-right: 2px solid #dee2e6 !important;
}

/* Sidebar header */
.css-1d391kg .css-1v0mbdj {
    background-color: #343a40 !important;
    color: white !important;
    padding: 1rem !important;
    margin-bottom: 1rem !important;
    border-radius: 0.5rem !important;
}

/* Navigation links styling */
.css-1d391kg .stSelectbox > div > div {
    background-color: white !important;
    border: 1px solid #ced4da !important;
    border-radius: 0.375rem !important;
}

/* Sidebar text */
.css-1d391kg .markdown-text-container {
    color: #495057 !important;
    font-weight: 500 !important;
}

/* Navigation section headers */
.css-1d391kg h3 {
    color: #343a40 !important;
    border-bottom: 2px solid #007bff !important;
    padding-bottom: 0.5rem !important;
    margin-bottom: 1rem !important;
}

/* Primary buttons (Navigation) - blue */
button[kind="primary"] {
    background-color: blue !important;
    color: white !important;
    width: 200px !important;
    border: none !important;
}

/* Sidebar navigation items */
.css-1d391kg .stRadio > div {
    background-color: white !important;
    padding: 0.5rem !important;
    border-radius: 0.375rem !important;
    margin-bottom: 0.5rem !important;
    border: 1px solid #e9ecef !important;
}

.css-1d391kg .stRadio > div:hover {
    background-color: #e9ecef !important;
    border-color: #007bff !important;
}
</style>
""", unsafe_allow_html=True)
# Configure page
st.set_page_config(
    page_title="Flowt pipeline",
    page_icon="🌊",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://github.com/FNayyeri/flowt-pipeline',
        'Report a bug': 'https://github.com/FNayyeri/flowt-pipeline/issues',
        'About': 'FLOWT Pipeline - Marine Litter Detection System'
    }
)

# Main page
st.title("🌊 Welcome to FLOWT Pipeline")
st.markdown("""
            **Floating Litter Observation & Waste Tracking** 
            is an AI-powered pipeline for marine debris detection and environmental monitoring.
            """)

col1, col2, col3,  = st.columns([1,1.2,2])
with col1:
    st.markdown("""
                ---
                **Pipeline Components:**
                - 📁 **Data Ingestion** - Upload videos
                - 🔍 **Inference** - Detect litter
                - ✏️ **Review** - Review detections
                - 👁️ **Tracking** - Track trash objects 
                - 🎬 **Video Generation** - Create output
                - 📊 **Analysis** - View metrics
                - 🤖 **AI-Powered Analysis** - Get insights
                - 🎯 **Fine-tuning** - Improve models
                            
                ---
                            

                **Navigation:**
                            
                - Select a component from the pages above to get started.
                ---

    """)

with col3:
    col1, col2 = st.columns(2)
    try:
        with col1:
            st.image("config/img/frame_0.jpg", width='stretch')
            st.image("config/img/frame_6.jpg", width='stretch')
        with col2:
            st.image("config/img/frame_20.jpg", width='stretch')
            st.image("config/img/frame_25.jpg", width='stretch')
            
    except:
        pass
    

# Setup shared sidebar with classic styling
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

st.markdown("---")
# Quick start guide
st.markdown("### 🚀 Quick Start Guide")
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown("""
    **Step 1-3: Data & Detection**
    - Upload videos
    - Run the inference  
    - Review detections
    """)
with col2:
    st.markdown("""
    **Step 4-6: Processing**
    - Track objects
    - Generate videos
    - Analyze results
    """)
with col3:
    st.markdown("""
    **Step 7-8: Intelligence**
    - AI-powered insights
    - Model fine-tuning
    """)