# Flowt Pipeline

## Overview
Plastic and other floating debris pose serious environmental threats, harming aquatic ecosystems, marine life, and even human health through the food chain. Automated detection powered by computer vision and AI technologies allows for real-time identification, quantification, and tracking of waste, providing accurate data for cleanup efforts, policymaking, and prevention strategies. This not only reduces labor costs and human error but also accelerates response times, helping authorities and environmental organisations protect water quality and biodiversity more effectively.

The **Flowt** is a comprehensive end-to-end computer vision pipeline for **Floating Litter Observation & Waste Tracking**. It provides a robust framework for ingesting videos, running object detection algorithm, curating results, tracking unique litter movement, and conducting deep analysis through AI services. Additionally, it generates annotated videos for quality evaluation purpose and supports iterative fine-tuning of detection models to continuously improve performance.

This pipeline is designed with scalability, ease of use, and maintainability in mind. It integrates multiple components with a consistent UI/UX and persistent configuration to streamline the workflow for environmental monitoring and research.

---

## Core Features

### 1. **📁 Data Ingestion - Video Upload**
- Supports multiple video formats: `.MP4`, `.AVI`, `.MOV`, `.MKV`, `.TLS`.
- Ingestion supports both normal and timelapse videos for flexible use cases.
- Metadata extraction on upload (duration, resolution, file size, creation time).
- Consistent `.mp4` display format for user-facing select boxes, regardless of actual underlying format.
- Timelapse videos can be explicitly marked during tracking to adjust processing parameters (e.g., disable IoU threshold).

### 2. **🔍 Inference Workflow**
- Model Selection: Support for both base models and fine-tuned models with automatic sorting by modification time
- YOLO Integration: Real-time object detection with configurable confidence thresholds
- File Overwrite Protection: Warning system when inference would overwrite existing detection, curated, tracking, or analysis files
- Results Display: Detection results table

### 4. **✏️ Curation Tools**
- Manual Review: Page-by-page review of detection results with customisable pagination
- True/False Positive Marking: Individual and bulk operations (scoped to current page)
- Classification Correction: Edit detected classes with dropdown selection
- Tagging System: Add custom tags to detections for better organisation and further analysis

### 5. **🎯 Tracking Enhancements**
- Advanced Techniques: IoU and template matching for object tracking across video frames
- Timelapse Support: Special mode for timelapse videos with disabled IoU threshold
- Configurable Parameters: Adjustable IoU and template matching thresholds
- Performance Statistics: Comprehensive tracking metrics and success rates

### 6. **🎬 Video Generation**
- Annotated Videos: Generate videos with corrected detections overlaid
- Customisable Appearance: Configurable text colors, bounding box colors and thickness
- Multiple Formats: Output support for MP4, AVI, MOV formats
- Quality Control: Selectable video quality levels (High, Medium, Low)

### 7. **📊 Analysis Pages**
- **Standard Analysis Page**:
- Detection Analytics: Comprehensive performance metrics including accuracy, precision, recall
- Class Distribution: Visual analysis of detected object classes with pie charts and histograms
- Confidence Analysis: Distribution analysis of detection confidence scores
- Tag Analytics: Frequency analysis of custom tags
- Video-Specific Analysis: Option to analyse all videos or focus on specific ones

- **AI-Powered Analysis Page**:
- LLM Integration: Support for **Google GenAI** and **OpenAI** for intelligent analysis
- Multiple Analysis Types: Performance analysis, trend identification, recommendations, and custom queries
- Data Integration: Automatic loading of curated detection data with tracking information
- API Key Management: Secure handling of API credentials with graceful fallbacks

### **🔧Iterative Fine-Tuning Workflow**
- Iterative Training: Version-controlled fine-tuning with timestamp-based model naming
- Dataset Management: Automatic dataset creation with duplicate prevention using MD5 hashing
- Performance Monitoring: False positive rate tracking and training specifications logging
- System Integration: GPU information capture and training duration tracking
- Model Lifecycle: Automatic model availability in inference after fine-tuning completion

