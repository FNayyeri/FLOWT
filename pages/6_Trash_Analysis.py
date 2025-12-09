import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path
import sys
import json

sys.path.append(str(Path(__file__).parent.parent))
from src.analytics import AnalyticsEngine

st.set_page_config(page_title="Analysis", page_icon="📊")

# Setup shared sidebar
from src.sidebar_config import setup_sidebar
setup_sidebar()

st.markdown("""
<style>          
/* Secondary buttons - green */
button[kind="secondary"] {
    background-color: green !important;
    color: white !important;
    width: 200px !important;
    border: none !important;
}

/* Primary buttons (Navigation) - blue */
button[kind="primary"] {
    background-color: blue !important;
    color: white !important;
    width: 150px !important;
    border: none !important;
}

/* Tertiary buttons - green */
button[kind="tertiary"] {
    background-color: green !important;
    color: Blue !important;
    width: 150px !important;
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
        st.switch_page("pages/5_Video_Generation.py")
with right_col:
    if st.button("Next ▶", type="primary"):
        st.switch_page("pages/7_AI_Insight.py")
st.markdown('<hr style="margin: 5px 0; border: 1px solid #ddd;">', unsafe_allow_html=True)
# Initialize analytics engine
@st.cache_resource
def load_analytics_engine():
    return AnalyticsEngine()

analytics = load_analytics_engine()

# Configuration
# st.header("🔧 Configuration")
curated_base_dir = Path("data/curated")
tracking_base_dir = Path("data/tracking")
analysis_base_dir = Path("data/analysis")


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
                ["Detection Analytics", "Tracking Analytics"]
            )
        st.markdown('<hr style="margin: 5px 0; border: 1px solid #ddd;">', unsafe_allow_html=True)
        
        class_order, class_color_map = analytics.get_class_order()
        # analysis_type ="Detection Analytics"
        # selected_video = "001.mp4"
        if analysis_type == "Detection Analytics":
            model_curated_dir = curated_base_dir / selected_model    
            if model_curated_dir.exists():  
                metrics_df, class_metrics_df, class_performance_df, conf_counts, tag_analysis, all_data_videos = analytics.generate_detection_report(class_order, model_curated_dir, selected_video)
                if not metrics_df.empty and not class_metrics_df.empty and not conf_counts.empty:

                    total_detections = class_metrics_df['Total Detections'].sum()
                    correct_trash = class_metrics_df['Correctly Detected'].sum()
                    misclassified = class_metrics_df['Misclassified'].sum()
                    not_trash = class_metrics_df['Falsely Detected'].sum()
                    accuracy = float(round((pd.to_numeric(class_metrics_df['Accuracy'], errors='coerce').mean()), 2))
                    
                    trash_presence = float(round((pd.to_numeric(class_metrics_df['Trash Precence'], errors='coerce').mean()), 2)) 
                    classification_acc = float(round((pd.to_numeric(class_metrics_df['Classification Accuracy'], errors='coerce').mean()), 2))  
                    avg_confidence = float(round((pd.to_numeric(class_metrics_df['Average Confidence'], errors='coerce').mean()), 2))  
                    
                   
                    
                    # Performance by Video - Always visible
                    
                    with st.expander("📊 Detection Results", expanded=True):
                    # Overall metrics - Always visible
                    # st.subheader("Reviewed Analysis Results")
                        col1, col2, col3, col4 = st.columns(4)
                        
                        with col1:
                            st.metric("Total Detections", total_detections)
                        with col2:
                            st.metric("Correct Trash", correct_trash, help="Correct trash with correct category")
                        with col3:
                            st.metric("Misclassified", misclassified, help="Correct trash but wrong category")
                        with col4:
                            st.metric("Not Trash", not_trash, help="False detections")
                    
                    
                    color_map = {
                            'Correct Trash': '#2E8B57',  # Green
                            'Misclassified': '#FF8C00',  # Orange
                            'Not Trash': '#DC143C'      # Red
                        }
                    
                    outcome_types =  ['Correct Trash', 'Misclassified', 'Not Trash']
                    outcome_counts = [int(correct_trash), int(misclassified), int(not_trash)]
                    
                    with st.expander("📊 Detection - per Class", expanded=False):
                        st.info("Shows the breakdown of detections into three categories: correctly identified trash, misclassified trash, and false detections (non-trash)")
                        col1, col2 = st.columns([2,1])
                        with col1:
                            st.dataframe(class_performance_df, height=490)
                        with col2: 
                            if any(count > 0 for count in outcome_counts): # Ensure there's at least one non-zero count
                                # Filter out zero values
                                outcome_types_filtered = [ot for ot, count in zip(outcome_types, outcome_counts) if count > 0]
                                outcome_counts_filtered = [count for count in outcome_counts if count > 0]

                                fig_review_outcome = px.pie(
                                    values=outcome_counts_filtered,
                                    names=outcome_types_filtered,
                                )
                                fig_review_outcome.update_traces(textinfo='percent+label')
                                if color_map:
                                    colors_outcomes = [class_color_map.get(name, '#808080') for name in outcome_types]
                                    fig_review_outcome.update_traces(marker=dict(colors=[color_map[cat] for cat in outcome_types_filtered]))
                                    fig_review_outcome.update_layout(legend=dict(orientation="h", yanchor="top", y=-0.1, xanchor="center", x=0.5))
                            # st.subheader("Reviewed Detections", help="Breakdown of detection results after reviewing process.")
                            st.plotly_chart(fig_review_outcome)
                        fig_hist = px.bar(
                            conf_counts,
                            x='confidence_range',
                            y='count',
                            color='Outcome',
                            color_discrete_map=color_map,
                            barmode='group'
                        )

                        fig_hist.update_layout(
                            xaxis_title="Confidence Range",
                            yaxis_title="Number of Detections",
                            legend=dict(orientation="h", y=-0.1)
                        )
                    with st.expander("📊 Detection - per Video and Class", expanded=False):
                        st.info("Shows the performance metrics for each video processed, allowing comparison across different videos.")
                        media_name = selected_video.replace('.mp4', '') if selected_video.endswith('.mp4') else selected_video
                        
                        if all_data_videos:
                            # Convert dictionary data into a dataframe format
                            video_summary = []
                            for media, dets in all_data_videos.items():
                                for det in dets:
                                    det_video = det.get('video', media + '.mp4')
                                    det_class = det.get('class', 'Unknown')
                                    det_is_true_positive = det.get('is_true_positive', False)
                                    det_corrected_class = det.get('corrected_class', det_class)
                                    det_confidence = det.get('confidence', 0.0)
                                    
                                    correct_trash = 1 if (det_is_true_positive and det_class == det_corrected_class) else 0
                                    misclassified = 1 if (det_is_true_positive and det_class != det_corrected_class) else 0  
                                    no_trash = 1 if (not det_is_true_positive) else 0
                                    
                                    info = {
                                        'video': det_video,
                                        'class': det_class,
                                        'correct_trash': correct_trash,
                                        'misclassified': misclassified,
                                        'no_trash': no_trash,
                                        'confidence': det_confidence
                                    }
                                    video_summary.append(info)
                            video_summary_df = pd.DataFrame(video_summary)
                            video_performance = video_summary_df.groupby(['video', 'class']).agg({
                                'correct_trash': 'sum',
                                'misclassified': 'sum',
                                'no_trash': 'sum',
                                'confidence': 'mean'
                            }).round(3)
                            
                            # Add Overall row with proper multi-index
                            overall_data = {
                                'correct_trash': video_summary_df['correct_trash'].sum(),
                                'misclassified': video_summary_df['misclassified'].sum(),
                                'no_trash': video_summary_df['no_trash'].sum(),
                                'confidence': round(video_summary_df['confidence'].mean(), 3)
                            }
                            overall_row = pd.DataFrame([overall_data], index=pd.MultiIndex.from_tuples([('Overall', 'All')], names=['video', 'class']))
                            
                            video_performance = pd.concat([video_performance, overall_row])
                            _, col1, _ = st.columns([1,2,1])
                            with col1:
                                st.dataframe(video_performance, width="stretch", height=490)
                        else:
                            st.info("No per-video data available.")
                       
                    with st.expander("🎯  Performance Summary", expanded=True):
                    # Performance Summary - Always visible
                        st.subheader("Performance Summary")
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Overall Accuracy", f"{accuracy}%", help="Proportion of 'total detections' that were correct trash (correct or misclassified)")
                        with col2:
                            st.metric("Trash Presence Rate", f"{trash_presence}%" , help="Proportion of 'detections' that were actually trash (correct or misclassified)")
                        with col3:
                            st.metric("Classification Accuracy", f"{classification_acc}%" , help="Proportion of 'trash detections'(correct or misclassified) that were correctly classified")
                    # Class-wise performance pie charts
                    class_metrics_df.set_index('Class', inplace=True)

                    correct_trash_data = class_metrics_df[class_metrics_df['Correctly Detected'] > 0]
                    if not correct_trash_data.empty:
                        fig_pie_correct_trash = px.pie(
                            values=correct_trash_data['Correctly Detected'].values,
                            names=correct_trash_data['Correctly Detected'].index,
                        )
                        fig_pie_correct_trash.update_traces(textinfo='percent+label')
                        if class_color_map:
                            colors_correct_trash = [class_color_map.get(name, '#808080') for name in correct_trash_data.index]
                            fig_pie_correct_trash.update_traces(marker=dict(colors=colors_correct_trash))
                            fig_pie_correct_trash.update_layout(legend=dict(orientation="h", yanchor="top", y=-0.1, xanchor="center", x=0.5))

                    else:
                        st.info("No correct trash detections")
                        
                    misclassified_data = class_metrics_df[class_metrics_df['Misclassified'] > 0]
                    if not misclassified_data.empty:
                        fig_pie_misclassified = px.pie(
                            values=misclassified_data['Misclassified'].values,
                            names=misclassified_data['Misclassified'].index,
                        ) 
                        fig_pie_misclassified.update_traces(textinfo='percent+label')
                        if class_color_map:
                            colors_misclassified = [class_color_map.get(name, '#808080') for name in misclassified_data.index]
                            fig_pie_misclassified.update_traces(marker=dict(colors=colors_misclassified))
                            fig_pie_misclassified.update_layout(legend=dict(orientation="h", yanchor="top", y=-0.1, xanchor="center", x=0.5))
                    else:
                        st.info("No misclassified trash detections")
                    
                    no_trash_data = class_metrics_df[class_metrics_df['Falsely Detected'] > 0]
                    if not no_trash_data.empty:
                        fig_pie_no_trash = px.pie(
                            values=no_trash_data['Falsely Detected'].values,
                            names=no_trash_data['Falsely Detected'].index,
                        ) 
                        fig_pie_no_trash.update_traces(textinfo='percent+label')
                        if class_color_map:
                            colors_no_trash = [class_color_map.get(name, '#808080') for name in no_trash_data.index]
                            fig_pie_no_trash.update_traces(marker=dict(colors=colors_no_trash))
                            fig_pie_no_trash.update_layout(legend=dict(orientation="h", yanchor="top", y=-0.1, xanchor="center", x=0.5))
                    else:
                        st.info("No falsely trash detections")
                    
                    # Third row - Collapsed by default
                    with st.expander("🎯 Detection Outcome - Breakdown per Class", expanded=False):
                        # Display all three pie charts
                        col_map1, col_map2, col_map3 = st.columns(3)
                        
                        with col_map1:
                            st.subheader("Correct Trash Classes", help="Trash classes that were correctly identified")
                            if 'fig_pie_correct_trash' in locals():                                
                                st.plotly_chart(fig_pie_correct_trash)
                            else:
                                st.info("No correct trash detections")
                        
                        with col_map2:
                            st.subheader("Misclassified Trash Classes", help="Trash classes that were misclassified")
                            if 'fig_pie_misclassified' in locals():   
                                st.plotly_chart(fig_pie_misclassified)
                            else:
                                st.info("No misclassified detections")
                        
                        with col_map3:
                            st.subheader("Falsley Detected", help="Detections that were not actually trash")
                            if 'fig_pie_no_trash' in locals():   
                                st.plotly_chart(fig_pie_no_trash)
                            else:
                                st.info("No false positive detections")
                    # Second row - Collapsed by default
                    with st.expander("📊 Confidence Distribution - per Detection Outcome", expanded=False):
                        _, col_map2,_ = st.columns([1,2, 1])

                        with col_map2:
                            # Confidence distribution histogram
                            # st.subheader("Confidence Distribution Across Detection Outcomes", help="Distribution of confidence scores for each detection outcome.")
                            st.plotly_chart(fig_hist)
                    # Fourth row - Tag Analysis - Collapsed by default
                    with st.expander("🏷️ Tag Analysis", expanded=False):
                        if tag_analysis and tag_analysis.get('overall_tag_distribution'):
                            col_tag1, col_tag2 = st.columns(2)
                            
                            with col_tag1:
                                st.subheader("Class-Tag Combinations")
                                if tag_analysis['class_tag_combinations']:
                                    fig_class_tags = px.pie(
                                        values=list(tag_analysis['class_tag_combinations'].values()),
                                        names=list(tag_analysis['class_tag_combinations'].keys()),
                                        # title="Tag Usage by Class"
                                    )
                                    fig_class_tags.update_traces(textinfo='percent+label')
                                    fig_class_tags.update_layout(legend=dict(orientation="h", yanchor="top", y=-0.1, xanchor="center", x=0.5))
                                    st.plotly_chart(fig_class_tags)
                                else:
                                    st.info("No class-tag combinations found")
                                
                            
                            with col_tag2:
                                st.subheader("Overall Tag Distribution")
                                if tag_analysis['overall_tag_distribution']:
                                    fig_tags_overall = px.pie(
                                        values=list(tag_analysis['overall_tag_distribution'].values()),
                                        names=list(tag_analysis['overall_tag_distribution'].keys()),
                                        # title="Tags Across All Classes"
                                    )
                                    fig_tags_overall.update_traces(textinfo='percent+label')
                                    fig_tags_overall.update_layout(legend=dict(orientation="h", yanchor="top", y=-0.1, xanchor="center", x=0.5))
                                    st.plotly_chart(fig_tags_overall)
                                else:
                                    st.info("No tags found")
                        else:
                            st.info("No tag data available for analysis")

            else:
                st.warning(f"No reviewed data found for {selected_model}. Please review the results and save them first.")
        # analysis_type = "Tracking Analytics"
        # selected_video = "008.mp4"
        # if analysis_type == "Tracking Analytics":
        elif analysis_type == "Tracking Analytics":
            # st.header("Tracking Analytics")
            
            model_tracking_dir = tracking_base_dir / selected_model
            
            if model_tracking_dir.exists():
                tracking_performance_all_df, tracking_classes_df, tracking_clas_all_df = analytics.generate_tracking_report(model_tracking_dir, selected_video)

                # Overall metrics
                st.subheader("Overall Tracking Metrics")
                if not tracking_performance_all_df.empty:
                    tracking_metrics_df = tracking_performance_all_df[tracking_performance_all_df['Video']=='Overall']

                    total_videos = len(tracking_metrics_df)
                    total_objects = tracking_metrics_df['Unique Trash'].sum()
                    total_detections = tracking_metrics_df['Detections'].sum()
                else:
                    st.warning(f"No tracking statistics available.")
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Videos Processed", total_videos)
                with col2:
                    st.metric("Total Unique Objects", total_objects)
                with col3:
                    st.metric("Total Detections", total_detections)
                st.markdown('<hr style="margin: 5px 0; border: 1px solid #ddd;">', unsafe_allow_html=True)
                # Objects by class
                st.subheader("Total Trash")
                # Create a grouped DataFrame first
                grouped_data = tracking_classes_df.groupby('Class')['Unique Trash'].sum().reset_index()
                fig_bar_trash_track = px.bar(
                    grouped_data,
                    x='Class',
                    y='Unique Trash',
                    title="Total Trash by Class",
                    color='Class',
                    color_discrete_map=class_color_map
                )

                # tracking_clas_all_df.to_csv(tracking_classes_all_csv, index=True)
                tracking_performance_all_df.set_index('Video', inplace=True)
                tracking_clas_all_df.set_index('Class', inplace=True)
                _, col2, _ = st.columns([1,2,1])
                with col2:
                    st.plotly_chart(fig_bar_trash_track)

                _, col1, col2, _ = st.columns([0.2, 1, 1, 0.2])
                with col1:
                    # # Per-video breakdown
                    st.subheader("Performance (Per-Video Breakdown)")
                    column_order_perform = ['Timelapse Video', 'IoU Threshold', 'Template Threshold', 'Unique Trash', 'Detections']
                    tracking_performance_all_df = tracking_performance_all_df[column_order_perform]
                    st.dataframe(tracking_performance_all_df, width="content", height=490)
                with col2:
                    # # Objects by class
                    st.subheader("Performance (Per-Trash Breakdown)")

                    # Specify the desired column order
                    column_order = ['Video', 'Unique Trash', 'Avg Confidence', 'Min Confidence', 'Max Confidence', 'Detections']
                    # # Reorder columns and drop unwanted columns
                    ordered_df = tracking_clas_all_df.drop(['Timelapse Video', 'IoU Threshold', 'Template Threshold'], axis=1, errors='ignore')[column_order]
                    st.dataframe(ordered_df, width="content", height=490)
 
            else:
                st.warning(f"No tracking data found for {selected_model}. Please run tracking first.")
    else:
        st.warning("No models with curated data found.")
else:
    st.warning("Curated data directory not found. Please complete curation first.")