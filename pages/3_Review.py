import streamlit as st
from pathlib import Path
import sys
import json
sys.path.append(str(Path(__file__).parent.parent))
from src.curation_manager import CurationManager
from src.frame_updater import FrameUpdater
from src import curation_manager as curation_module

st.set_page_config(page_title="Review", page_icon="✏️")

# Setup shared sidebar
from src.sidebar_config import setup_sidebar
setup_sidebar()

# Custom CSS for button styling
st.markdown("""
<style>
.stContainer > div[role="list"] {
        background-color: white !important;
        padding: 16px;
        border-radius: 8px;
        margin: 10px 0;
    }            
/* Secondary buttons - red */
button[kind="secondary"] {
    background-color: white !important;
    color: Red !important;
    width: 40px !important;
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
    width: 150px !important;
    border: 1px solid #ccc !important;
}

.stButton > button {
    white-space: nowrap !important;
}

/* White background for all inputs */
div[data-baseweb="input"] > div {
        background-color: white !important;
    }
/* White background for all selectboxes */
    div[data-baseweb="select"] > div {
        background-color: white !important;
    }
/* --- TAB CONTAINER --- */
    /* Make the whole tab container stretch across the page */
    div[data-baseweb="tab-list"] {
        display: flex;
        justify-content: space-between;
        width: 100%;
        background-color: #f8f9fa;  /* Dark background for the tab bar */
        padding: 10px;
        border-radius: 8px;
        margin-bottom: 20px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }

    /* --- INDIVIDUAL TABS --- */
    /* Make each tab take equal space */
    div[data-baseweb="tab"] {
        flex: 1 !important;
        text-align: center;
    }

    /* Default state of tab buttons */
    div[data-baseweb="tab"] > button {
        width: 100%;
        background-color: #8CD2FB;  
        color: #fff !important;
        border-radius: 8px;
        padding: 10px;
        font-weight: 500;
        border: none;
        transition: all 0.3s ease;
    }

    /* Hover effect: Blue background and white text */
    div[data-baseweb="tab"] > button:hover {
        background-color: #007BFF !important;
        color: white !important;
    }

    /* Active tab style */
    div[data-baseweb="tab"][aria-selected="true"] > button {
        background-color: #0056b3 !important;
        color: white !important;
        font-weight: bold;
    }

</style>
""", unsafe_allow_html=True)
st.title("✏️ Review")
st.markdown("Review and correct detection results to improve accuracy.")

left_col, spacer_col, right_col = st.columns([0.1, 1, 0.1])
with left_col:
    if st.button("◀ Previous", key="nav_prev", type="primary"):
        st.switch_page("pages/2_Scanning.py")
with right_col:
    if st.button("Next ▶", key="nav_next", type="primary"):
        st.switch_page("pages/4_Tracking.py")

st.markdown('<hr style="margin: 5px 0; border: 1px solid #ddd;">', unsafe_allow_html=True)

# Model and results selection
results_dir = Path("data/results")
selected_model = None
curation_manager = None
frame_updater = None
result_files = []

