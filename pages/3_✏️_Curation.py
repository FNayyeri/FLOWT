import streamlit as st
from pathlib import Path
import sys
sys.path.append(str(Path(__file__).parent.parent))
from src.curation_manager import CurationManager
from src.frame_updater import FrameUpdater

st.set_page_config(page_title="Curation", page_icon="✏️")

# Setup shared sidebar
from src.sidebar_config import setup_sidebar
setup_sidebar()

# Custom CSS for button styling
st.markdown("""
<style>
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
    width: 200px !important;
    border: none !important;
}

/* Tertiary buttons - white */
button[kind="tertiary"] {
    background-color: white !important;
    color: Blue !important;
    width: 150px !important;
    border: 1px solid #ccc !important;
}
/* Save buttons using secondary type - small and compact */
button[data-testid*="save_btn_"] {
    background-color: #f0f0f0 !important;
    color: #333 !important;
    width: 40px !important;
    height: 30px !important;
    border: 1px solid #ccc !important;
    font-size: 16px !important;
    padding: 2px !important;
}

.stButton > button {
    white-space: nowrap !important;
}
</style>
""", unsafe_allow_html=True)
st.title("✏️ Curation")
st.markdown("Review and correct detection results to improve accuracy.")

# Debug: Show current session state
# st.write(f"Debug - nav_video: {st.session_state.get('nav_video', 'Not set')}")

# Navigation buttons
col1, col2, col3 = st.columns([1, 6, 1])
with col1:
    if st.button("◀ Previous", key="nav_prev", type="primary"):
        st.switch_page("pages/2_🔍_Inference.py")
with col3:
    if st.button("Next ▶", key="nav_next",  type="primary"):
        st.switch_page("pages/4_🎯_Tracking.py")
st.markdown('<hr style="margin: 5px 0; border: 1px solid #ddd;">', unsafe_allow_html=True)
# Status icons guide
# st.info("""
# **Status Icons Guide:**
# - ⏳ **Pending**: Detection not yet curated 
# - ✅ **Saved**: Detection has been saved to the curated file
# """)

