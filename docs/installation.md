## Installation

### Prerequisites
- Python 3.9+
- Docker (for containerised deployments)
- GPU support for fine-tuning and inference (recommended)

### Setup
```bash
# Clone the repository
git clone https://github.com/FNayyeri/FLOWT.git
cd FLOWT

# Run the application
./flowt.sh
```

### Docker Deployment
```bash
# Build the Docker image
docker build -t flowt-pipeline .

# Run the container
docker run -p 8501:8501 flowt-pipeline
```