if results_dir.exists():
    model_dirs = [d for d in results_dir.iterdir() if d.is_dir()]
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if model_dirs:
            model_names = [d.name for d in model_dirs]
            nav_model = st.session_state.get('nav_model', '')
            nav_model_name = Path(nav_model).stem if nav_model else ''
            default_model = nav_model_name if nav_model_name in model_names else (model_names[0] if model_names else "")
            
            selected_model = st.selectbox(
                "Select Model",
                model_names,
                index=model_names.index(default_model) if default_model in model_names else 0
            )
            
            st.session_state.nav_model = f"models/{selected_model}.pt"
            curation_manager = CurationManager(selected_model)
            frame_updater = FrameUpdater()
            
            model_results_dir = results_dir / selected_model
            result_files = list(model_results_dir.glob("*.json"))
        else:
            st.warning("No models found. Please run inference first.")
            
    with col2:
        if result_files:
            col_mediaType, col_mediaSelect = st.columns([1,3])
            with col_mediaType:
                # media_type = st.radio("Select Media Type", ["Video", "Image"], horizontal=True)
                media_type = st.radio("Select Media Type", ["Video"], horizontal=True)
                # media_type = "Image"
            with col_mediaSelect:
                if media_type == "Video":
                    videos_dir = Path("data/videos")
                    video_files = []
                    if videos_dir.exists():
                        video_files = list(videos_dir.glob("*.mp4")) + list(videos_dir.glob("*.avi")) + list(videos_dir.glob("*.mov")) + list(videos_dir.glob("*.mkv")) + list(videos_dir.glob("*.tls"))
                    
                    filtered_files = [r for r in result_files if any(v.stem == r.stem.replace('_detections', '') for v in video_files)]
                    media_names = sorted([r.stem.replace('_detections', '') + '.mp4' for r in filtered_files])
                else:
                    images_dir = Path("data/images")
                    image_files = []
                    if images_dir.exists():
                        image_files = list(images_dir.glob("*.jpg")) + list(images_dir.glob("*.jpeg")) + list(images_dir.glob("*.png")) + list(images_dir.glob("*.bmp")) + list(images_dir.glob("*.tiff"))
                    
                    filtered_files = [r for r in result_files if any(i.stem == r.stem.replace('_detections', '') for i in image_files)]
                    media_names = sorted([r.stem.replace('_detections', '') + i.suffix for r in filtered_files for i in image_files if i.stem == r.stem.replace('_detections', '')])
            
                if media_names:
                    if 'media_selection' not in st.session_state:
                        nav_video = st.session_state.get('nav_video', '')
                        if nav_video:
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
                        for ext in ['.mp4', '.jpg', '.jpeg', '.png', '.bmp', '.tiff']:
                            if selected.endswith(ext):
                                st.session_state.nav_video = selected.replace(ext, '')
                                break
                        else:
                            st.session_state.nav_video = selected
                    
                    selected_video = st.selectbox(
                        "Select Media File",
                        media_names,
                        key="media_selection",
                        on_change=update_nav_media
                    )
                else:
                    st.warning(f"No {media_type.lower()} files with detection results found.")
                    selected_video = None
            
            if selected_video:
                for ext in ['.mp4', '.jpg', '.jpeg', '.png', '.bmp', '.tiff']:
                    if selected_video.endswith(ext):
                        selected_result = selected_video.replace(ext, '') + '_detections'
                        break
                else:
                    selected_result = selected_video + '_detections'
            else:
                selected_result = None
        else:
            st.warning("No models found. Please run inference first.")
    
    with col3:
        if result_files and selected_result and selected_video:
            curated_file = f"data/curated/{selected_model}/{selected_result.replace('_detections', '_curated_detections')}.json"
            if not Path(curated_file).exists():
                Path(curated_file).parent.mkdir(parents=True, exist_ok=True)
                original_detections = curation_manager.load_detections(f"data/results/{selected_model}/{selected_result}.json")
                for detection in original_detections:
                    detection['corrected_class'] = detection.get('class', 'Unknown')
                with open(curated_file, 'w') as f:
                    json.dump(original_detections, f, indent=2)
            
            all_detections = curation_manager.load_detections(curated_file)
            curations = all_detections
            available_classes = sorted(list(set([d.get('corrected_class', 'Unknown') for d in all_detections])))
            class_options = ["All Classes"] + available_classes
            
            col3_sel, col3_dets = st.columns([2,1])
            with col3_sel:
                selected_class_filter = st.selectbox(
                    "Filter by Class",
                    class_options,
                    key="class_filter"
                )
            with col3_dets:
                if st.session_state.get('class_filter', 'All Classes') != 'All Classes':
                    curations = [d for d in all_detections if d.get('corrected_class', d.get('class', 'Unknown')) == st.session_state.class_filter]
                else:
                    curations = all_detections
                filtered_count = len(curations)
                st.metric("Total Detections", filtered_count)

    if result_files and selected_result and selected_video and curations:
        col1, col2 = st.columns(2)
        with col1:
            items_per_page = st.selectbox("Items per page", [10, 20, 30], index=2)
        
        columns_per_row = min(3, items_per_page // 10) if items_per_page >= 10 else 1
        total_items = len(curations)
        total_pages = max(1, (total_items - 1) // items_per_page + 1) if total_items > 0 else 1
        
        if 'current_page' not in st.session_state or st.session_state.current_page > total_pages:
            st.session_state.current_page = 1
        page = st.session_state.current_page - 1
        start_idx = page * items_per_page
        end_idx = min(start_idx + items_per_page, total_items)
        with col2:
            page_input = st.number_input("Page", 1, total_pages, st.session_state.current_page, key="page_input")
            if page_input != st.session_state.current_page:
                st.session_state.current_page = page_input
                st.rerun()
        col1, col2, col3 = st.columns([1,1,1])
        with col1:
            if st.button("Mark All Valid", type="tertiary"):
                curation_module.bulk_mark_tp(curations, curated_file, all_detections, start_idx, end_idx)                
                st.rerun()
        
        with col2:
            if st.button("Mark All Invalid", type="tertiary"):
                curation_module.bulk_mark_fp(curations, curated_file, all_detections, start_idx, end_idx)
                st.rerun()
        
        with col3:
            if st.button("💾 Save Changes", type="tertiary"):
                curation_manager.save_all_changes(curated_file)
                st.success("Changes saved successfully!")
                st.rerun()
        
        
        tab1, tab2, _ = st.tabs(["📊 Table Review", "📋 Visual Review"," "])
        
        with tab2:
            col1, col2 = st.columns(2)
            with col1:
                if st.button("View All Large", type="tertiary"):
                    for i in range(len(curations)):
                        st.session_state[f"view_large_{i}"] = True
                    st.rerun()
            
            with col2:
                if st.button("View All Small", type="tertiary"):
                    for i in range(len(curations)):
                        st.session_state[f"view_large_{i}"] = False
                    st.rerun()
            
            for row_start in range(start_idx, end_idx, columns_per_row):
                row_end = min(row_start + columns_per_row, end_idx)
                cols = st.columns(columns_per_row)
                
                for col_idx, i in enumerate(range(row_start, row_end)):
                    curation = curations[i]
                    
                    with cols[col_idx]:
                        is_curated = curation.get('corrected_class') != curation.get('class')
                        status_icon = "✅" if is_curated else "🔄"
                        
                        col_frame, col_score, col_valid = st.columns([1, 1, 1])
                        with col_frame:
                            st.markdown(f"{status_icon} **#{i+1}** | Frame: {curation.get('frame', 'N/A')}")
                        with col_score:
                            st.markdown(f"Score: {curation.get('confidence', 0):.2f}")
                        with col_valid:
                            is_true_positive = st.checkbox("✓ Valid", value=curation.get('is_true_positive', True), key=f"tp_{i}")
                        
                        if is_true_positive != curation.get('is_true_positive', True):
                            curation_manager.update_validity(i, is_true_positive, curated_file)

                        if is_true_positive:
                            from src.bbox_drawer import BBoxDrawer
                            bbox_drawer = BBoxDrawer()
                            
                            current_class = curation.get('corrected_class', curation.get('class', 'Packaging'))
                            
                            try:
                                default_idx = bbox_drawer.class_names.index(current_class)
                            except ValueError:
                                default_idx = 0
                            col_1, col_2, col_3 = st.columns([2, 0.4, 2])
                            with col_1:
                                st.markdown("**Class:**")
                            with col_3:
                                st.markdown("**Tags:**")
                            col_select, col_color, col_tag_select = st.columns([2, 0.4, 2])
                            with col_select:
                                new_class = st.selectbox("Class", bbox_drawer.class_names, index=default_idx, key=f"class_{i}", label_visibility="collapsed")
                            with col_color:
                                selected_color_hex = bbox_drawer.get_class_color_hex(new_class)
                                st.markdown(f"<div style='display:inline-block; width:40px; height:20px; background-color:{selected_color_hex}; border:1px solid #ccc; border-radius:3px; vertical-align:middle; margin-top:8px;'></div>", unsafe_allow_html=True)
                            with col_tag_select:
                                current_tags = curation.get('tags', [])
                                tags = st.multiselect("Tags", ["floating", "submerged", "large", "small", "degraded"], default=current_tags, key=f"tags_{i}", label_visibility="collapsed")
                        
                            if new_class != current_class:
                                curation_manager.edit_classification(i, new_class, curated_file)
                            if tags != curation.get('tags', []):
                                curation_manager.add_tags(i, tags, curated_file)
                                # Update frame image with new class color and detection ID
                                frame_image_path = curation.get('frame_image')
                                if frame_image_path:
                                    frame_updater.update_frame_with_detection_id(f"data/{frame_image_path}", curation, new_class, i+1)
                        
                        frame_image_path = curation.get('frame_image')
                        if frame_image_path and Path(f"data/{frame_image_path}").exists():
                            frame_image = f"data/{frame_image_path}"
                            

                            st.image(f"data/{frame_image_path}", width=200)
                                
                            view_key = f"view_large_{i}"
                            if view_key not in st.session_state:
                                st.session_state[view_key] = False
                            
                            if not st.session_state[view_key]:
                                if st.button("🔍 View Large", key=f"view_{i}", type="tertiary"):
                                    st.session_state[view_key] = True
                                    st.rerun()
                            else:
                                if st.button("❌ Close", key=f"close_{i}", type="tertiary"):
                                    st.session_state[view_key] = False
                                    st.rerun()
                                st.image(f"data/{frame_image_path}", caption=f"Detection {i+1} - Frame {curation.get('frame', 'N/A')}")
                        elif frame_image_path:
                            st.info(f"Image not found: {frame_image_path}")
                        else:
                            st.info("No image path available")
        
        with tab1:
            if curations:
                from src.bbox_drawer import BBoxDrawer
                bbox_drawer = BBoxDrawer()
                tags_list = ["floating", "submerged", "large", "small", "degraded"]
                
                _, col_middle, _ = st.columns([1,4,1])
                with col_middle:
                    col_id, col_frame, col_class, col_conf, col_valid, col_tags = st.columns([0.5, 0.8, 1.5, 0.8, 0.8, 2])

                    with col_id:
                        st.markdown("<div style='display: flex; justify-content: center;'><b>ID</b></div>", unsafe_allow_html=True)
                    with col_frame:
                        st.markdown("<div style='text-align: center;'><b>Frame</b></div>", unsafe_allow_html=True)
                    with col_class:
                        st.markdown("**Class**")
                    with col_conf:
                        st.markdown("<div style='text-align: center;'><b>Confidence</b></div>", unsafe_allow_html=True)
                    with col_valid:
                        st.markdown("**Valid**")
                    with col_tags:
                        st.markdown("**Tags**")
                    st.markdown('<hr style="margin: 5px 0; border: 1px solid #ddd;">', unsafe_allow_html=True)
                    
                    for i, curation in enumerate(curations[start_idx:end_idx], start=start_idx):
                        col_id, col_frame, col_class, col_conf, col_valid, col_tags = st.columns([0.5, 0.8, 1.5, 0.8, 0.8, 2])
                        
                        with col_id:
                            st.markdown(f"<div style='text-align: center;'>{i + 1}</div>", unsafe_allow_html=True)
                        with col_frame:
                            st.markdown(f"<div style='text-align: center;'>{curation.get('frame', 'N/A')}</div>", unsafe_allow_html=True)
                        with col_class:
                            new_class = st.selectbox(
                                "Class", 
                                bbox_drawer.class_names, 
                                index=bbox_drawer.class_names.index(curation.get('corrected_class', curation.get('class', 'Packaging'))) if curation.get('corrected_class', curation.get('class', 'Packaging')) in bbox_drawer.class_names else 0,
                                key=f"table_class_{i}",
                                label_visibility="collapsed"
                            )
                        with col_conf:
                            st.markdown(f"<div style='text-align: center;'>{curation.get('confidence', 0):.2f}</div>", unsafe_allow_html=True)
                        with col_valid:
                            is_valid = st.checkbox(
                                "Valid", 
                                value=curation.get('is_true_positive', True), 
                                key=f"table_valid_{i}",
                                label_visibility="collapsed"
                            )
                        with col_tags:
                            current_tags = curation.get('tags', [])
                            new_tags = st.multiselect(
                                "Tags", 
                                tags_list, 
                                default=current_tags, 
                                key=f"table_tags_{i}",
                                label_visibility="collapsed"
                            )
                        # frame_updater.update_frame_with_detection_id(f"data/{frame_image_path}", curation, new_class, i+1)
                        if new_class != curation.get('corrected_class', curation.get('class')):
                            curation_manager.edit_classification(i, new_class, curated_file)
                        if is_valid != curation.get('is_true_positive', True):
                            curation_manager.update_validity(i, is_valid, curated_file)
                        if new_tags != curation.get('tags', []):
                            curation_manager.add_tags(i, new_tags, curated_file)
                            # Update frame image with new class color and detection ID
                            frame_image_path = curation.get('frame_image')
                            if frame_image_path and new_class != curation.get('corrected_class', curation.get('class')):
                                frame_updater.update_frame_with_detection_id(f"data/{frame_image_path}", curation, new_class, i+1)
            else:
                st.info("No detections to display in table.")
        
    else:
        st.info("No detections to display. Please select a media file with detection results.")
else:
    st.warning("No detection results found for this model. Please run inference first.")