# Model and results selection
results_dir = Path("data/results")
if results_dir.exists():
    model_dirs = [d for d in results_dir.iterdir() if d.is_dir()]
    
    if model_dirs:
        # Three column layout for selection controls
        col1, col2, col3 = st.columns(3)
        
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
        
        # Initialize curation manager after model selection
        curation_manager = CurationManager(selected_model)
        frame_updater = FrameUpdater()
        
        model_results_dir = results_dir / selected_model
        result_files = list(model_results_dir.glob("*.json"))
        
        if result_files:
            with col2:
                # Convert detection files to video names for display
                video_names = sorted([r.stem.replace('_detections', '') + '.mp4' for r in result_files])
                # Initialize video_selection if not exists
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

                # Use nav_video if available (add .mp4 extension if missing)
                # nav_video = st.session_state.get('nav_video', '')
                # if nav_video and not nav_video.endswith('.mp4'):
                #     nav_video = f"{nav_video}.mp4"  # Add .mp4 extension
                # default_video = nav_video if nav_video in video_names else (video_names[0] if video_names else "")
                # # st.write(f"Debug - nav_video: {st.session_state.get('nav_video', '')}, processed: {nav_video}, default_video: {default_video}")
                
                # selected_video = st.selectbox(
                #     "Select Video",
                #     video_names,
                #     index=video_names.index(default_video) if default_video in video_names else 0
                # )
                # # Always update nav_video to match current selection
                # st.session_state.nav_video = selected_video.replace('.mp4', '') if selected_video.endswith('.mp4') else selected_video
                # st.write(f"Debug - Selected video: {selected_video}, nav_video set to: {st.session_state.nav_video}")
                
                # Get the actual result file name for loading
                selected_result = selected_video.replace('.mp4', '') + '_detections'
            
            with col3:
                items_per_page = st.selectbox("Items per page", [10, 20, 30], index=2)
        
            if selected_result:
                # Clear any cached state when loading new detections
                curation_manager.curations = {}
                detections = curation_manager.load_detections(f"data/results/{selected_model}/{selected_result}.json")
                video_name = selected_result.replace('_detections', '')  # Extract video name

                # Pagination settings
                columns_per_row = items_per_page // 10
                
                total_items = len(detections)
                total_pages = (total_items - 1) // items_per_page + 1
                
                # Page navigation with buttons
                col_empty1, col_prev, col_gap1, col_page, col_gap2, col_next, col_empty2 = st.columns([2, 2, 1, 6, 1, 2, 2], gap="small")
                
                # center the Previous button inside its column by nesting columns
                with col_prev:
                    _, center_prev, _ = st.columns([1, 2, 1])
                    with center_prev:
                        if st.button("◀ Previous Page", disabled=(st.session_state.get('current_page', 1) <= 1), key="page_prev", type="tertiary"):
                            st.session_state.current_page = max(1, st.session_state.get('current_page', 1) - 1)
                            st.rerun()

                # the input (use number_input if you want the +/- UI like your screenshot)
                with col_page:
                    if 'current_page' not in st.session_state:
                        st.session_state.current_page = 1
                    
                    page_input = st.number_input("Page", 1, total_pages, st.session_state.current_page, key="page_input", label_visibility="collapsed")
                    if page_input != st.session_state.current_page:
                        st.session_state.current_page = page_input

                # center the Next button as well
                with col_next:
                    _, center_next, _ = st.columns([1, 2, 1])
                    with center_next:
                        # next_clicked = st.button("Next ▶", key="next")
                        if st.button("Next Page▶", disabled=(st.session_state.current_page >= total_pages), key="page_next", type="tertiary"):
                            st.session_state.current_page = min(total_pages, st.session_state.current_page + 1)
                            st.rerun()
                
                
                page = st.session_state.current_page - 1
                start_idx = page * items_per_page
                end_idx = min(start_idx + items_per_page, total_items)
            
                # st.markdown('<hr style="margin: 5px 0; border: 1px solid #ddd;">', unsafe_allow_html=True)
                # Bulk actions
                _, col1, col2, col3, col4 = st.columns([1, 1, 1, 1, 1])
                with col1:
                    if st.button("Mark All True Positive", type="secondary"):
                        curation_manager.bulk_mark_true_positive(start_idx, end_idx)
                        curation_manager.export_curated_data(video_name)
                        st.success("Page detections marked as true positive!")
                with col2:
                    if st.button("Mark All False Positive", type="secondary"):
                        curation_manager.bulk_mark_false_positive(start_idx, end_idx)
                        curation_manager.export_curated_data(video_name)
                        st.success("Page detections marked as false positive!")
                with col3:
                    if st.button("Save All", type="secondary"):
                        # Save all current page detections
                        for i in range(start_idx, end_idx):
                            st.session_state.saved_detections.add(i)
                        curation_manager.export_curated_data(video_name)
                        st.success("All detections saved!")
                        st.rerun()
                with col4:
                    if st.button("Export Curated Data", type="secondary"):
                        exported_file = curation_manager.export_curated_data(video_name)
                        st.success(f"Curated data exported to {exported_file}!")
                        st.rerun()
                st.markdown('<hr style="margin: 5px 0; border: 1px solid #ddd;">', unsafe_allow_html=True)
                # Initialize saved state tracking
                if 'saved_detections' not in st.session_state:
                    st.session_state.saved_detections = set()
                
                # Display detections in a scrollable container
                with st.container():
                    # Group detections by columns
                    for row_start in range(start_idx, end_idx, columns_per_row):
                        row_end = min(row_start + columns_per_row, end_idx)
                        cols = st.columns(columns_per_row)
                        
                        for col_idx, i in enumerate(range(row_start, row_end)):
                            detection = detections[i]
                            
                            with cols[col_idx]:
                                # Compact card layout
                                with st.container():
                                    # Detection info section
                                    with st.container():
                            
                                        # Detection info
                                        # Show curation and save status
                                        curated_class = detection.get('corrected_class', detection.get('class', 'Unknown'))
                                        is_curated = 'corrected_class' in detection or detection.get('is_true_positive') != True
                                        is_saved = i in st.session_state.saved_detections
                                        status_icon = "✅" if is_saved else ("🔄" if is_curated else "⏳")
                                        
                                        col_frame, col_score, col_valid, save_button = st.columns([1, 1, 1, 1])
                                        with col_frame:
                                            st.markdown(f"{status_icon} **#{i+1}** | Frame: {detection.get('frame', 'N/A')}")
                                        with col_score:
                                            # st.markdown(f"**{curated_class}** ({detection.get('confidence', 0):.2f})")
                                            st.markdown(f"Score: {detection.get('confidence', 0):.2f}")
                                        with col_valid:
                                            is_true_positive = st.checkbox("✓ Valid", value=detection.get('is_true_positive', True), key=f"tp_{i}")
                                        
                                        with save_button:
                                            if st.button("💾", key=f"save_btn_{i}"):
                                                st.session_state[f"save_trigger_{i}"] = True
                                                st.rerun()
                                        
                                # Auto-save when checkbox changes
                                if is_true_positive != detection.get('is_true_positive', True):
                                    curation_data = {
                                        "is_true_positive": is_true_positive,
                                        "corrected_class": detection.get('corrected_class', detection.get('class')),
                                        "tags": detection.get('tags', [])
                                    }
                                    curation_manager.save_curation(i, curation_data, video_name=video_name)
                                    st.session_state.saved_detections.add(i)
                                    
                                    # Update frame with new class color if class changed
                                    frame_image_path = detection.get('frame_image')
                                    if frame_image_path:
                                        frame_updater.update_frame_with_curated_class(
                                            f"data/{frame_image_path}", 
                                            detection, 
                                            curation_data['corrected_class']
                                        )
                                    st.rerun()
                                
                                if is_true_positive:
                                    # Use bbox_drawer to get consistent colors
                                    from src.bbox_drawer import BBoxDrawer
                                    bbox_drawer = BBoxDrawer()
                                    
                                    # Get current class (what's actually shown in frame after any updates)
                                    current_class = detection.get('corrected_class', detection.get('class', 'Packaging'))
                                    
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
                                    # col_label, col_select, col_color, col_tag_label, col_tag_select = st.columns([0.4, 2, 0.4, 0.4, 2])
                                    # with col_label:
                                    #         st.markdown("**Class:**")
                                    with col_select:
                                        new_class = st.selectbox("Class", bbox_drawer.class_names, index=default_idx, key=f"class_{i}", label_visibility="collapsed")
                                    with col_color:
                                        # Show color for selected class using HTML
                                        selected_color_hex = bbox_drawer.get_class_color_hex(new_class)
                                        st.markdown(f"<div style='display:inline-block; width:40px; height:20px; background-color:{selected_color_hex}; border:1px solid #ccc; border-radius:3px; vertical-align:middle; margin-top:8px;'></div>", unsafe_allow_html=True)
                                    # with col_tag_label:
                                            # st.markdown("**Tags:**")
                                    with col_tag_select:
                                        current_tags = detection.get('tags', [])
                                        tags = st.multiselect("Tags", ["floating", "submerged", "large", "small", "degraded"], default=current_tags, key=f"tags_{i}", label_visibility="collapsed")
                                

                                    # Auto-save when class or tags change
                                    if (new_class != current_class or tags != detection.get('tags', [])):
                                        curation_data = {
                                            "is_true_positive": is_true_positive,
                                            "corrected_class": new_class,
                                            "tags": tags
                                        }
                                        curation_manager.save_curation(i, curation_data, video_name=video_name)
                                        st.session_state.saved_detections.add(i)
                                        
                                        # Update frame with new class color if class changed
                                        frame_image_path = detection.get('frame_image')
                                        if frame_image_path and new_class != current_class:
                                            frame_updater.update_frame_with_curated_class(
                                                f"data/{frame_image_path}", 
                                                detection, 
                                                new_class
                                            )
                                        st.rerun()
                                else:
                                    new_class = detection.get('corrected_class', detection.get('class', 'Packaging'))
                                    tags = detection.get('tags', [])
                                
                                # Save button functionality
                                if st.session_state.get(f"save_trigger_{i}", False):
                                    curation_data = {
                                        "is_true_positive": is_true_positive,
                                        "corrected_class": new_class,
                                        "tags": tags
                                    }
                                    curation_manager.save_curation(i, curation_data, video_name=video_name)
                                    st.session_state.saved_detections.add(i)
                                    
                                    # Update frame with new class color
                                    frame_image_path = detection.get('frame_image')
                                    if frame_image_path and new_class != detection.get('class'):
                                        frame_updater.update_frame_with_curated_class(
                                            f"data/{frame_image_path}", 
                                            detection, 
                                            new_class
                                        )
                                    st.success("Saved!")
                                    st.session_state[f"save_trigger_{i}"] = False
                                    st.rerun()
                                
                                # Image preview
                                frame_image_path = detection.get('frame_image')
                                if frame_image_path and Path(f"data/{frame_image_path}").exists():
                                    
                                    st.image(f"data/{frame_image_path}", width=200)
                                        
                                    # Toggle large view
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
                                        st.image(f"data/{frame_image_path}", caption=f"Detection {i+1} - Frame {detection.get('frame', 'N/A')}")
                                elif frame_image_path:
                                    st.info(f"Image not found: {frame_image_path}")
                                else:
                                    st.info("No image path available")
                                
                                # Divider between detection cards
                                st.markdown('<hr style="margin: 5px 0; border: 1px solid #ddd;">', unsafe_allow_html=True)
                
        else:
            st.warning("No detection results found for this model. Please run inference first.")
    else:
        st.warning("No models found. Please run inference first.")
else:
    st.warning("Results directory not found. Please run inference first.")
