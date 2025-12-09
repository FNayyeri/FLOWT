import streamlit as st
from pathlib import Path
import sys
import json
import pandas as pd
sys.path.append(str(Path(__file__).parent.parent))
from src.genai_service import GenAIService
from src.analytics import AnalyticsEngine
from src.prompts_ai import PromptsAI
from src.prompts_ai import PromptsAI

st.set_page_config(page_title="AI Insight", page_icon="🤖")

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
    width: 200px !important;
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
st.title("🤖 AI Insight")
st.markdown("AI insight from marine litter detection data using Large Language Models.")

# Navigation buttons
left_col, spacer_col, right_col = st.columns([0.1, 1, 0.1])
with left_col:
    if st.button("◀ Previous", type="primary"):
        st.switch_page("pages/6_Trash_Analysis.py")
with right_col:
    if st.button("Next ▶", type="primary"):
        st.switch_page("pages/8_Model_Refining.py")
st.markdown('<hr style="margin: 5px 0; border: 1px solid #ddd;">', unsafe_allow_html=True)
# Initialize GenAI service
genai_service = GenAIService()
prompt_ai_service = PromptsAI()
available_providers = genai_service.get_available_providers()

@st.cache_resource
def load_analytics_engine():
    return AnalyticsEngine()

analytics = load_analytics_engine()

# Configuration
# st.header("🔧 Configuration")
curated_base_dir = Path("data/curated")
tracking_base_dir = Path("data/tracking")
analysis_base_dir = Path("data/analysis")
metadata_dir = Path("data/metadata")

col_model, col_video, col_analysis, col_token = st.columns(4)

if curated_base_dir.exists():
    model_dirs = [d for d in curated_base_dir.iterdir() if d.is_dir()]
    
    if model_dirs:
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
            # Get curated files for selected model
            model_curated_dir = curated_base_dir / selected_model
            if model_curated_dir.exists():
                curated_files = list(model_curated_dir.glob("*_curated_detections.json"))
                video_names = sorted([f.stem.replace('_curated_detections', '') for f in curated_files])
                video_options = ["All"] + [f+'.mp4' for f in video_names]
                
            else:
                video_options = ["All"]
            
            # Use nav_video if available
            default_video = st.session_state.get('nav_video', video_options[0] if video_options else "All")
            if default_video not in video_options:
                default_video = video_options[0] if video_options else "All"
            
            selected_video = st.selectbox("Select Video", video_options, index=video_options.index(default_video) if default_video in video_options else 0)
            # selected_video = '010.mp4'
            
            st.session_state.nav_video = selected_video
    else:
        st.warning("No models found.")
        selected_model = None
        curated_files = []

else:
    st.warning("No curated data directory found.")
    selected_model = None
    curated_files = []
with col_analysis:
    analysis_types = [
        "Data Summary & Insights",
        "Performance Analysis",
        "Class Distribution Analysis",
        "Quality Assessment",
        "Custom Query"
    ]
    analysis_type = st.selectbox("Analysis Type", [at for at in analysis_types])

with col_token:    
    # Token size selection
    token_sizes = ["Short", "Long"]
    token_size_selected = st.selectbox("Prompt Length", token_sizes, disabled=(analysis_type == "Custom Query"))
    

col_scope, _, col_ai, col_tokeninfo = st.columns([2, 0.001, 1, 1])
with col_scope:
    # Analysis scope expander
    with st.expander("📋 Analysis Scope", expanded=False):
        st.write("Select what to include in the analysis:")
        include_detection = st.checkbox("Detection Results", value=True, help="Include detection accuracy, class distribution, and confidence scores")
        include_tracking = st.checkbox("Tracking Results", value=True, help="Include object tracking data and movement patterns")
        include_tags = st.checkbox("Tags", value=True, help="Include user-defined tags and annotations")
        include_metadata = st.checkbox("Metadata", value=True, help="Include video metadata and processing parameters")
        include_confidence = st.checkbox("Confidence Analysis", value=True, help="Include detailed confidence score analysis")
        # include_temporal = st.checkbox("Temporal Patterns", value=False, help="Include time-based analysis patterns")

