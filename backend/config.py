"""
Configuration file for the TriModal XAI Backend.
Modify these settings as needed for your deployment.
"""

import os
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).parent

# Model configuration
MODEL_PATH = BASE_DIR / "best_model.keras"
KNOWLEDGE_DB_PATH = BASE_DIR / "knowledge_db.json"

# Model settings
IMG_SIZE = (224, 224)
NUM_CLASSES = 7
CLASSES = [
    "alpinia_galanga",
    "azadirachta_indica",
    "basella_alba",
    "jasminum",
    "nerium_oleander",
    "plectranthus_amboinicus",
    "trigonella_foenum_graecum"
]

# Grad-CAM settings
GRADCAM_LAYER = "fused_reduce"  # Last convolutional layer name
USE_GRADCAM_PLUS_PLUS = True    # Use Grad-CAM++ (vs standard Grad-CAM)

# API settings
API_TITLE = "TriModal Medicinal Leaf Classifier"
API_DESCRIPTION = "AI-powered medicinal leaf identification with explainable AI"
API_VERSION = "1.0.0"

# CORS settings (for frontend integration)
CORS_ORIGINS = [
    "http://localhost:3000",      # React default
    "http://localhost:8501",      # Streamlit default
    "http://localhost:5173",      # Vite default
    "http://127.0.0.1:3000",
    "http://127.0.0.1:8501",
    "http://127.0.0.1:5173",
]
# For production, replace with specific origins:
# CORS_ORIGINS = ["https://yourdomain.com"]

# Server settings (when running directly with python)
HOST = "0.0.0.0"
PORT = 8000
RELOAD = True  # Set to False in production

# File upload settings
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}

# Preprocessing settings
VEIN_CLAHE_CLIP_LIMIT = 2.0
VEIN_CLAHE_GRID_SIZE = (8, 8)
VEIN_FRANGI_SCALE_RANGE = (1, 4)
VEIN_FRANGI_SCALE_STEP = 1
VEIN_MORPH_KERNEL_SIZE = (5, 5)

TEXTURE_LBP_RADIUS = 2
TEXTURE_LBP_POINTS = 16  # 8 * radius
TEXTURE_LBP_METHOD = "uniform"
TEXTURE_GABOR_FREQUENCIES = [0.2, 0.3]
TEXTURE_GABOR_ORIENTATIONS = [0, 0.785, 1.571, 2.356]  # 0, π/4, π/2, 3π/4
TEXTURE_UNSHARP_RADIUS = 1
TEXTURE_UNSHARP_AMOUNT = 1

# Logging settings
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# Environment-specific settings
DEBUG = os.getenv("DEBUG", "True").lower() == "true"
ENV = os.getenv("ENV", "development")  # development, staging, production

# TensorFlow settings
TF_ENABLE_GPU_MEMORY_GROWTH = True
TF_LOG_LEVEL = "2"  # 0=all, 1=info, 2=warning, 3=error
