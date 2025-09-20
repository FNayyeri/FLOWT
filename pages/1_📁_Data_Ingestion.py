import streamlit as st
import os
import json
import cv2
from pathlib import Path
from datetime import datetime

st.set_page_config(page_title="Data Ingestion", page_icon="📁")

# Setup shared sidebar
from src.sidebar_config import setup_sidebar
setup_sidebar()

st.markdown("""
<style>
/* Secondary buttons - red */
button[kind="secondary"] {
    background-color: red !important;
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
    color: Red !important;
    width: 100px !important;
    border: none !important;
}

.stButton > button {
    white-space: nowrap !important;
}
</style>
""", unsafe_allow_html=True)
st.title("📁 Data Ingestion")
st.markdown("Upload and manage your video datasets for marine litter detection.")
# Navigation buttons
col1, col2, col3 = st.columns([1, 6, 1])

with col3:
    if st.button("Next ▶", type="primary"):
        st.switch_page("pages/3_✏️_Curation.py")
st.markdown('<hr style="margin: 5px 0; border: 1px solid #ddd;">', unsafe_allow_html=True)
# File upload section
st.header("Upload Videos")
uploaded_files = st.file_uploader(
    "Choose video files",
    type=['mp4', 'avi', 'mov', 'mkv', 'tls'],
    accept_multiple_files=True
)

if uploaded_files:
    st.success(f"Uploaded {len(uploaded_files)} video(s)")
    
    # Create data directory if it doesn't exist
    data_dir = Path("data/videos")
    data_dir.mkdir(parents=True, exist_ok=True)
    
    # Save uploaded files and extract metadata
    metadata_dir = Path("data/metadata")
    metadata_dir.mkdir(parents=True, exist_ok=True)
    
    for uploaded_file in uploaded_files:
        original_file_path = data_dir / uploaded_file.name
        with open(original_file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        # Convert to MP4 if not already MP4
        file_ext = original_file_path.suffix.lower()
        if file_ext != '.mp4':
            mp4_file_path = data_dir / f"{original_file_path.stem}.mp4"
            
            # Convert using OpenCV
            cap_read = cv2.VideoCapture(str(original_file_path))
            fps = cap_read.get(cv2.CAP_PROP_FPS)
            width = int(cap_read.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap_read.get(cv2.CAP_PROP_FRAME_HEIGHT))
            
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(str(mp4_file_path), fourcc, fps, (width, height))
            
            while True:
                ret, frame = cap_read.read()
                if not ret:
                    break
                out.write(frame)
            
            cap_read.release()
            out.release()
            
            # Remove original file and use MP4 version
            original_file_path.unlink()
            file_path = mp4_file_path
            st.write(f"🔄 Converted {uploaded_file.name} to MP4 format")
        else:
            file_path = original_file_path
        
        # Extract video metadata
        try:
            cap = cv2.VideoCapture(str(file_path))
            
            # Get video properties
            fps = cap.get(cv2.CAP_PROP_FPS)
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            duration = frame_count / fps if fps > 0 else 0
            
            # Get file info
            file_size = file_path.stat().st_size
            file_ext = file_path.suffix.lower()
            creation_time = datetime.fromtimestamp(file_path.stat().st_ctime)
            
            # Create metadata dictionary
            metadata = {
                "filename": file_path.name,
                "original_filename": uploaded_file.name,
                "file_size_bytes": file_size,
                "file_size_mb": round(file_size / (1024*1024), 2),
                "file_type": ".mp4",
                "original_format": file_ext,
                "duration_seconds": round(duration, 2),
                "duration_formatted": f"{int(duration//60):02d}:{int(duration%60):02d}",
                "fps": round(fps, 2),
                "frame_count": frame_count,
                "resolution": f"{width}x{height}",
                "width": width,
                "height": height,
                "creation_time": creation_time.isoformat(),
                "ingestion_time": datetime.now().isoformat(),
                "scenario": "marine_litter_detection",
                "format_details": {
                    "codec": "unknown",  # OpenCV doesn't easily provide codec info
                    "bitrate": "unknown"
                }
            }
            
            cap.release()
            
            # Save metadata to JSON file
            metadata_file = metadata_dir / f"{file_path.stem}_metadata.json"
            with open(metadata_file, 'w') as f:
                json.dump(metadata, f, indent=2)
            
            st.write(f"✅ Saved: {file_path.name} ({metadata['duration_formatted']}, {metadata['resolution']})")
            
        except Exception as e:
            st.write(f"✅ Saved: {file_path.name} (metadata extraction failed: {str(e)})")
st.markdown('<hr style="margin: 5px 0; border: 1px solid #ddd;">', unsafe_allow_html=True)
# Display existing videos with metadata
st.header("Existing Videos")
data_dir = Path("data/videos")
metadata_dir = Path("data/metadata")

if data_dir.exists():
    video_files = list(data_dir.glob("*.mp4")) + list(data_dir.glob("*.avi")) + list(data_dir.glob("*.mov")) + list(data_dir.glob("*.mkv")) + list(data_dir.glob("*.tls"))
    video_files.sort(key=lambda x: x.name.lower())
    
    if video_files:
        for video_file in video_files:
            col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
            
            # Load metadata if available
            metadata_file = metadata_dir / f"{video_file.stem}_metadata.json"
            metadata = None
            if metadata_file.exists():
                try:
                    with open(metadata_file, 'r') as f:
                        metadata = json.load(f)
                except:
                    pass
            
            with col1:
                if metadata:
                    st.write(f"📹 {video_file.name}")
                    st.caption(f"{metadata['resolution']} • {metadata['duration_formatted']}")
                else:
                    st.write(f"📹 {video_file.name}")
            
            with col2:
                if metadata:
                    st.write(f"{metadata['file_size_mb']} MB")
                else:
                    file_size = video_file.stat().st_size / (1024*1024)
                    st.write(f"{file_size:.1f} MB")
            
            with col3:
                if metadata:
                    with st.expander("📊 Info"):
                        st.json(metadata)
            
            with col4:
                if st.button("🗑️ Delete", key=f"del_{video_file.name}", type="tertiary"):
                    video_file.unlink()
                    # Also delete metadata file
                    if metadata_file.exists():
                        metadata_file.unlink()
                    st.rerun()
    else:
        st.info("No videos uploaded yet. Use the upload section above to add videos.")
else:
    st.info("No videos uploaded yet. Use the upload section above to add videos.")