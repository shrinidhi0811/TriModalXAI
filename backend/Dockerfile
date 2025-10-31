# Use Python 3.11 slim image for smaller size
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    TF_ENABLE_ONEDNN_OPTS=0 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies required for OpenCV, scikit-image, and rembg
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender1 \
    libgomp1 \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency files first (for better caching)
COPY pyproject.toml ./
COPY requirements.txt ./

# Install Python dependencies using pip
# Upgrade pip first for better dependency resolution
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app.py .
COPY preprocessing.py .
COPY model_utils.py .
COPY xai.py .
COPY knowledge_utils.py .
COPY custom_layers.py .
COPY config.py .

# Copy model and data files
COPY best_model.keras .
COPY knowledge_db.json .

# Create directory for temporary files
RUN mkdir -p /tmp/gradcam

# Expose port (Render will set PORT environment variable)
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run the application
# Render will override PORT, so we use ${PORT:-8000}
CMD uvicorn app:app --host 0.0.0.0 --port ${PORT:-8000} --workers 1
