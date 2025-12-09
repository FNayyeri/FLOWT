import streamlit as st
import os
import json
import cv2
from pathlib import Path
from datetime import datetime
from src import utils

st.set_page_config(page_title="Data Ingestion", page_icon="📁")

# Setup shared sidebar
from src.sidebar_config import setup_sidebar
setup_sidebar()
# .stApp {
#         background-color: #F5FAFF;  /* very light blue */
#     }  
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
    width: 150px !important;
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

/* White background for all selectboxes */
.stSelectbox > div > div {
    background-color: white !important;
}
</style>
""", unsafe_allow_html=True)
st.title("📁 Data Ingestion")
st.markdown("Upload and manage your video and image datasets for marine litter detection.")
# Navigation buttons in gray row

left_col, spacer_col, right_col = st.columns([0.1, 1, 0.1])
with right_col:
    if st.button("Next ▶", key="nav_next", type="primary"):
        st.switch_page("pages/2_Scanning.py")
st.markdown('<hr style="margin: 5px 0; border: 1px solid #ddd;">', unsafe_allow_html=True)
# File upload section
st.header("Upload Media Files")

# Tabs for different upload types
tab1, tab2 = st.tabs(["📹 Videos", "🖼️ Images"])

with tab1:
    uploaded_videos = st.file_uploader(
        "Choose video files",
        type=['mp4', 'avi', 'mov', 'mkv', 'tls'],
        accept_multiple_files=True,
        key="video_uploader"
    )

with tab2:
    st.info("This feature is currently not available!")
    uploaded_images = None
    # uploaded_images = st.file_uploader(
    #     "Choose image files",
    #     type=['jpg', 'jpeg', 'png', 'bmp', 'tiff'],
    #     accept_multiple_files=True,
    #     key="image_uploader"
    # )

uploaded_files = (uploaded_videos or []) + (uploaded_images or [])

if uploaded_files:
    video_count = len(uploaded_videos or [])
    image_count = len(uploaded_images or [])
    if video_count and image_count:
        st.success(f"Uploaded {video_count} video(s) and {image_count} image(s)")
    elif video_count:
        st.success(f"Uploaded {video_count} video(s)")
    else:
        st.success(f"Uploaded {image_count} image(s)")
    
    # Create data directories if they don't exist
    videos_dir = Path("data/videos")
    images_dir = Path("data/images")
    videos_dir.mkdir(parents=True, exist_ok=True)
    images_dir.mkdir(parents=True, exist_ok=True)
    
    # Save uploaded files and extract metadata
    metadata_dir = Path("data/metadata")
    metadata_dir.mkdir(parents=True, exist_ok=True)
    
    for uploaded_file in uploaded_files:
        # Determine if it's an image or video
        file_ext = Path(uploaded_file.name).suffix.lower()
        is_image = file_ext in ['.jpg', '.jpeg', '.png', '.bmp', '.tiff']
        
        # Save to appropriate directory
        data_dir = images_dir if is_image else videos_dir
        original_file_path = data_dir / uploaded_file.name
        with open(original_file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        # Convert videos to MP4 if not already MP4 (keep images as-is)
        if not is_image:
            file_path = utils.load_video(original_file_path, data_dir)
            if file_path != original_file_path:
                st.write(f"🔄 Converted {uploaded_file.name} to MP4 format")
        else:
            file_path = original_file_path
        
        # Extract metadata (video or image)
        try:
            metadata = utils.extract_metadata(file_path, uploaded_file.name, is_image)
            
            if is_image:
                st.write(f"✅ Saved: {file_path.name} ({metadata['resolution']})")
            else:
                st.write(f"✅ Saved: {file_path.name} ({metadata['duration_formatted']}, {metadata['resolution']})")
            
            # Save metadata to JSON file
            metadata_file = metadata_dir / f"{file_path.stem}_metadata.json"
            with open(metadata_file, 'w') as f:
                json.dump(metadata, f, indent=2)
            
        except Exception as e:
            st.write(f"✅ Saved: {file_path.name} (metadata extraction failed: {str(e)})")
st.markdown('<hr style="margin: 5px 0; border: 1px solid #ddd;">', unsafe_allow_html=True)
# Display existing media files with metadata
st.header("Existing Media Files")
videos_dir = Path("data/videos")
images_dir = Path("data/images")
metadata_dir = Path("data/metadata")

# Combine videos and images
media_files = []
if videos_dir.exists():
    video_files = list(videos_dir.glob("*.mp4")) + list(videos_dir.glob("*.avi")) + list(videos_dir.glob("*.mov")) + list(videos_dir.glob("*.mkv")) + list(videos_dir.glob("*.tls"))
    media_files.extend(video_files)
if images_dir.exists():
    image_files = list(images_dir.glob("*.jpg")) + list(images_dir.glob("*.jpeg")) + list(images_dir.glob("*.png")) + list(images_dir.glob("*.bmp")) + list(images_dir.glob("*.tiff"))
    media_files.extend(image_files)

media_files.sort(key=lambda x: x.name.lower())
    
if media_files:
    for media_file in media_files:
        col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
        
        # Load metadata if available
        metadata_file = metadata_dir / f"{media_file.stem}_metadata.json"
        metadata = None
        if metadata_file.exists():
            try:
                with open(metadata_file, 'r') as f:
                    metadata = json.load(f)
            except:
                pass
        
        with col1:
            if metadata:
                icon = "📹" if metadata.get('media_type') == 'video' else "🖼️"
                st.write(f"{icon} {media_file.name}")
                if metadata.get('media_type') == 'video':
                    st.caption(f"{metadata['resolution']} • {metadata['duration_formatted']}")
                else:
                    st.caption(f"{metadata['resolution']}")
            else:
                icon = "📹" if media_file.suffix.lower() in ['.mp4', '.avi', '.mov', '.mkv', '.tls'] else "🖼️"
                st.write(f"{icon} {media_file.name}")
        
        with col2:
            if metadata:
                st.write(f"{metadata['file_size_mb']} MB")
            else:
                file_size = media_file.stat().st_size / (1024*1024)
                st.write(f"{file_size:.1f} MB")
        
        with col3:
            if metadata:
                with st.expander("📊 Info"):
                    st.json(metadata)
        
        with col4:
            if st.button("🗑️ Delete", key=f"del_{media_file.name}", type="tertiary"):
                media_file.unlink()
                # Also delete metadata file
                if metadata_file.exists():
                    metadata_file.unlink()
                st.rerun()
else:
    st.info("No media files uploaded yet. Use the upload section above to add videos or images.")
