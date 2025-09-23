import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path
import sys
sys.path.append(str(Path(__file__).parent.parent))
from src.analytics import AnalyticsEngine

st.set_page_config(page_title="Analysis", page_icon="📊")

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
st.title("📊 Analysis")
st.markdown("Statistical insights and performance metrics for marine litter detection.")

# Debug: Show current session state
# st.write(f"Debug - nav_video: {st.session_state.get('nav_video', 'Not set')}")

# Navigation buttons
left_col, spacer_col, right_col = st.columns([0.1, 1, 0.1])
with left_col:
    if st.button("◀ Previous", type="primary"):
        st.switch_page("pages/5_🎬_Video_Generation.py")
with right_col:
    if st.button("Next ▶", type="primary"):
        st.switch_page("pages/7_🤖_Analysis_AI.py")
st.markdown('<hr style="margin: 5px 0; border: 1px solid #ddd;">', unsafe_allow_html=True)
# Initialize analytics engine
@st.cache_resource
def load_analytics_engine():
    return AnalyticsEngine()

analytics = load_analytics_engine()

# Configuration
st.header("Configuration")
curated_base_dir = Path("data/curated")
if curated_base_dir.exists():
    model_dirs = [d for d in curated_base_dir.iterdir() if d.is_dir()]
    
    if model_dirs:
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # Use nav_model if available
            model_names = [d.name for d in model_dirs]
            nav_model = st.session_state.get('nav_model', '')
            # Extract model name from path if nav_model is a full path
            nav_model_name = Path(nav_model).stem if nav_model else ''
            default_model = nav_model_name if nav_model_name in model_names else (model_names[0] if model_names else "")
            
            selected_model = st.selectbox(
                "Select Model for Analysis",
                model_names,
                index=model_names.index(default_model) if default_model in model_names else 0
            )
            
            # Update nav_model to match current selection
            st.session_state.nav_model = f"models/{selected_model}.pt"
        
        with col2:
            # Get curated files for selected model to populate video options
            model_curated_dir = curated_base_dir / selected_model
            video_names = []
            if model_curated_dir.exists():
                curated_files = list(model_curated_dir.glob("*_curated_detections.json"))
                video_names = sorted([f.stem.replace('_curated_detections', '') for f in curated_files])

            video_options = ["All"] + [f+'.mp4' for f in video_names]
            if 'video_selection' not in st.session_state:
                nav_video = st.session_state.get('nav_video', '')
                if nav_video:
                    nav_video_full = f"{nav_video}.mp4" if not nav_video.endswith('.mp4') else nav_video
                    st.session_state.video_selection = nav_video_full if nav_video_full in video_options else (video_options[0] if video_options else "")
                else:
                    st.session_state.video_selection = video_options[0] if video_options else ""
            # st.write(f"Debug - video_selection: {st.session_state.get('video_selection', 'Not set')}")
            def update_nav_video():
                selected = st.session_state.video_selection
                st.session_state.nav_video = selected.replace('.mp4', '') if selected.endswith('.mp4') else selected
            
            selected_video = st.selectbox(
                "Select Video",
                video_options,
                key="video_selection",
                on_change=update_nav_video
            )

            st.session_state.nav_video = selected_video
        with col3:
            # Analysis type selection
            analysis_type = st.radio(
                "Analysis Type",
                ["Tracking Analytics", "Detection Analytics"]
            )
        st.markdown('<hr style="margin: 5px 0; border: 1px solid #ddd;">', unsafe_allow_html=True)
        if analysis_type == "Detection Analytics":
            st.header("Detection Analytics")
            model_curated_dir = curated_base_dir / selected_model
            
            if model_curated_dir.exists():
                # Load all curated JSON files for the selected model
                curated_files = list(model_curated_dir.glob("*_curated_detections.json"))
                
                if curated_files:
                    
                    # Load data based on selection
                    if selected_video == "All":
                        # Combine data from all curated files
                        all_data = []
                        for curated_file in curated_files:
                            file_data = analytics.load_curated_data(curated_file)
                            if file_data:
                                all_data.extend(file_data)
                        data = all_data
                        # st.info(f"Analyzing {len(curated_files)} curated files with {len(data)} total detections.")
                    else:
                        # Load data for specific video
                        selected_video_stem = selected_video.replace('.mp4', '')
                        specific_file = model_curated_dir / f"{selected_video_stem}_curated_detections.json"
                        if specific_file.exists():
                            data = analytics.load_curated_data(specific_file)
                            # st.info(f"Analyzing video '{selected_video}' with {len(data)} detections.")
                        else:
                            data = []
                            st.warning(f"No curated data found for video '{selected_video}'.")
                    
                    if data:
                        # Overall metrics
                        st.subheader("Overall Metrics")
                        col1, col2, col3, col4 = st.columns(4)
                        
                        total_detections = len(data)
                        true_positives = sum(1 for d in data if d.get('is_true_positive', False))
                        false_positives = total_detections - true_positives
                        accuracy = true_positives / total_detections if total_detections > 0 else 0
                        
                        with col1:
                            st.metric("Total Detections", total_detections)
                        with col2:
                            st.metric("True Positives", true_positives)
                        with col3:
                            st.metric("False Positives", false_positives)
                        with col4:
                            st.metric("Accuracy", f"{accuracy:.2%}")
                        
                        # Class distribution
                        st.subheader("Class Distribution")
                        df = pd.DataFrame(data)
                        
                        if 'corrected_class' in df.columns:
                            class_counts = df['corrected_class'].value_counts()
                            fig_pie = px.pie(
                                values=class_counts.values,
                                names=class_counts.index,
                                title="Distribution of Trash Classes"
                            )
                            st.plotly_chart(fig_pie)
                        
                        # Confidence distribution
                        st.subheader("Confidence Distribution")
                        if 'confidence' in df.columns:
                            fig_hist = px.histogram(
                                df,
                                x='confidence',
                                nbins=20,
                                title="Detection Confidence Distribution"
                            )
                            st.plotly_chart(fig_hist)
                        
                        # Performance by class
                        st.subheader("Performance by Class")
                        if 'corrected_class' in df.columns and 'is_true_positive' in df.columns:
                            class_performance = df.groupby('corrected_class').agg({
                                'is_true_positive': ['count', 'sum']
                            }).round(3)
                            class_performance.columns = ['Total', 'True Positives']
                            class_performance['Accuracy'] = class_performance['True Positives'] / class_performance['Total']
                            st.dataframe(class_performance)
                        
                        # Tag analysis
                        st.subheader("Tag Analysis")
                        all_tags = []
                        for detection in data:
                            if 'tags' in detection and detection['tags']:
                                all_tags.extend(detection['tags'])
                        
                        if all_tags:
                            tag_counts = pd.Series(all_tags).value_counts()
                            fig_bar = px.bar(
                                x=tag_counts.index,
                                y=tag_counts.values,
                                title="Tag Frequency"
                            )
                            st.plotly_chart(fig_bar)
                    
                        # Export analytics
                        st.header("Export Analytics")
                        if st.button("Generate Analytics Report"):
                            # Filter and prepare CSV report
                            export_df = df[df['is_true_positive'] == True].copy()
                            
                            # Round confidence to 2 decimal places
                            if 'confidence' in export_df.columns:
                                export_df['confidence'] = export_df['confidence'].round(2)
                            
                            # Rename corrected_class to class
                            if 'corrected_class' in export_df.columns:
                                export_df['class'] = export_df['corrected_class']
                            
                            # Remove unwanted columns
                            columns_to_remove = ['bbox', 'is_true_positive', 'tags', 'corrected_class']
                            export_df = export_df.drop(columns=[col for col in columns_to_remove if col in export_df.columns])
                            
                            report_csv = export_df.to_csv(index=False)
                            st.download_button(
                                "Download Report",
                                report_csv,
                                "analytics_report.csv",
                                "text/csv"
                            )
                    else:
                        st.warning(f"No data available for analysis.")
                else:
                    st.warning(f"No curated files found for {selected_model}. Please complete curation first.")
            else:
                st.warning(f"No curated directory found for {selected_model}. Please complete curation first.")
        
        elif analysis_type == "Tracking Analytics":
            st.header("Tracking Analytics")
            tracking_base_dir = Path("data/tracking")
            model_tracking_dir = tracking_base_dir / selected_model
            
            if model_tracking_dir.exists():
                tracking_files = list(model_tracking_dir.glob("*.json"))
                
                if tracking_files:
                    import json
                    all_tracking_stats = []
                    video_stats = {}
                     # Load data based on selection
                    if selected_video == "All":
                        # Combine data from all curated files
                        # all_data = []
                        for tracking_file in tracking_files:
                            tracking_data = analytics.load_curated_data(tracking_file)
                            if tracking_data:
                                video_name = tracking_data['video']
                                stats = tracking_data['statistics']
                                video_stats[video_name] = stats
                                all_tracking_stats.append(stats)

                                # all_data.extend(tracking_data)
                        # data = all_data
                        # st.info(f"Analyzing {len(tracking_files)} files with {len(all_tracking_stats)} total detections.")
                    else:
                        # Load data for specific video
                        selected_video_stem = selected_video.replace('.mp4', '')
                        specific_file = model_tracking_dir / f"{selected_video_stem}_tracking.json"
                        if specific_file.exists():
                            tracking_data = analytics.load_curated_data(specific_file)
                            if tracking_data:
                                video_name = tracking_data['video']
                                stats = tracking_data['statistics']
                                video_stats[video_name] = stats
                                all_tracking_stats.append(stats)
                            # st.info(f"Analyzing video '{selected_video}' with {len(all_tracking_stats)} detections.")
                        else:
                            data = []
                            st.warning(f"No tracked data found for video '{selected_video}'.")
                    # Load all tracking data
                    
                    
                    # for tracking_file in tracking_files:
                    #     with open(tracking_file, 'r') as f:
                    #         tracking_data = json.load(f)
                        
                    #     video_name = tracking_data['video']
                    #     stats = tracking_data['statistics']
                    #     video_stats[video_name] = stats
                    #     all_tracking_stats.append(stats)
                    
                    # Overall metrics
                    st.subheader("Overall Tracking Metrics")
                    total_videos = len(all_tracking_stats)
                    total_objects = sum(s['total_unique_objects'] for s in all_tracking_stats)
                    total_detections = sum(s['total_detections'] for s in all_tracking_stats)
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Videos Processed", total_videos)
                    with col2:
                        st.metric("Total Unique Objects", total_objects)
                    with col3:
                        st.metric("Total Detections", total_detections)
                    
                    # Objects by class
                    st.subheader("Objects by Class (All Videos)")
                    class_totals = {}
                    for stats in all_tracking_stats:
                        for class_name, count in stats['objects_by_class'].items():
                            class_totals[class_name] = class_totals.get(class_name, 0) + count
                    
                    if class_totals:
                        df_classes = pd.DataFrame(list(class_totals.items()), columns=['Class', 'Count'])
                        fig_bar = px.bar(df_classes, x='Class', y='Count', title="Total Objects by Class")
                        st.plotly_chart(fig_bar)
                    
                    # Per-video breakdown
                    st.subheader("Per-Video Breakdown")
                    for video_name, stats in video_stats.items():
                        with st.expander(f"📹 {video_name}"):
                            col1, col2 = st.columns(2)
                            with col1:
                                st.metric("Unique Objects", stats['total_unique_objects'])
                                st.metric("Total Detections", stats['total_detections'])
                            with col2:
                                st.write("**Objects by Class:**")
                                for class_name, count in stats['objects_by_class'].items():
                                    st.write(f"• {class_name}: {count}")
                else:
                    st.warning(f"No tracking results found for {selected_model}. Please run tracking first.")
            else:
                st.warning(f"No tracking data found for {selected_model}. Please run tracking first.")
    else:
        st.warning("No models with curated data found.")
else:
    st.warning("Curated data directory not found. Please complete curation first.")