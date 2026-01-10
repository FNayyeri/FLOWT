# Flowt Pipeline
## Overview

Plastic and other floating debris pose serious environmental threats, harming aquatic ecosystems, marine life, and even human health through the food chain. Automated detection powered by computer vision and AI technologies allows for real-time identification, quantification, and tracking of waste, providing accurate data for cleanup efforts, policymaking, and prevention strategies. This not only reduces labor costs and human error but also accelerates response times, helping authorities and environmental organisations protect water quality and biodiversity more effectively.

The **Flowt** pipeline is a comprehensive end-to-end computer vision framework for **Floating Litter Observation & Waste Tracking**. It provides robust tools for ingesting videos, running object detection models, reviewing and saving detection results, tracking unique litter movements, and conducting in-depth analysis through AI services. Additionally, it supports iterative fine-tuning of detection models to improve performance over time and can generate annotated videos for quality evaluation.

The pipeline is designed with scalability, ease of use, and maintainability in mind. It integrates multiple components with a consistent UI/UX and persistent configuration to streamline workflows for environmental monitoring and research.

The pipeline is divided into two main workflows, each supporting different objectives:

#### 1. Waste Tracking Workflow

This workflow, highlighted by green color in pipeline workflow diagram, focuses on applying the model for monitoring and analysis of floating litter. The sequential steps include:

Data Ingestion ──> Scanning ──> Review the Detections ──> Tracking ──> Analysis ──> Video Generation
- Provides detection results review and correction.
- Tracks unique litter objects across frames.
- Performs in-depth analysis and generates annotated videos for reporting.

#### 2. Model Improvement Workflow

This workflow, highlighted by red color in pipeline workflow diagram, focuses on improving the detection model’s performance through iterative training. The sequential steps include:

Data Ingestion ──> Scanning ──> Review the Detections ──> Model Refinement
- Used to create high-quality training datasets.
- Enables version-controlled fine-tuning of models.
- Automatically integrates improved models back into the inference workflow.

## Overview
## Technical Architecture ###
**Navigation System** is implemented for seamless transition between workflow stages in order with following featurs.

- State Persistence: Cross-page model and video selection
- Consistent UI: Uniform video display with .mp4 extensions while handling internal file mappings
- Page Flow: Intuitive Previous/Next navigation buttons across all pages

**Configuration Management**
- YAML-Based Config: Centralised configuration in `config/config.yaml`
- Persistent Settings: User preferences automatically saved and restored
- Modular Sections: Separate configuration sections for video generation, tracking, and fine-tuning


## Pipeline Structure
```
FLOWT/
├── pages/                  # Streamlit UI Pages
│   ├── 1_Data_Ingestion.py
│   ├── 2_Scanning.py
│   ├── 3_Review.py
│   ├── 4_Tracking.py
│   ├── 5_Video_Generation.py
│   ├── 6_Trash_Analysis.py
│   ├── 7_AI_Insight.py
│   ├── 8_Model_Refining.py
│   ├── 9_Edge_Deployment.py
│   └── Documentation.py
├── Flowt pipeline.py        
├── src/
├── config/
│   ├── config.yaml
│   └── floating_litter_classes.json
├── docs/  
│   ├── README.md 
│   ├── Features.md
│   ├── installation.md
│   ├── Model_Cards.md
│   └── LICENCE
├── requirements.txt
├── Dockerfile
├── flowt.sh                  # Mac/Linux entry point
├── flowt_win.sh              # Windows entry point
└── models/                   # Model storage directory - Base and active models
```

## Setup

## Setup

### Mac/Linux
1. Install Homebrew if missing:
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```
2. Install pyenv & pyenv-virtualenv if missing:
```bash
brew install pyenv pyenv-virtualenv
```
3. Install Python & venv if missing:
```bash
pyenv install 3.11.8 && pyenv virtualenv 3.11.8 flowt-venv
```
4. Run:
```bash
./flowt.sh
```

### Windows
1. Install Python from [python.org](https://www.python.org/downloads/)
2. Install virtualenv:
```cmd
pip install virtualenv
```
3. Create virtual environment:
```cmd
python -m venv flowt-venv && flowt-venv\Scripts\activate
```
4. Run:
```cmd
./flowt_win.sh
```

Access the application at `http://localhost:8001`

## Tech Stack
- **Frontend**: Streamlit
- **Backend**: Python
- **AI Services**: OpenAI
- **Containerisation**: Docker
- **Data Storage**: Local filesystem with JSON/CSV

## Future Improvements
- Real-time inference via edge devices.
- Integration with cloud storage (AWS S3, Azure Data Lake).

## License
The original code and documentation developed as part of this pipeline are released under the `Creative Commons Attribution 4.0 International (CC BY 4.0)` license. This license permits users to share, adapt, and reuse the work,
including for commercial purposes, provided that appropriate attribution is given to the original author.

## Paper
[CSIRO Publication](https://publications.csiro.au/publications/publication/PIcsiro:EP2026-0022/SQnayyeri/RP1/RS25/RORECENT/STsearch-by-keyword/LISEA/RI1/RT4)

[Detailed Documentation (PDF)](FlowtPipeline-FloatingLitterObservation&WasteTracking.pdf)

## Youtube Demo
[FLOWT in Action: AI-Powered Floating Litter Observation & Waste Tracking](https://www.youtube.com/watch?v=Pkm2afZjb54)


## Contact
For inquiries or collaboration:
- **Author**: Fereshteh Nayyeri
- **Email**: [fereshteh.nayyeri@gmail.com]

