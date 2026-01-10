#!/bin/bash
echo "🌊 Starting FLOWT Pipeline"

# ------------------------
# Install dependencies
# ------------------------
python -m pip install --upgrade pip setuptools wheel
python -m pip install --no-cache-dir -r requirements.txt

# ------------------------
# Setup directories & models
# ------------------------
mkdir -p data/{videos,results,curated,tracking,analysis,output} models
[ ! -d "models/.git" ] && git clone --depth 1 https://huggingface.co/FNayyeri/flowt-pretrained-models models

# ------------------------
# Start Streamlit
# ------------------------
echo "Starting FLOWT app..."
streamlit run "Flowt pipeline.py" --server.port=8001
echo "✅ FLOWT running at http://localhost:8001"
