#!/bin/bash

# FLOWT - Floating Litter Observation & Waste Tracking
# Quick start script

echo "🌊 Starting FLOWT - Floating Litter Observation & Waste Tracking Pipeline"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install requirements
echo "Installing requirements..."
pip install -r requirements.txt

# Create necessary directories
echo "Setting up directories..."
mkdir -p data/{videos,results,curated,tracking,training,output}
mkdir -p models/fine_tuned

# Start Streamlit app
echo "Starting FLOWT application..."
streamlit run "Flowt pipeline.py" --server.port=8501

echo "✅ FLOWT is running at http://localhost:8501"