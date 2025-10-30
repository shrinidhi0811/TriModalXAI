# TriModal XAI Backend

FastAPI backend for tri-modal medicinal leaf classification with explainable AI (Grad-CAM++).

## 🌿 Overview

This backend provides an AI-powered API for identifying medicinal leaves using a tri-modal deep learning approach:
- **RGB imaging** - Original leaf appearance
- **Vein-enhanced imaging** - Vein structure analysis using CLAHE + Frangi filter
- **Texture-enhanced imaging** - Texture patterns using LBP + Gabor filters

The model classifies 7 medicinal plant species and provides:
- Top-3 predictions with confidence scores
- Medicinal knowledge (uses, compounds, precautions)
- Grad-CAM++ heatmap visualization for explainability

## 📋 Supported Classes

1. `alpinia_galanga` - Greater Galangal
2. `azadirachta_indica` - Neem
3. `basella_alba` - Malabar Spinach
4. `jasminum` - Jasmine
5. `nerium_oleander` - Oleander
6. `plectranthus_amboinicus` - Indian Borage
7. `trigonella_foenum_graecum` - Fenugreek

## 🏗️ Project Structure

```
backend/
├── app.py                  # FastAPI entrypoint with /predict route
├── preprocessing.py        # Background removal, vein & texture enhancement
├── model_utils.py         # Model loading and inference utilities
├── xai.py                 # Grad-CAM and Grad-CAM++ implementation
├── knowledge_utils.py     # Knowledge database handler
├── best_model.keras       # Trained tri-modal model
├── knowledge_db.json      # Medicinal plant information database
├── pyproject.toml         # uv project configuration
└── README.md              # This file
```

## 🚀 Setup & Installation

### Prerequisites

- Python 3.9+
- [uv](https://github.com/astral-sh/uv) package manager

### Install uv (if not already installed)

**Windows (PowerShell):**
```powershell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

**Linux/macOS:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Install Dependencies

Navigate to the backend directory and install all dependencies:

```powershell
cd backend
uv sync
```

This will create a virtual environment and install all required packages including:
- FastAPI & Uvicorn
- TensorFlow
- OpenCV
- scikit-image
- rembg (background removal)
- Pillow, NumPy

## 🎯 Usage

### Run the Server

```powershell
uv run uvicorn app:app --reload
```

The server will start at: `http://localhost:8000`

### API Endpoints

#### 1. **Health Check**
```
GET /
GET /health
```

#### 2. **Get Supported Classes**
```
GET /classes
```

#### 3. **Predict (Main Endpoint)**
```
POST /predict
Content-Type: multipart/form-data
```

**Request:**
- Upload an image file (JPG/PNG) of a medicinal leaf

**Response:**
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
    "Medicinal Uses": [
      "Aromatherapeutic uses (stress relief, calming)",
      "Used in traditional medicine for skin diseases, wounds",
      "Used as anti‑inflammatory agent in folk remedies"
    ],
    "Active Compounds": [
      "Jasminoids, jasmine lactones",
      "Flavonoids",
      "Essential oils (linalool, benzyl acetate, eugenol)"
    ],
    "Precautions": "May cause skin sensitivity...",
    "Sources": ["Ethnobotanical reviews...", "..."]
  },
  "gradcam_image_base64": "iVBORw0KGgoAAAANSUhEUgAA..."
}
```

### Test with cURL

```powershell
curl -X POST "http://localhost:8000/predict" `
  -H "accept: application/json" `
  -H "Content-Type: multipart/form-data" `
  -F "file=@path/to/leaf_image.jpg"
```

### Test with Python

```python
import requests

url = "http://localhost:8000/predict"
files = {"file": open("leaf_image.jpg", "rb")}
response = requests.post(url, files=files)
print(response.json())
```

## 🧪 Testing the API

You can test the API using:

1. **Swagger UI**: Visit `http://localhost:8000/docs`
2. **ReDoc**: Visit `http://localhost:8000/redoc`
3. **cURL/Postman**: Use the examples above
4. **Python script**: Use the requests library

## 🔬 Model Architecture

The model uses a tri-modal architecture:

1. **Three Parallel Branches** (RGB, Vein, Texture)
   - MobileNetV3Large backbone (feature extraction)
   - ECA Attention (channel-wise)
   - Spatial Attention (region focus)
   - MobileViT Block (contextual refinement)

2. **Feature Fusion**
   - Concatenation of 3 modality features
   - 1x1 Convolution (dimensionality reduction)
   - MobileViT Block (cross-modal refinement)

3. **Classification Head**
   - Global Average Pooling
   - Dense(512) + Dropout(0.4)
   - Dense(256) + Dropout(0.3)
   - Softmax(7 classes)

## 🎨 Explainable AI (XAI)

The backend generates **Grad-CAM++** heatmaps that highlight which regions of the leaf image influenced the model's decision. The heatmap is returned as a Base64-encoded PNG image that can be directly displayed in a frontend.

**Layer Used**: `fused_reduce` (last convolutional layer after feature fusion)

## 📊 Preprocessing Pipeline

1. **Background Removal** (rembg)
   - Removes background and replaces with black
   
2. **Vein Enhancement**
   - Extract green channel
   - CLAHE (Contrast Limited Adaptive Histogram Equalization)
   - Frangi filter (ridge detection)
   - Morphological top-hat
   - Contrast stretching

3. **Texture Enhancement**
   - Unsharp masking
   - Local Binary Pattern (LBP)
   - Gabor filters (multiple orientations & frequencies)
   - Histogram equalization

## 📝 Knowledge Database

The `knowledge_db.json` file contains curated information for each medicinal plant:

- Scientific name
- Medicinal uses
- Active compounds
- Precautions
- Credible sources

## 🛠️ Development

### Run with auto-reload
```powershell
uv run uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

### Run tests (if implemented)
```powershell
uv run pytest
```

## 🚨 Important Notes

1. **Model File**: Ensure `best_model.keras` is present in the backend directory
2. **Knowledge DB**: Ensure `knowledge_db.json` is present
3. **Memory**: TensorFlow models can be memory-intensive. Ensure adequate RAM (8GB+ recommended)
4. **GPU Support**: For faster inference, ensure TensorFlow GPU support is configured

## 📄 License

This project is part of the TriModalXAI system for medicinal leaf classification.

## 🤝 Contributing

For questions or contributions, please refer to the main project repository.