1. **Upload curated data** through the curation page.
2. **Create a fine-tuning dataset**:
   - Prevents duplicates using MD5 hashing.
   - Sequential file naming (`img_000001.jpg`, etc.).
3. **Run training**:
   - Uses the most recent model as a baseline.
   - Logs GPU info, system specs, and training duration.
4. **Evaluate performance** using false positive monitoring.
5. **Deploy new model** for immediate use in inference.


### Technical Architecture ###
**Navigation System**
**Navigation System** is implemented for seamless transition between workflow stages in order:
  - Data Ingestion
  - Inference
  - Curation
  - Tracking
  - Video Generation
  - Analysis 
  - Fine-Tuning

- State Persistence: Cross-page video and model selection using st.session_state.nav_video and st.session_state.nav_model
- Consistent UI: Uniform video display with .mp4 extensions while handling internal file mappings
- Page Flow: Intuitive Previous/Next navigation buttons across all pages

**Configuration Management**
- YAML-Based Config: Centralised configuration in `config/config.yaml`
- Persistent Settings: User preferences automatically saved and restored
- Modular Sections: Separate configuration sections for video generation, tracking, and fine-tuning

---

## Pipeline Structure
```
FLOWT/
├── flowt/
│   ├── pages/
│   │   ├── 1_📁_Data_Ingestion.py
│   │   ├── 2_🔍_Inference.py
│   │   ├── 3_✏️_Curation.py
│   │   ├── 4_🎯_Tracking.py
│   │   ├── 5_🎬_Video_Generation.py
│   │   ├── 6_📊_Analysis.py
│   │   ├── 7_🤖_Analysis_AI.py
│   │   └── 8_🔧_Fine_Tuning.py
│   │
│   ├── data/
│   │   ├── videos/           # Original video files
│   │   ├── metadata/         # Metadata extracted from original video files
│   │   ├── results/          # Raw inference results
│   │   ├── curated/          # Manually reviewed detections
│   │   ├── tracking/         # Object tracking results
│   │   ├── output/           # generated videos after tracking process
│   │   └── analysis/         # Analysis outputs
│   │
│   ├── Flowt pipeline.py        # Main entry point
│   ├── src/
│   │   ├── curation_manager.py
│   │   ├── bbox_drawer.py
│   │   └── genai_service.py
│   │
│   ├── config/
│   │   └── config.yaml
│   │
│   ├── requirements.txt
│   ├── Dockerfile
│   └── run.sh
├── models/                       # Model storage directory - Base and active models
└── models_ft/                    # Fine-tuned model versions
```

---

## Installation

### Prerequisites
- Python 3.9+
- Docker (for containerised deployments)
- GPU support for training and inference (recommended)

### Setup
```bash
# Clone the repository
git clone https://github.com/FNayyeri/flowt-pipeline.git
cd flowt-pipeline

# Install dependencies
pip install -r requirements.txt

# Run the application
streamlit run "Flowt pipeline.py"
```

### Docker Deployment
```bash
# Build the Docker image
docker build -t flowt-pipeline .

# Run the container
docker run -p 8501:8501 flowt-pipeline
```


---

## Best Practices
- **Bulk curation operations** are scoped to the current page to avoid accidental dataset-wide changes.
- Always check overwrite warnings before running inference again.
- Keep `requirements.txt` updated when adding dependencies.
- Use unique keys for all Streamlit interactive elements to avoid conflicts.

---

## Tech Stack
- **Frontend**: Streamlit
- **Backend**: Python
- **AI Services**: Google GenAI, OpenAI
- **Containerisation**: Docker
- **Data Storage**: Local filesystem with JSON/CSV

---

## Future Improvements
- Integration with cloud storage (AWS S3, Azure Data Lake).
- Advanced analytics dashboards.
- Real-time inference via edge devices.
- Automated model evaluation reports.

---

## License
This project is licensed under the MIT License. See the `LICENSE` file for details.

---

## Contact
For inquiries or collaboration:
- **Author**: Fereshteh Nayyeri
- **Email**: [fereshteh.nayyeri@google.com]
- **Organisation**: CSIRO Data61

