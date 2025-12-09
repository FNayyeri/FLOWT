<<<<<<< HEAD
FROM python:3.12-slim-bookworm

WORKDIR /app

# Set non-interactive mode to prevent tzdata prompts
ENV DEBIAN_FRONTEND=noninteractive
# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    ca-certificates \
    curl \
    apt-utils \
    build-essential \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender1 \
    libgomp1 \
    libgtk-4-1 \
    tzdata && \
    rm -rf /var/lib/apt/lists/* /var/cache/apt/archives/*
=======
FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    libglib2.0-0 \
    libgtk-3-0 \
    && rm -rf /var/lib/apt/lists/*
>>>>>>> 72b8e1e1f0a7e01f097607743d6e659c209801f9

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
<<<<<<< HEAD
RUN mkdir -p data/videos data/results data/curated data/training data/output
=======
RUN mkdir -p data/videos data/results data/curated data/training data/output models/fine_tuned
>>>>>>> 72b8e1e1f0a7e01f097607743d6e659c209801f9

# Expose Streamlit port
EXPOSE 8501

# Health check
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

# Run Streamlit app
CMD ["streamlit", "run", "Flowt pipeline.py", "--server.port=8501", "--server.address=0.0.0.0"]