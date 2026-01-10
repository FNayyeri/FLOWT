@echo off
echo 🌊 Starting FLOWT Pipeline

REM ------------------------
REM Install dependencies
REM ------------------------
python -m pip install --upgrade pip setuptools wheel
python -m pip install --no-cache-dir -r requirements.txt

REM ------------------------
REM Setup directories & models
REM ------------------------
if not exist "data\videos" mkdir data\videos
if not exist "data\results" mkdir data\results
if not exist "data\curated" mkdir data\curated
if not exist "data\tracking" mkdir data\tracking
if not exist "data\analysis" mkdir data\analysis
if not exist "data\output" mkdir data\output
if not exist "models" mkdir models
if not exist "Sample_Data" mkdir Sample_Data

if not exist "models\model1.pt" (
    echo Downloading models from Hugging Face...
    curl -L -o models\model1.pt https://huggingface.co/FNayyeri/flowt-pretrained-models/resolve/main/model1.pt
    curl -L -o models\model2.pt https://huggingface.co/FNayyeri/flowt-pretrained-models/resolve/main/model2.pt
    curl -L -o models\model3.pt https://huggingface.co/FNayyeri/flowt-pretrained-models/resolve/main/model3.pt
    curl -L -o models\model4.pt https://huggingface.co/FNayyeri/flowt-pretrained-models/resolve/main/model4.pt
)

REM ------------------------
REM Start Streamlit
REM ------------------------
echo Starting FLOWT app...
streamlit run "Flowt pipeline.py" --server.port=8001
echo ✅ FLOWT running at http://localhost:8001