with col_ai:
    if available_providers:
        # AI Provider info (first available provider)
        provider = available_providers[0]
        provider_name = "OpenAI"

        with st.expander(f"{provider_name} Information", expanded=False):
            provider_info = genai_service.get_provider_info(provider)
            # provider_helps = genai_service.provider_helps.get('max_tokens', '')
            st.write(f"**Model:** {provider_info.get('model_name', 'N/A')}", help=provider_info.get('model_name_help', ''))
            st.info(provider_info.get('model_name_help', ''))
            st.write(f"**Max Tokens:** {provider_info.get('max_tokens', 'N/A')}")
            st.info(genai_service.provider_helps.get('max_tokens', ''))
            st.write(f"**Cost per 1K:** ${provider_info.get('cost_per_1k', 'N/A')}")
            st.info(genai_service.provider_helps.get('cost_per_1k', ''))
            st.write(f"**Rate Limit:** {provider_info.get('rate_limit', 'N/A')}/min")
            st.info(genai_service.provider_helps.get('rate_limit', ''))
    else:
        st.warning("⚠️ Please configure an AI provider first.")
        provider = None
        analysis_type = analysis_types[0]
        include_detection = include_tracking = include_tags = include_metadata = include_confidence = include_temporal = True
        
with col_tokeninfo:
    if available_providers:
        with st.expander("🪙 Cost Information", expanded=False):
            # Show token info
            token_info = PromptsAI.get_token_info()
            if analysis_type != "Custom Query":
                token_range = token_info[token_size_selected.lower()][analysis_type]
                st.write(f"**Token range:** {token_range}")
                token_values_range = token_range.lstrip('~').rstrip('tokens').strip()
                token_values_range = [int(t.strip()) for t in token_values_range.split('-')]   
            else:
                st.info("Token usage will depend on the length of your custom query and the data provided.")
                token_values_range = [1000, 4000]  # Estimate for custom queries
            
            cost_per_1k = provider_info.get('cost_per_1k', 0) 
            if len(token_values_range)==1:
                estimated_cost = round((token_values_range[0] / 1000) * cost_per_1k, 4)
                st.write(f"**Estimated cost per analysis:**  ~${estimated_cost}")
            elif len(token_values_range)==2:
                estimated_cost_range = [round((tokens / 1000) * cost_per_1k, 4) for tokens in token_values_range]
                estimated_cost1 = estimated_cost_range[0]
                estimated_cost2 = estimated_cost_range[1]
                st.write(f"**Estimated cost per analysis:**  ~$({estimated_cost1} - {estimated_cost2})")

            # st.write(f"**Estimated cost per analysis:** ${estimated_cost_range[0]} - ${estimated_cost_range[1]}")
