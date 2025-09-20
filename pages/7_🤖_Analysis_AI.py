import streamlit as st
from pathlib import Path
import sys
import json
sys.path.append(str(Path(__file__).parent.parent))
from src.genai_service import GenAIService

st.set_page_config(page_title="AI-Powered Analysis", page_icon="🤖")

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
    border: 1px solid #ccc !important;
}

.stButton > button {
    white-space: nowrap !important;
}
</style>
""", unsafe_allow_html=True)
st.title("🤖 AI-Powered Analysis")
st.markdown("AI-powered analysis of marine litter detection data using Large Language Models.")

# Navigation buttons
col1, col2, col3 = st.columns([1, 6, 1])
with col1:
    if st.button("◀ Previous", type="primary"):
        st.switch_page("pages/6_📊_Analysis.py")
with col3:
    if st.button("Next ▶", type="primary"):
        st.switch_page("pages/1_📁_Data_Ingestion.py")
st.markdown('<hr style="margin: 5px 0; border: 1px solid #ddd;">', unsafe_allow_html=True)
# Initialize GenAI service
genai_service = GenAIService()
available_providers = genai_service.get_available_providers()

# Configuration
st.header("Configuration")
col_config, col_ai = st.columns(2)

with col_config:
    st.subheader("Data Configuration")
    curated_base_dir = Path("data/curated")
    if curated_base_dir.exists():
        model_dirs = [d for d in curated_base_dir.iterdir() if d.is_dir()]
        
        if model_dirs:
            col1, col2 =  st.columns(2)
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
                # Get curated files for selected model
                model_curated_dir = curated_base_dir / selected_model
                if model_curated_dir.exists():
                    curated_files = list(model_curated_dir.glob("*_curated_detections.json"))
                    video_options = ["All"] + [f.stem.replace('_curated_detections', '') for f in curated_files]
                else:
                    video_options = ["All"]
                
                # Use nav_video if available
                default_video = st.session_state.get('nav_video', video_options[0] if video_options else "All")
                if default_video not in video_options:
                    default_video = video_options[0] if video_options else "All"
                
                selected_video = st.selectbox("Select Video", video_options, index=video_options.index(default_video) if default_video in video_options else 0)
                st.session_state.nav_video = selected_video
        else:
            st.warning("No models found.")
            selected_model = None
            curated_files = []
    else:
        st.warning("No curated data directory found.")
        selected_model = None
        curated_files = []

with col_ai:
    st.subheader("Analysis Configuration")
    if available_providers:
        col1, col2= st.columns(2)
        with col1:
            # Data source selection
            data_source = st.selectbox(
                "Results Type",
                ["Both Curated Detection & Tracking", "Curated Detection", "Tracking"]
            )
        with col2:    
            # Analysis type selection
            analysis_type = st.selectbox(
                "Analysis Type",
                [
                    "Data Summary & Insights",
                    "Performance Analysis",
                    "Class Distribution Analysis",
                    "Quality Assessment",
                    "Custom Query"
                ]
            )
        # AI Provider info (first available provider)
        provider = available_providers[0]
        provider_name = "Google GenAI" if provider == "google" else "OpenAI"
        st.info(f"AI Provider: {provider_name}")
    else:
        st.warning("⚠️ Please configure an AI provider first.")
        provider = None
        data_source = "Both Curated Detection & Tracking"
        analysis_type = "Data Summary & Insights"
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
            # Load data based on source selection
            detection_data = []
            tracking_data = []
            
            # Load detection data
            if data_source in ["Curated Detection", "Both Curated Detection & Tracking"]:
                if selected_video == "All":
                    for curated_file in curated_files:
                        try:
                            with open(curated_file, 'r') as f:
                                file_data = json.load(f)
                                if file_data and isinstance(file_data, list):
                                    detection_data.extend(file_data)
                        except Exception as e:
                            st.error(f"Error loading {curated_file}: {str(e)}")
                else:
                    model_curated_dir = curated_base_dir / selected_model
                    specific_file = model_curated_dir / f"{selected_video}_curated_detections.json"
                    try:
                        with open(specific_file, 'r') as f:
                            file_data = json.load(f)
                            if file_data and isinstance(file_data, list):
                                detection_data = file_data
                    except Exception as e:
                        st.error(f"Error loading detection data: {str(e)}")
            
            # Load tracking data
            if data_source in ["Tracking", "Both Curated Detection & Tracking"]:
                tracking_base_dir = Path("data/tracking") / selected_model
                if tracking_base_dir.exists():
                    if selected_video == "All":
                        tracking_files = list(tracking_base_dir.glob("*_tracking.json"))
                        for tracking_file in tracking_files:
                            try:
                                with open(tracking_file, 'r') as f:
                                    file_data = json.load(f)
                                    if file_data and isinstance(file_data, list):
                                        tracking_data.extend(file_data)
                                        # st.success(f"Extended tracking_data with {len(file_data)} items")
                                    elif file_data and isinstance(file_data, dict):
                                        # Convert dict values to list for tracking data
                                        for key, value in file_data.items():
                                            if isinstance(value, list):
                                                tracking_data.extend(value)
                            except Exception as e:
                                st.error(f"Error loading {tracking_file}: {str(e)}")
                    else:
                        tracking_file = tracking_base_dir / f"{selected_video}_tracking.json"
                        # st.info(f"Looking for specific tracking file: {tracking_file}")
                        try:
                            with open(tracking_file, 'r') as f:
                                file_data = json.load(f)
                                if file_data and isinstance(file_data, list):
                                    tracking_data = file_data
                                elif file_data and isinstance(file_data, dict):
                                    # Convert dict values to list for tracking data
                                    tracking_data = []
                                    for key, value in file_data.items():
                                        if isinstance(value, list):
                                            tracking_data.extend(value)
                        except Exception as e:
                            st.error(f"Error loading tracking data: {str(e)}")
                else:
                    st.warning(f"Tracking directory does not exist: {tracking_base_dir}")
            
            # Combine data for analysis (ensure both are lists)
            all_data = (detection_data if isinstance(detection_data, list) else []) + (tracking_data if isinstance(tracking_data, list) else [])

            if not all_data:
                st.error("No data found for the selected configuration.")
            else:
                # Prepare data summary for LLM
                detection_data = detection_data if isinstance(detection_data, list) else []
                tracking_data = tracking_data if isinstance(tracking_data, list) else []
                total_detections = len(detection_data)
                total_tracks = len(tracking_data)
                true_positives = sum(1 for d in detection_data if d.get('is_true_positive', False))
                false_positives = total_detections - true_positives
                
                # Analysis based on data source
                data_summary_parts = []
                
                if detection_data:
                    # Detection data analysis
                    classes = {}
                    for d in detection_data:
                        class_name = d.get('corrected_class', d.get('class', 'Unknown'))
                        classes[class_name] = classes.get(class_name, 0) + 1
                    
                    confidences = [d.get('confidence', 0) for d in detection_data]
                    avg_confidence = sum(confidences) / len(confidences) if confidences else 0
                    
                    all_tags = []
                    for d in detection_data:
                        if 'tags' in d and d['tags']:
                            all_tags.extend(d['tags'])
                    
                    accuracy = true_positives/total_detections*100 if total_detections > 0 else 0
                    data_summary_parts.append(f"""
                        Detection Data:
                        - Total Detections: {total_detections}
                        - True Positives: {true_positives}
                        - False Positives: {false_positives}
                        - Accuracy: {accuracy:.1f}%
                        - Average Confidence: {avg_confidence:.2f}
                        - Class Distribution: {dict(sorted(classes.items(), key=lambda x: x[1], reverse=True))}
                        - Common Tags: {list(set(all_tags))}
                    """)
                
                if tracking_data:
                    # Tracking data analysis
                    track_ids = set()
                    for t in tracking_data:
                        track_id = t.get('track_id')
                        if track_id:
                            track_ids.add(track_id)
                    
                    # Calculate track lengths
                    track_frames = {}
                    for t in tracking_data:
                        track_id = t.get('track_id')
                        if track_id:
                            if track_id not in track_frames:
                                track_frames[track_id] = []
                            track_frames[track_id].append(t.get('frame', 0))
                    
                    track_lengths = []
                    for track_id, frames in track_frames.items():
                        track_lengths.append(max(frames) - min(frames) + 1 if frames else 0)
                    
                    avg_track_length = sum(track_lengths) / len(track_lengths) if track_lengths else 0
                    track_dist = sorted(track_lengths) if len(track_lengths) <= 10 else f"Min: {min(track_lengths)}, Max: {max(track_lengths)}, Avg: {avg_track_length:.1f}"
                    
                    data_summary_parts.append(f"""
                        Tracking Data:
                        - Total Tracking Points: {total_tracks}
                        - Unique Tracks: {len(track_ids)}
                        - Average Track Length: {avg_track_length:.1f} frames
                        - Track Length Distribution: {track_dist}
                    """)
                
                data_summary = "\n".join(data_summary_parts)
                
                # Project context
                project_context = """Project: Flowt Pipeline - Floating Litter Observation & Waste Tracking
