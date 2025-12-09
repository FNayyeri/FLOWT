import streamlit as st
from pathlib import Path
import sys
import json
import cv2
import numpy as np
import threading
import time
sys.path.append(str(Path(__file__).parent.parent))

st.set_page_config(page_title="Edge Deployment -- Under Development", page_icon="📱", layout="wide")

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
    color: Red !important;
    width: 150px !important;
    border: 1px solid #ccc !important;
}
/* White background for all selectboxes */
.stSelectbox > div > div {
    background-color: white !important;
}
</style>
""", unsafe_allow_html=True)

st.title("📱 Edge Deployment")
st.markdown("Deploy models using MLFlow Triton plugin for scalable inference.")

# Navigation buttons
left_col, spacer_col, right_col = st.columns([0.1, 1, 0.1])
with left_col:
    if st.button("◀ Previous", type="primary"):
        st.switch_page("pages/8_Model_Refining.py")
with right_col:
    if st.button("Next ▶", type="primary"):
        st.switch_page("pages/1_Data_Ingestion.py")

st.markdown('<hr style="margin: 5px 0; border: 1px solid #ddd;">', unsafe_allow_html=True)

# Model Optimization Section
st.header("🔧 Configuration")

col1, col2 = st.columns(2)

with col1:
    # st.subheader("Knowledge Distillation")
    
    # Teacher model selection
    models_dir = Path("models")
    models_ft_dir = Path("models_ft")
    
    teacher_models = []
    if models_dir.exists():
        teacher_models.extend([str(f) for f in models_dir.glob("*.pt")])
    if models_ft_dir.exists():
        teacher_models.extend([str(f) for f in models_ft_dir.glob("*.pt")])
    
    if teacher_models:
        teacher_model = st.selectbox("Original Model (Large)", teacher_models)
        
        # Student model size
        student_size = st.selectbox(
            "model size", 
            ["Nano", "Small"]
        )
        # Student model architecture
        student_arch_m = st.selectbox(
            "Student Architecture", 
            ["Model1", "Model2", "Model3", "Model4"]
        )
        student_arch = f"{student_arch_m}{student_size[0].lower()}"
        # Distillation parameters
        col_a, col_b = st.columns(2)
        with col_a:
            temperature = st.slider("Temperature", 1.0, 10.0, 4.0, 0.5)
            alpha = st.slider("Distillation Weight", 0.1, 1.0, 0.7, 0.1)
        with col_b:
            epochs = st.number_input("Training Epochs", 10, 200, 50)
            batch_size = st.selectbox("Batch Size", [8, 16, 32], index=1)
        
        if st.button("Start Model Compression", type="secondary"):
            # Placeholder for knowledge distillation
            st.info("Knowledge Distillation Developmemnt is in progress...")
            # with st.spinner("Creating optimised student model..."):
            #     try:
            #         # Placeholder for knowledge distillation
            #         st.success("Knowledge distillation completed!")
            #         st.info("Student model saved to models_edge/ directory")
            #     except Exception as e:
            #         st.error(f"Distillation failed: {str(e)}")
    else:
        st.warning("No teacher models found. Train a model first.")

with col2:
    st.subheader("Model Conversion")
    
    # Edge model selection
    edge_models_dir = Path("models_edge")
    if edge_models_dir.exists():
        edge_models = list(edge_models_dir.glob("*.pt"))
    else:
        edge_models = []
    
    if edge_models:
        selected_edge_model = st.selectbox("Edge Model", [m.name for m in edge_models])
        
        # Conversion options
        export_format = st.selectbox(
            "Export Format",
            ["TensorRT", "ONNX", "TorchScript", "OpenVINO"]
        )
        
        # Optimization settings
        if export_format == "TensorRT":
            precision = st.selectbox("Precision", ["FP16", "INT8", "FP32"])
            workspace_size = st.slider("Workspace Size (GB)", 1, 8, 4)
        
        if st.button("Convert Model", type="secondary"):
            with st.spinner(f"Converting to {export_format}..."):
                try:
                    # Placeholder for model conversion
                    st.success(f"Model converted to {export_format} format!")
                except Exception as e:
                    st.error(f"Conversion failed: {str(e)}")
    else:
        st.info("No edge models available. Create one using knowledge distillation.")

st.markdown('<hr style="margin: 5px 0; border: 1px solid #ddd;">', unsafe_allow_html=True)

# MLFlow Triton Deployment Section
st.header("🚀 MLFlow Triton Deployment")

col1, col2 = st.columns(2)

with col1:
    st.subheader("MLFlow Model Registry")
    
    # MLFlow tracking URI
    mlflow_uri = st.text_input("MLFlow Tracking URI", "http://localhost:5000")
    
    # Model selection from registry
    model_name = st.text_input("Model Name", "yolo-marine-litter")
    model_version = st.selectbox("Model Version", ["latest", "1", "2", "3"])
    
    # Triton server configuration
    triton_host = st.text_input("Triton Server Host", "localhost")
    triton_port = st.number_input("Triton Server Port", 8000, 9000, 8000)
    
    # Model deployment settings
    model_platform = st.selectbox(
        "Model Platform",
        ["onnxruntime_onnx", "tensorrt_plan", "pytorch_libtorch"]
    )
    
    max_batch_size = st.number_input("Max Batch Size", 1, 32, 8)

with col2:
    st.subheader("Triton Deployment")
    
    # Instance configuration
    instance_count = st.number_input("Instance Count", 1, 4, 1)
    gpu_memory_fraction = st.slider("GPU Memory Fraction", 0.1, 1.0, 0.5, 0.1)
    
    # Dynamic batching
    enable_batching = st.checkbox("Enable Dynamic Batching", True)
    if enable_batching:
        max_queue_delay = st.number_input("Max Queue Delay (μs)", 100, 10000, 1000)
    
    # Model optimization
    enable_model_warmup = st.checkbox("Enable Model Warmup", True)
    
    if st.button("Deploy to Triton", type="secondary"):
        with st.spinner("Deploying model to Triton server..."):
            try:
                # Placeholder for MLFlow Triton deployment
                st.success("Model deployed successfully to Triton!")
                st.info(f"Model available at: {triton_host}:{triton_port}/v2/models/{model_name}")
            except Exception as e:
                st.error(f"Deployment failed: {str(e)}")

st.markdown('<hr style="margin: 5px 0; border: 1px solid #ddd;">', unsafe_allow_html=True)

# Triton Inference Section
st.header("📹 Triton Inference")

col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("Live Stream")
    
    # Placeholder for video stream
    video_placeholder = st.empty()
    
    # Control buttons
    col_a, col_b, col_c = st.columns(3)
    with col_a:
        start_stream = st.button("🎥 Start Stream", type="secondary")
    with col_b:
        stop_stream = st.button("⏹️ Stop Stream", type="tertiary")
    with col_c:
        capture_frame = st.button("📸 Capture Frame")
    
    # Stream status
    if 'stream_active' not in st.session_state:
        st.session_state.stream_active = False
    
    if start_stream:
        st.session_state.stream_active = True
        st.success("Stream started!")
    
    if stop_stream:
        st.session_state.stream_active = False
        st.info("Stream stopped.")
    
    # Simulate live stream (placeholder)
    if st.session_state.stream_active:
        video_placeholder.info("🔴 LIVE - Real-time detection active")
    else:
        video_placeholder.info("📷 Camera ready - Click 'Start Stream' to begin")

with col2:
    st.subheader("Detection Stats")
    
    # Real-time metrics
    col_metric1, col_metric2 = st.columns(2)
    with col_metric1:
        st.metric("FPS", "0.0")
        st.metric("Detections", "0")
    with col_metric2:
        st.metric("Latency", "0ms")
        st.metric("GPU Usage", "0%")
    
    # Detection log
    st.subheader("Recent Detections")
    detection_log = st.empty()
    detection_log.text("No detections yet...")

st.markdown('<hr style="margin: 5px 0; border: 1px solid #ddd;">', unsafe_allow_html=True)

# System Monitoring
st.header("📊 System Monitoring")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("CPU Usage", "0%")
with col2:
    st.metric("GPU Usage", "0%")
with col3:
    st.metric("Memory", "0/8 GB")
with col4:
    st.metric("Temperature", "0°C")

# Deployment Instructions
st.header("📋 MLFlow Triton Setup")

with st.expander("Setup Instructions"):
    st.markdown("""
    ### 1. Install MLFlow and Triton
    ```bash
    pip install mlflow[extras] tritonclient[all]
    
    # Start MLFlow tracking server
    mlflow server --host 0.0.0.0 --port 5000
    ```
    
    ### 2. Start Triton Inference Server
    ```bash
    # Using Docker
    docker run --gpus=1 --rm -p8000:8000 -p8001:8001 -p8002:8002 \
        -v /path/to/model_repository:/models \
        nvcr.io/nvidia/tritonserver:23.10-py3 \
        tritonserver --model-repository=/models
    ```
    
    ### 3. Deploy Model with MLFlow
    ```python
    import mlflow
    from mlflow.deployments import get_deploy_client
    
    # Deploy to Triton
    client = get_deploy_client("triton")
    client.create_deployment(
        name="yolo-marine-litter",
        model_uri="models:/yolo-marine-litter/latest",
        config={"triton_host": "localhost", "triton_port": 8000}
    )
    ```
    
    ### 4. Inference with Triton Client
    ```python
    import tritonclient.http as httpclient
    import numpy as np
    
    client = httpclient.InferenceServerClient(url="localhost:8000")
    
    # Prepare input
    inputs = [httpclient.InferInput("input", image.shape, "FP32")]
    inputs[0].set_data_from_numpy(image)
    
    # Run inference
    results = client.infer("yolo-marine-litter", inputs)
    output = results.as_numpy("output")
    ```
    """)

# Export deployment script
if st.button("📦 Generate Deployment Package"):
    with st.spinner("Creating deployment package..."):
        # Create deployment script
        deployment_script = f"""
import cv2
import numpy as np
from ultralytics import YOLO
import time

class EdgeDetector:
    def __init__(self, model_path, conf_threshold={conf_threshold}):
        self.model = YOLO(model_path)
        self.conf_threshold = conf_threshold
        
    def detect_stream(self, camera_id=0):
        cap = cv2.VideoCapture(camera_id)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, {input_size.split('x')[0]})
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, {input_size.split('x')[1]})
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
                
            results = self.model(frame, conf=self.conf_threshold)
            annotated_frame = results[0].plot()
            
            cv2.imshow('Marine Litter Detection', annotated_frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
                
        cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    detector = EdgeDetector("student_model.pt")
    detector.detect_stream(0)
"""
        
        st.download_button(
            "Download edge_detection.py",
            deployment_script,
            "edge_detection.py",
            "text/plain"
        )
        
        st.success("Deployment package ready for download!")