st.markdown('<hr style="margin: 5px 0; border: 1px solid #ddd;">', unsafe_allow_html=True)
# AI Analysis Section
if selected_model and curated_files:
    st.header("AI Analysis")

    # Custom query input for custom analysis
    if analysis_type == "Custom Query":
        custom_query = st.text_area(
            "Enter your custom analysis question:",
            placeholder="e.g., What patterns do you see in the false positive detections?"
        )
    # Generate analysis button
    if available_providers and st.button("Generate AI Analysis", type="secondary"):
        with st.spinner("Analysing data with AI..."):
            # Prepare data summary for LLM ;  Load data based on source selection
            
            data_summary = "" ; data_details = ""
            csv_name = selected_video.replace('.mp4', '') if selected_video.endswith('.mp4') else selected_video 
            class_order, class_color_map = analytics.get_class_order()
            
            total_detections = 0; num_videso = 0 ; total_metadata = 0
            detection_summary = "" ; detection_details = "" ; confidence_summary = "";  tag_details_summary = ""; metadata_summary = ""; trash_categories_info = ""
            tracking_summary = ""; tracking_details = ""
            if include_detection or include_tags or include_confidence:
                detection_csv =  analysis_base_dir / selected_model / f"detection_performance_{csv_name}.csv"
                model_curated_dir = curated_base_dir / selected_model
                detection_total_df, detection_data_df, _, conf_counts, tag_analysis, all_data_videos = analytics.generate_detection_report(class_order, model_curated_dir, selected_video)
                
                if include_detection and (detection_data_df.empty or detection_total_df.empty):
                    total_detections = detection_summary  = 0
                    detection_Details = detection_summary = "No detection data available."
                else:
                    if not detection_data_df.empty:
                        for rec in detection_data_df.to_dict('records'):
                            detection_record = f"""
                                - class name : {rec.get('Class', 'Unknown')}
                                - total class detections : {rec.get('Total Detections', 0)}
                                - class correctly detected : {rec.get('Correctly Detected', 0)}
                                - class misclassified : {rec.get('Misclassified', 0)}
                                - class falsely detected : {rec.get('Falsely Detected' , 0)}
                                - class average confidence : {rec.get('Average Confidence', 0.0)}
                                - class accuracy : {rec.get('Accuracy', 0.0)}
                                - class trash presence : {rec.get('Trash Precence', 0.0)}
                                - class classification accuracy : {rec.get('Classification Accuracy', 0.0)}
                            """
                            if 'detection_Details' not in locals():
                                detection_Details = detection_record
                            else:
                                detection_Details += detection_record
                    if not detection_total_df.empty:
                        total_detections = int(detection_total_df['Total Detections'].values[0]) if 'Total Detections' in detection_total_df else 0
                        correctly_detected = int(detection_total_df['Correctly Detected'].values[0]) if 'Correctly Detected' in detection_total_df else 0
                        misclassified = int(detection_total_df['Misclassified'].values[0]) if 'Misclassified' in detection_total_df else 0
                        falsely_detected = int(detection_total_df['Falsely Detected'].values[0]) if 'Falsely Detected' in detection_total_df else 0
                        average_confidence =  float(detection_total_df['Average Confidence'].values[0]) if 'Average Confidence' in detection_total_df else 0.0
                        accuracy= float(detection_total_df['Accuracy'].values[0]) if 'Accuracy' in detection_total_df else 0.0
                        trash_presence = float(detection_total_df['Trash Precence'].values[0]) if 'Trash Precence' in detection_total_df else 0.0
                        classification_accuracy = float(detection_total_df['Classification Accuracy'].values[0]) if 'Classification Accuracy' in detection_total_df else 0.0

                        detection_summary = f"""
                            Detection Summary: 
                            - Total Detections: {total_detections}
                            - Correctly Detected: {correctly_detected}
                            - Misclassified: {misclassified}
                            - Falsely Detected: {falsely_detected}
                            - Average Confidence: {average_confidence}
                            - Accuracy: {accuracy:.1f}%
                            - Trash Precence: {trash_presence:.2f}%
                            - Classification Accuracy:{classification_accuracy:.2f}%
                        """
                if include_confidence and (detection_data_df.empty or detection_total_df.empty):
                    total_detections = detection_summary  = 0
                    detection_Details = detection_summary = "No detection data available."
                else:
                    if include_confidence:
                        confidence_summary = ""
                        confidence_correct_trash = conf_counts[conf_counts['Outcome'] == 'Correct Trash'][['count', 'confidence_range']]
                        top_3_ranges_correct_trash = confidence_correct_trash.nlargest(3, 'count') # Get top 3 confidence ranges by count
                        
                        
                        if not top_3_ranges_correct_trash.empty:
                            i=1
                            for rec in top_3_ranges_correct_trash.to_dict('records'):
                                conf_summary = f"""
                                    - top {i} range for correct trash: {rec.get('count', 'Unknown')} correctly detected tarsh with confidence in range ({rec.get('confidence_range', '0-0')})
                                """
                                i+=1
                                confidence_summary += conf_summary
                        else:
                            conf_summary = "No correct trash detections found."
                            confidence_summary += conf_summary
                        confidence_misclassified = conf_counts[conf_counts['Outcome'] == 'Misclassified'][['count', 'confidence_range']]
                        top_3_ranges_misclassified = confidence_misclassified.nlargest(3, 'count') # Get top 3 confidence ranges by count
                        if not top_3_ranges_misclassified.empty:
                            i=1
                            for rec in top_3_ranges_misclassified.to_dict('records'):
                                conf_summary = f"""
                                    - top {i} range for misclassified: {rec.get('count', 'Unknown')} misclassified tarsh with confidence in range ({rec.get('confidence_range', '0-0')})
                                """
                                i+=1
                                confidence_summary += conf_summary
                        else:
                            conf_summary = "No misclassified detections found."
                            confidence_summary += conf_summary
                        
                        confidence_no_trash = conf_counts[conf_counts['Outcome'] == 'No Trash'][['count', 'confidence_range']]
                        top_3_ranges_no_trash = confidence_no_trash.nlargest(3, 'count') # Get top 3 confidence ranges by count
                        if not top_3_ranges_no_trash.empty:
                            i=1
                            for rec in top_3_ranges_no_trash.to_dict('records'):
                                conf_summary = f"""
                                    - top {i} range for no-trash: {rec.get('count', 'Unknown')} wrongly detected tarsh with confidence in range ({rec.get('confidence_range', '0-0')})
                                """
                                i+=1
                                confidence_summary += conf_summary
                        else:
                            conf_summary = "No wrongly detected trash found."
                            confidence_summary += conf_summary


                        # class_average_confidence = detection_data_df[['Class', 'Total Detections', 'Correctly Detected', 'Misclassified', 'Falsely Detected', 'Average Confidence']] 
                        class_average_confidence = detection_data_df[['Class', 'Total Detections', 'Correctly Detected', 'Misclassified', 'Falsely Detected', 'Average Confidence']].copy()
                        class_average_confidence['Average Confidence'] = pd.to_numeric(class_average_confidence['Average Confidence'], errors='coerce')
                        top_3_class_average_confidence = class_average_confidence.nlargest(3, 'Average Confidence')
                        if not top_3_class_average_confidence.empty:
                            i=1
                            for rec in top_3_class_average_confidence.to_dict('records'):
                                conf_summary = f"""
                                    - top {i} highest average confidence is for the class: {rec.get('Class', 'Unknown')} with Average Confidence ({rec.get('Average Confidence', '0-0')}). 
                                    This class has {rec.get('Total Detections', 0)} total detections, {rec.get('Correctly Detected', 0)} correctly detected, {rec.get('Misclassified', 0)} misclassified trash, and {rec.get('Falsely Detected', 0)} wrongly detected trash.
                                """
                                i+=1
                                confidence_summary += conf_summary


                    if include_tags:
                        tag_summary_df = pd.DataFrame(tag_analysis['tag_summary']) if 'tag_summary' in tag_analysis else {}
                        if not tag_summary_df.empty:
                            tag_summary = ""
                            for rec in tag_summary_df.to_dict('records'):
                                tag_summary += f"""
                                    Percentage of the class: {rec.get('Class', 'Unknown')} - {rec.get('Tag', 'Unknown')} is {rec.get('Percentage_in_Class', '')}.                               
                                """
                            tag_details_summary += tag_summary

            if include_tracking:
                tracking_csv = analysis_base_dir / selected_model / f"tracking_performance_{csv_name}.csv"
                model_tracking_dir = tracking_base_dir / selected_model
                _, _, tracking_data_df = analytics.generate_tracking_report(model_tracking_dir, selected_video)
                
                if tracking_data_df.empty:
                    num_videso = 0
                    tracking_summary = tracking_details = "No tracking data available."
                else:
                    tracking_total_df = tracking_data_df[tracking_data_df['Class'] == 'Overall']
                    tracking_data_df = tracking_data_df[tracking_data_df['Class'] != 'Overall']

                    video_info = tracking_data_df[['Video', 'Timelapse Video']].drop_duplicates() if 'Video' in tracking_data_df and 'Timelapse Video' in tracking_data_df else pd.DataFrame()
                    unique_videos = video_info['Video'].unique() if not video_info.empty else []
                    num_videso = len(unique_videos)
                    timelapse_video_count = len(video_info[video_info['Timelapse Video']==True]) if 'Timelapse Video' in video_info else 0
                    tracking_summary = f"""
                            - Total Videos': {num_videso}
                            - Timelapse Video Count: {timelapse_video_count}
                            - Detections: {int(tracking_total_df['Detections'].values[0]) if 'Detections' in tracking_total_df else 0}
                            - Unique Trash: {int(tracking_total_df['Unique Trash'].values[0]) if 'Unique Trash' in tracking_total_df else 0}
                            - Avg Confidence: {float(tracking_total_df['Avg Confidence'].values[0]) if 'Avg Confidence' in tracking_total_df else 0.0}
                            - Min Confidence: {float(tracking_total_df['Min Confidence'].values[0]) if 'Min Confidence' in tracking_total_df else 0.0}
                            - Max Confidence: {float(tracking_total_df['Max Confidence'].values[0]) if 'Max Confidence' in tracking_total_df else 0.0}
                        """
                    tracking_info_df = tracking_data_df[['Class', 'Detections', 'Unique Trash']].copy()
                    tracking_class_unique = tracking_info_df.groupby('Class').agg({
                        'Detections': 'sum',
                        'Unique Trash': 'sum'
                    }).reset_index()
                    if not tracking_class_unique.empty:
                        for rec in tracking_class_unique.to_dict('records'):
                            tracking_details += f"""
                                There are {rec.get('Unique Trash', 0)} unique trash from {rec.get('Class', 'Unknown')} category , with total of {rec.get('Detections', 0)} detections.                               
                            """

            if include_metadata:
                metadata_summary = ""
                metadata_dir = Path("data/metadata")
                metadata_analysis = {}
                
                if csv_name == 'All':
                    metadata_files = list(metadata_dir.glob("*_metadata.json"))
                else:
                    metadata_files = list(metadata_dir.glob(f"{csv_name}_metadata.json"))
                for mf in metadata_files:
                    try:
                        with open(mf, 'r') as f:
                            metadata = json.load(f)
                            metadata_summary += f"""
                                The size of video {metadata.get('filename', '')} is {metadata.get('file_size_mb', 0)} MegaByte. it's duration is {metadata.get('duration_seconds', 0)} seconds, and it's frame rate is {metadata.get('fps', 0)} frames per second. 
                                it has {metadata.get('frame_count', 0)} frames. Resolution is {metadata.get('resolution', 'Unknown')}. 
                                Codec is {metadata.get('format_details', {}).get('codec', 'Unknown')}. Bitrate is {metadata.get('format_details', {}).get('bitrate', 'Unknown')}.
                            """  
                    except Exception as e:
                        continue
                
            
            trash_classes_file = Path('config/floating_litter_classes.json')
            if trash_classes_file.exists():
                try:
                    with open(trash_classes_file, 'r') as f:
                        classes_infos = json.load(f)
                except Exception as e:
                    classes_infos = {}
            if classes_infos:
                for class_details in classes_infos:
                    trash_categories_info += f"""
                        Trash category: {class_details.get('Class', 'Unknown')}, includes trash that are {class_details.get('Description', '')} - The material of this trash category can be: {', '.join(class_details.get('Material', []))}.
                    """
                   
            # Get appropriate prompts based on selected token size
            if token_size_selected == "Short":
                prompt_contexts = PromptsAI.short_prompts()
            else:
                prompt_contexts = PromptsAI.long_prompts()
            
            prompts = {
                "Data Summary & Insights": prompt_contexts[0].format(
                    metadata_summary=metadata_summary,
                    detection_summary=detection_summary,
                    detection_details=detection_details,
                    tag_details_summary=tag_details_summary,
                    trash_categories_info=trash_categories_info
                ),
                "Performance Analysis": prompt_contexts[1].format(
                    metadata_summary=metadata_summary,
                    confidence_summary=confidence_summary,
                    detection_details=detection_details,
                    tag_details_summary=tag_details_summary,
                    tracking_details=tracking_details
                ),
                "Class Distribution Analysis": prompt_contexts[2].format(
                    metadata_summary=metadata_summary,
                    detection_summary=detection_summary,
                    detection_details=detection_details,
                    tag_details_summary=tag_details_summary,
                    trash_categories_info=trash_categories_info
                ),
                "Quality Assessment": prompt_contexts[3].format(
                    metadata_summary=metadata_summary,
                    confidence_summary=confidence_summary,
                    detection_details=detection_details,
                    tag_details_summary=tag_details_summary,
                    tracking_details=tracking_details
                ),
                "Custom Query": f"""Project: FLOWT Pipeline - Marine litter detection system.
                    Based on this data, please answer: {custom_query if analysis_type == 'Custom Query' else ''}
                    Data: {detection_summary} {metadata_summary}
                """
            }
            
            # st.subheader(f"AI Analysis Results - {analysis_type}")
            
            # Generate analysis using selected provider
            analysis_result = genai_service.generate_analysis(prompts[analysis_type], provider)
            
            if analysis_result:
                st.markdown(analysis_result)
                
                # Option to show the prompt used
                # with st.expander("View Analysis Prompt"):
                #     st.code(prompts[analysis_type])
            else:
                st.error("Failed to generate analysis. Please check your API key and try again.")
else:
    st.warning("Please select a model with available data to proceed with analysis.")