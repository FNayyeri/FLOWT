import streamlit as st
from pathlib import Path
import sys
import yaml
sys.path.append(str(Path(__file__).parent.parent))
from src.video_generator import VideoGenerator

st.set_page_config(page_title="Video Generation", page_icon="🎬")

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
    border: none !important;
}

.stButton > button {
    white-space: nowrap !important;
}
</style>
""", unsafe_allow_html=True)
st.title("🎬 Video Generation")
st.markdown("Generate new videos with corrected detections replacing original ones.")

# Debug: Show current session state
# st.write(f"Debug - nav_video: {st.session_state.get('nav_video', 'Not set')}")

# Navigation buttons
col1, col2, col3 = st.columns([1, 6, 1])
with col1:
    if st.button("◀ Previous", type="primary"):
        st.switch_page("pages/4_🎯_Tracking.py")
with col3:
    if st.button("Next ▶", type="primary"):
        st.switch_page("pages/6_📊_Analysis.py")
st.markdown('<hr style="margin: 5px 0; border: 1px solid #ddd;">', unsafe_allow_html=True)
# Initialize video generator
@st.cache_resource
def load_video_generator():
    return VideoGenerator()

video_gen = load_video_generator()

data_dir = Path("data/videos")
if data_dir.exists():
    video_files = list(data_dir.glob("*.mp4")) + list(data_dir.glob("*.avi")) + list(data_dir.glob("*.mov")) + list(data_dir.glob("*.mkv")) + list(data_dir.glob("*.tls"))   
    if video_files:
        # Model and output configuration in one row
        st.header("Configuration")
        tracking_base_dir = Path("data/tracking")
        if tracking_base_dir.exists():
            model_dirs = [d for d in tracking_base_dir.iterdir() if d.is_dir()]
            
            if model_dirs:
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    # Use nav_model if available
                    model_names = [d.name for d in model_dirs]
                    nav_model = st.session_state.get('nav_model', '')
                    # Extract model name from path if nav_model is a full path
                    nav_model_name = Path(nav_model).stem if nav_model else ''
                    default_model = nav_model_name if nav_model_name in model_names else (model_names[0] if model_names else "")
                    
                    selected_model = st.selectbox(
                        "Select Model",
                        model_names,
                        index=model_names.index(default_model) if default_model in model_names else 0
                    )
                    
                    # Update nav_model to match current selection
                    st.session_state.nav_model = f"models/{selected_model}.pt"
                
                with col2:
                    # Use nav_video if available (add .mp4 extension if missing)
                    video_names = sorted([v.name for v in video_files])
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
                with col3:
                    output_format = st.selectbox(
                        "Output Format",
                        ["mp4", "avi", "mov"]
                    )
                
                with col4:
                    quality = st.selectbox(
                        "Video Quality",
                        ["High", "Medium", "Low"],
                        index=1
                    )
                
                # Auto-select tracking data based on video name
                model_tracking_dir = tracking_base_dir / selected_model
                tracking_files = list(model_tracking_dir.glob("*_tracking.json"))
                
                video_name_without_ext = Path(selected_video).stem
                matching_tracking = f"{video_name_without_ext}_tracking"
                
                tracking_options = [t.stem for t in tracking_files]
                default_index = 0
                if matching_tracking in tracking_options:
                    default_index = tracking_options.index(matching_tracking)
                
                if tracking_files and default_index < len(tracking_options):
                    selected_tracking = tracking_options[default_index]
            else:
                tracking_files = []
            st.markdown('<hr style="margin: 5px 0; border: 1px solid #ddd;">', unsafe_allow_html=True)
            if tracking_files:
                
                # Generation options
                st.header("Generation Options")
                col1, col2 = st.columns(2)
                
                with col1:
                    show_bboxes = st.checkbox("Show Bounding Boxes", value=True)
                    show_labels = st.checkbox("Show Class Labels", value=True, disabled=not show_bboxes)
                    show_confidence = st.checkbox("Show Confidence Scores", value=True, disabled=not show_bboxes)
                
                with col2:
                    # col_bboxcolor, col_textcolor, col_thickness, _, _ = st.columns(5)
                    # Load current values from config
                    config_path = Path(__file__).parent.parent / "config" / "config.yaml"
                    with open(config_path, 'r') as f:
                        config = yaml.safe_load(f)
                    
                    current_bbox_color = config.get('video_generation', {}).get('bbox_color', '#FF0000')
                    current_text_color = config.get('video_generation', {}).get('text_color', '#FFFFFF')
                    current_thickness = config.get('video_generation', {}).get('bbox_thickness', 2)

                    col_bboxcolor, col_bboxcolor_set= st.columns([1,5])
                    with col_bboxcolor:
                        st.markdown("Bounding Box Color")
                    with col_bboxcolor_set:
                        bbox_color = st.color_picker("Bounding Box Color", current_bbox_color, disabled=show_labels, label_visibility="collapsed")
                    

                    col_textcolor, col_textcolor_set= st.columns([1,5])
                    with col_textcolor:
                        st.markdown("Text Color")
                    with col_textcolor_set:
                        text_color = st.color_picker("Text Color", current_text_color, label_visibility="collapsed")
                    
                    col_thickness, col_thickness_set= st.columns([1,5])
                    with col_thickness:
                        st.markdown("Box Thickness")
                    with col_thickness_set:
                        bbox_thickness = st.slider("Box Thickness", 1, 5, current_thickness, label_visibility="collapsed")
                    
                    # Save changes to config if values changed
                    if (bbox_color != current_bbox_color or 
                        text_color != current_text_color or 
                        bbox_thickness != current_thickness):
                        
                        config['video_generation']['bbox_color'] = bbox_color
                        config['video_generation']['text_color'] = text_color
                        config['video_generation']['bbox_thickness'] = bbox_thickness
                        
                        with open(config_path, 'w') as f:
                            yaml.dump(config, f, default_flow_style=False)
                        
                        st.rerun()
                
                # Use the same video name for output
                video_name_without_ext = Path(selected_video).stem
                output_name = f"{video_name_without_ext}.{output_format}"
                
                # Generate video
                if st.button("Generate Video", type="secondary"):
                    with st.spinner("Generating video with corrected detections..."):
                        try:
                            video_path = data_dir / selected_video
                            tracking_path = model_tracking_dir / f"{selected_tracking}.json"
                            
                            # Remove extension from output_name since generator adds it
                            output_name_no_ext = Path(output_name).stem
                            
                            output_path = video_gen.generate_video_from_tracking(
                                video_path=video_path,
                                tracking_data_path=tracking_path,
                                output_name=output_name_no_ext,
                                output_format=output_format,
                                model_name=selected_model,
                                options={
                                    'show_bboxes': show_bboxes,
                                    'show_labels': show_labels,
                                    'show_confidence': show_confidence,
                                    'bbox_color': bbox_color,
                                    'text_color': text_color,
                                    'bbox_thickness': bbox_thickness,
                                    'quality': quality
                                }
                            )
                            
                            st.success(f"Video generated successfully: {output_path}")
                            
                            # Show download button
                            with open(output_path, "rb") as file:
                                st.download_button(
                                    "📥 Download Generated Video",
                                    file.read(),
                                    file_name=output_name,
                                    mime="video/mp4"
                                , type="tertiary")
                                
                        except Exception as e:
                            st.error(f"Video generation failed: {str(e)}")
            else:
                st.warning("No tracking data found for this model. Please run tracking first.")
        else:
            st.warning("No models with tracking data found.")
    else:
        st.warning("No videos found. Please upload videos first.")
else:
    st.warning("Tracking data directory not found. Please run tracking first.")
st.markdown('<hr style="margin: 5px 0; border: 1px solid #ddd;">', unsafe_allow_html=True)
# Generated videos list
st.header("Generated Videos")
output_base_dir = Path("data/output")
if output_base_dir.exists():
    for model_dir in output_base_dir.iterdir():
        if model_dir.is_dir():
            st.subheader(f"Model: {model_dir.name}")
            output_videos = list(model_dir.glob("*.mp4")) + list(model_dir.glob("*.avi")) + list(model_dir.glob("*.mov")) + list(model_dir.glob("*.mkv")) + list(model_dir.glob("*.tls"))
            
            if output_videos:
                for video in output_videos:
                    col1, col2, col3 = st.columns([3, 1, 1])
                    with col1:
                        st.write(f"🎬 {video.name}")
                    with col2:
                        file_size = video.stat().st_size / (1024*1024)  # MB
                        st.write(f"{file_size:.1f} MB")
                    with col3:
                        with open(video, "rb") as file:
                            st.download_button(
                                "📥 Download",
                                file.read(),
                                file_name=video.name,
                                mime="video/mp4",
                                key=f"download_{model_dir.name}_{video.name}", 
                                type="tertiary")
            else:
                st.info(f"No generated videos for {model_dir.name} yet.")
else:
    st.info("No generated videos yet.")