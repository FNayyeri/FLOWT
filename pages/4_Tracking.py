import streamlit as st
from pathlib import Path
import sys
import yaml
sys.path.append(str(Path(__file__).parent.parent))
from src.object_tracker import ObjectTracker
import json

st.set_page_config(page_title="Object Tracking", page_icon="🎯")

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
}

/* Tertiary buttons - white */
button[kind="tertiary"] {
    background-color: white !important;
    color: Blue !important;
    width: 100px !important;
    border: 1px solid #ccc !important;
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
st.title("🎯 Object Tracking")
st.markdown("Track curated objects across video frames using template matching.")

# Debug: Show current session state
# st.write(f"Debug - nav_video: {st.session_state.get('nav_video', 'Not set')}")

# Navigation buttons
left_col, spacer_col, right_col = st.columns([0.1, 1, 0.1])
with left_col:
    if st.button("◀ Previous", type="primary"):
        st.switch_page("pages/3_Review.py")
with right_col:
    if st.button("Next ▶",  type="primary"):
        st.switch_page("pages/5_Video_Generation.py")
st.markdown('<hr style="margin: 5px 0; border: 1px solid #ddd;">', unsafe_allow_html=True)
# Configuration
# st.header("🔧 Configuration")
curated_base_dir = Path("data/curated")
if curated_base_dir.exists():
    model_dirs = [d for d in curated_base_dir.iterdir() if d.is_dir()]
    
    if model_dirs:
        videos_dir = Path("data/videos")
        video_files = list(videos_dir.glob("*.mp4")) + list(videos_dir.glob("*.avi")) + list(videos_dir.glob("*.mov")) + list(videos_dir.glob("*.mkv")) + list(videos_dir.glob("*.tls"))
        
        col_model, col_video = st.columns(2)
        
        with col_model:
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
        
        with col_video:
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
        curated_files = list((curated_base_dir / selected_model).glob("*.json"))
        with st.expander("🔧 Configuration", expanded=False):
            col_vidtype, col_info = st.columns([1, 2])
            with col_vidtype:
                # st.markdown("**Video Type:**")
                # Load timelapse setting from config
                config_path = Path(__file__).parent.parent / "config" / "config.yaml"
                with open(config_path, 'r') as f:
                    config = yaml.safe_load(f)
                
                current_timelapse = config.get('tracking', {}).get('timelapse_video', False)
                timelapse_video = st.checkbox("Timelapse Video", value=current_timelapse, help="Check if this is a timelapse video (IoU will be disabled)")
            with col_info:
                # st.markdown("**Video Type Info:**")
                if timelapse_video:
                    st.info("📹 Timelapse mode: IoU threshold disabled, using template matching for tracking only.")
                else:
                    st.info("🎥 Regular video: Using both IoU and template matching for tracking.")
                
                # Save changes to config if value changed
                if timelapse_video != current_timelapse:
                    if 'tracking' not in config:
                        config['tracking'] = {}
                    config['tracking']['timelapse_video'] = timelapse_video
                    
                    with open(config_path, 'w') as f:
                        yaml.dump(config, f, default_flow_style=False)
                    
                    st.rerun()
            
            st.header("Tracking Parameters")
                
            col1, col2, _ = st.columns(3)
            
            with col1:
                iou_threshold = st.slider("IoU Threshold", 0.1, 0.8, 0.3, 0.05, disabled=timelapse_video)
            with col2:
                template_threshold = st.slider("Template Threshold", 0.3, 0.9, 0.5, 0.05)
        
        
        if videos_dir.exists() and curated_files:
            # Auto-select curated data based on video name
            video_name_without_ext = Path(selected_video).stem if selected_video else ""
            matching_curated = f"{video_name_without_ext}_curated_detections"
            
            curated_options = [c.stem for c in curated_files]
            default_index = 0
            if matching_curated in curated_options:
                default_index = curated_options.index(matching_curated)
            
            selected_curated = curated_options[default_index] if curated_options else None
            
            if selected_video and selected_curated:

                # Run tracking
                if st.button("Start Tracking", type="secondary"):
                    with st.spinner("Tracking objects across video frames..."):
                        try:
                            # Initialize tracker
                            tracker = ObjectTracker()
                            tracker.iou_threshold = 0.0 if timelapse_video else iou_threshold
                            tracker.template_threshold = template_threshold
                            
                            # Load curated data
                            curated_path = curated_base_dir / selected_model / f"{selected_curated}.json"
                            with open(curated_path, 'r') as f:
                                curated_detections = json.load(f)
                            
                            # Run tracking
                            video_path = videos_dir / selected_video
                            tracked_objects = tracker.track_objects(video_path, curated_detections)
                            
                            # Get statistics
                            stats = tracker.get_tracking_stats(tracked_objects)
                            
                            # Save tracking results
                            tracking_dir = Path("data/tracking") / selected_model
                            tracking_dir.mkdir(parents=True, exist_ok=True)
                            
                            video_stem = Path(selected_video).stem
                            tracking_file = tracking_dir / f"{video_stem}_tracking.json"
                            
                            tracking_data = {
                                'video': selected_video,
                                'model': selected_model,
                                'curated_data': selected_curated,
                                'parameters': {
                                    'timelapse_video': timelapse_video,
                                    'iou_threshold': 0.0 if timelapse_video else iou_threshold,
                                    'template_threshold': template_threshold
                                },
                                'tracked_objects': tracked_objects,
                                'statistics': stats
                            }
                            
                            with open(tracking_file, 'w') as f:
                                json.dump(tracking_data, f, indent=2)
                            
                            st.success(f"Tracking completed! Results saved to {tracking_file}")
                            
                            # Display results
                            st.header("Tracking Results")
                            
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                st.metric("Total Unique Objects", stats['total_unique_objects'])
                            with col2:
                                st.metric("Total Detections", stats['total_detections'])
                            with col3:
                                st.metric("Object Classes", len(stats['objects_by_class']))
                            
                            # Objects by class
                            st.subheader("Objects by Class")
                            for class_name, count in stats['objects_by_class'].items():
                                st.write(f"**{class_name}**: {count} unique objects")
                            
                        except Exception as e:
                            st.error(f"Tracking failed: {str(e)}")
        else:
            st.warning("No videos or curated data found.")
    else:
        st.warning("No models with curated data found.")
else:
    st.warning("No curated data directory found.")
st.markdown('<hr style="margin: 5px 0; border: 1px solid #ddd;">', unsafe_allow_html=True)
# Display existing tracking results
st.header("Existing Tracking Results")
tracking_base_dir = Path("data/tracking")
if tracking_base_dir.exists():
    for model_dir in tracking_base_dir.iterdir():
        if model_dir.is_dir():
            st.subheader(f"Model: {model_dir.name}")
            tracking_files = list(model_dir.glob("*.json"))
            
            for tracking_file in tracking_files:
                with open(tracking_file, 'r') as f:
                    tracking_data = json.load(f)
                
                col1, col2, col3 = st.columns([2, 1, 1])
                with col1:
                    st.write(f"📹 {tracking_data['video']}")
                with col2:
                    st.write(f"Objects: {tracking_data['statistics']['total_unique_objects']}")
                with col3:
                    if st.button("View Details", key=f"view_{model_dir.name}_{tracking_file.stem}", type="tertiary"):
                        st.json(tracking_data['statistics'])
else:
    st.info("No tracking results yet.")