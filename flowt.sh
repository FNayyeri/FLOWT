#!/bin/bash
echo "🌊 Starting FLOWT Pipeline"

export PYENV_ROOT="$HOME/.pyenv"
export PATH="$PYENV_ROOT/bin:$PATH"
eval "$(pyenv init --path)"
eval "$(pyenv virtualenv-init -)"

# ------------------------
# Install dependencies
# ------------------------
python -m pip install --upgrade pip setuptools wheel
python -m pip install --no-cache-dir -r requirements.txt

# ------------------------
# Setup directories & models
# ------------------------
mkdir -p data/{videos,results,curated,tracking,analysis,output} models Sample_Data
if [ ! -f "models/model1.pt" ]; then
    echo "Downloading models from Hugging Face..."
    curl -L -o models/model1.pt https://huggingface.co/FNayyeri/flowt-pretrained-models/resolve/main/model1.pt
    curl -L -o models/model2.pt https://huggingface.co/FNayyeri/flowt-pretrained-models/resolve/main/model2.pt
    curl -L -o models/model3.pt https://huggingface.co/FNayyeri/flowt-pretrained-models/resolve/main/model3.pt
    curl -L -o models/model4.pt https://huggingface.co/FNayyeri/flowt-pretrained-models/resolve/main/model4.pt
fi

# ------------------------
# Start Streamlit
# ------------------------
echo "Starting FLOWT app..."
streamlit run "Flowt pipeline.py" --server.port=8001
echo "✅ FLOWT running at http://localhost:8001"
