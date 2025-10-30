# 🚀 Quick Start Guide

Get the TriModal XAI Backend running in 3 simple steps!

## Step 1: Install uv (if not installed)

Open PowerShell and run:

```powershell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

Close and reopen your terminal after installation.

## Step 2: Install Dependencies

Navigate to the backend directory:

```powershell
cd backend
uv sync
```

This will automatically:
- Create a virtual environment
- Install all required packages (FastAPI, TensorFlow, OpenCV, etc.)

## Step 3: Start the Server

### Option A: Using the startup script (Recommended)

```powershell
.\start_server.ps1
```

### Option B: Manual start

```powershell
uv run uvicorn app:app --reload
```

## ✅ Verify Installation

The server should start at `http://localhost:8000`

Open your browser and visit:
- **API Root**: http://localhost:8000
- **Interactive Docs**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc

## 🧪 Test the API

### Using the Swagger UI (Easiest)

1. Go to http://localhost:8000/docs
2. Click on `POST /predict`
3. Click "Try it out"
4. Upload a leaf image
5. Click "Execute"
6. See the results!

### Using the Test Script

```powershell
uv run python test_api.py
```

### Using cURL

```powershell
curl -X POST "http://localhost:8000/predict" `
  -H "accept: application/json" `
  -H "Content-Type: multipart/form-data" `
  -F "file=@your_leaf_image.jpg"
```

## 📁 Required Files

Make sure these files are in the `backend/` directory:

- ✅ `best_model.keras` - The trained model
- ✅ `knowledge_db.json` - Medicinal plant database
- ✅ `app.py` - Main FastAPI application
- ✅ `preprocessing.py` - Image preprocessing
- ✅ `model_utils.py` - Model utilities
- ✅ `xai.py` - Grad-CAM implementation
- ✅ `knowledge_utils.py` - Knowledge DB handler

## ⚡ Quick Commands

```powershell
# Install dependencies
uv sync

# Start server (development mode with auto-reload)
uv run uvicorn app:app --reload

# Start server (production mode)
uv run uvicorn app:app --host 0.0.0.0 --port 8000

# Test API
uv run python test_api.py

# Check health
curl http://localhost:8000/health

# Get supported classes
curl http://localhost:8000/classes
```

## 🎯 API Response Example

```json
{
  "predicted_class": "jasminum",
  "confidence": 0.92,
  "top3": [
    {"class": "jasminum", "confidence": 0.92},
    {"class": "nerium_oleander", "confidence": 0.05},
    {"class": "azadirachta_indica", "confidence": 0.03}
  ],
  "knowledge": {
    "Scientific Name": "Jasminum sambac",
    "Medicinal Uses": [...],
    "Active Compounds": [...],
    "Precautions": "...",
    "Sources": [...]
  },
  "gradcam_image_base64": "iVBORw0KG..."
}
```

## 🐛 Troubleshooting

### Issue: Port 8000 already in use

```powershell
# Use a different port
uv run uvicorn app:app --reload --port 8001
```

### Issue: Module not found

```powershell
# Reinstall dependencies
uv sync --reinstall
```

### Issue: TensorFlow GPU not detected

TensorFlow CPU version will work fine. GPU support requires additional setup.

### Issue: Out of memory

Reduce batch processing or use a machine with more RAM (8GB+ recommended).

## 📚 Next Steps

- Read the full [README_NEW.md](README_NEW.md) for detailed documentation
- Integrate with a frontend (Streamlit, React, etc.)
- Deploy to production (Docker, cloud services)
- Add custom preprocessing or models

## 🆘 Need Help?

Check the logs in the terminal for detailed error messages. Most issues are related to:
1. Missing dependencies (run `uv sync`)
2. Missing model file (`best_model.keras`)
3. Missing knowledge database (`knowledge_db.json`)

---

**Happy leaf classifying! 🌿🔬**
