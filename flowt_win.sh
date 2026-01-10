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

if not exist "models\.git" (
    git clone --depth 1 https://huggingface.co/FNayyeri/flowt-pretrained-models models
)

REM ------------------------
REM Start Streamlit
REM ------------------------
echo Starting FLOWT app...
streamlit run "Flowt pipeline.py" --server.port=8001
echo ✅ FLOWT running at http://localhost:8001