Purpose: Automated detection of plastic and floating debris in waterways using computer vision and AI to protect aquatic ecosystems, marine life, and human health.

Litter Classes (26 categories): Packaging (colorful branded materials), Other_packaging (plain/metallic), S_bubblewrap, S_label, S_squeeze, S_straw, PS_string, P_cardboard, P_foodcontainer, PH_cup, H_packaging, H_beveragebottle, H_otherbottle, H_plate/bowl, H_utensil, DH_lid, D_polystyrene, M_beveragecan, M_foodcan/tin, M_aerosol, R_ball/balloon, G_beveragebottle, F_facemask, T_wood/timber, Other.

Materials: Soft/Hard Plastic, Cardboard, Paper, Thin Film, Aluminium, Polystyrene, Metal, Rubber, Glass, Fabric, Timber."""
                
                # Define analysis prompts based on data source
                data_type_desc = {
                    "Curated Detection": "marine litter detection",
                    "Tracking": "marine litter tracking", 
                    "Both Curated Detection & Tracking": "combined marine litter detection and tracking"
                }[data_source]
                
                prompts = {
                    "Data Summary & Insights": f"{project_context}\n\nAnalyse this {data_type_desc} data and provide key insights, trends, and observations considering the environmental impact of different material types:\n{data_summary}",
                    "Performance Analysis": f"{project_context}\n\nEvaluate the performance of this {data_type_desc} system. Focus on accuracy across the 26 litter classes, precision patterns for different materials, and areas for improvement:\n{data_summary}",
                    "Class Distribution Analysis": f"{project_context}\n\nAnalyse the class distribution in this {data_type_desc} dataset. Consider material composition, environmental persistence, and potential impact on marine ecosystems:\n{data_summary}",
                    "Quality Assessment": f"{project_context}\n\nAssess the quality of this {data_type_desc} dataset considering the 26 litter classes and material types. Evaluate accuracy, confidence levels, and data completeness:\n{data_summary}",
                    "Custom Query": f"{project_context}\n\nBased on this {data_type_desc} data, please answer: {custom_query if analysis_type == 'Custom Query' else ''}\n\nData:\n{data_summary}"
                }
                
                st.subheader("AI Analysis Results")
                
                # Generate analysis using selected provider
                analysis_result = genai_service.generate_analysis(prompts[analysis_type], provider)
                
                if analysis_result:
                    st.markdown(analysis_result)
                    
                    # Option to show the prompt used
                    with st.expander("View Analysis Prompt"):
                        st.code(prompts[analysis_type])
                else:
                    st.error("Failed to generate analysis. Please check your API key and try again.")
else:
    st.warning("Please select a model with available data to proceed with analysis.")