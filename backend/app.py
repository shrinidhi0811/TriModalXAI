"""
FastAPI backend for tri-modal medicinal leaf classification with XAI.
"""

import base64
import io
from pathlib import Path
from typing import Dict

import cv2
import numpy as np
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image

from knowledge_utils import KnowledgeDB
from model_utils import TriModalClassifier
from preprocessing import preprocess_all_modalities
from xai import generate_gradcam_overlay

# Initialize FastAPI app
app = FastAPI(
    title="TriModal Medicinal Leaf Classifier",
    description="AI-powered medicinal leaf identification with explainable AI",
    version="1.0.0"
)

# Add CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update with specific origins in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize global components
BASE_DIR = Path(__file__).parent
MODEL_PATH = BASE_DIR / "best_model.keras"
KNOWLEDGE_DB_PATH = BASE_DIR / "knowledge_db.json"

# Load model and knowledge DB at startup
classifier = None
knowledge_db = None


@app.on_event("startup")
async def startup_event():
    """Initialize model and knowledge database on startup."""
    global classifier, knowledge_db
    
    try:
        print("=" * 50)
        print("🚀 Starting TriModal XAI Backend...")
        print("=" * 50)
        
        print(f"📂 Base directory: {BASE_DIR}")
        print(f"🤖 Model path: {MODEL_PATH}")
        print(f"📚 Knowledge DB path: {KNOWLEDGE_DB_PATH}")
        
        # Check if files exist
        if not MODEL_PATH.exists():
            raise FileNotFoundError(f"Model file not found: {MODEL_PATH}")
        if not KNOWLEDGE_DB_PATH.exists():
            raise FileNotFoundError(f"Knowledge DB not found: {KNOWLEDGE_DB_PATH}")
        
        print(f"✅ Model file exists ({MODEL_PATH.stat().st_size / (1024*1024):.2f} MB)")
        print(f"✅ Knowledge DB exists ({KNOWLEDGE_DB_PATH.stat().st_size / 1024:.2f} KB)")
        
        print("\n🔄 Loading model (this may take 30-60 seconds)...")
        classifier = TriModalClassifier(str(MODEL_PATH))
        print("✅ Model loaded successfully!")
        
        print("\n🔄 Loading knowledge database...")
        knowledge_db = KnowledgeDB(str(KNOWLEDGE_DB_PATH))
        print("✅ Knowledge database loaded!")
        
        print("\n" + "=" * 50)
        print("🎉 Backend ready to accept requests!")
        print("=" * 50)
        
    except Exception as e:
        print("\n" + "=" * 50)
        print(f"❌ STARTUP FAILED: {type(e).__name__}")
        print(f"Error: {str(e)}")
        print("=" * 50)
        import traceback
        traceback.print_exc()
        raise


@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "status": "running",
        "message": "TriModal Medicinal Leaf Classifier API",
        "endpoints": {
            "predict": "/predict",
            "health": "/health"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint with detailed status."""
    model_status = "loaded" if classifier is not None else "not_loaded"
    kb_status = "loaded" if knowledge_db is not None else "not_loaded"
    
    is_healthy = classifier is not None and knowledge_db is not None
    
    return {
        "status": "healthy" if is_healthy else "unhealthy",
        "model_loaded": classifier is not None,
        "knowledge_db_loaded": knowledge_db is not None,
        "details": {
            "model": model_status,
            "knowledge_db": kb_status
        }
    }


@app.post("/predict")
async def predict(file: UploadFile = File(...)) -> Dict:
    """
    Predict medicinal leaf class from uploaded image.
    
    Args:
        file: Uploaded image file (JPG/PNG)
    
    Returns:
        JSON response with predictions, knowledge, and Grad-CAM visualization
    """
    # Validate file type
    if not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=400,
            detail="File must be an image (JPG/PNG)"
        )
    
    try:
        # Read uploaded file
        image_bytes = await file.read()
        
        # Step 1: Preprocess all modalities
        print("Preprocessing image modalities...")
        rgb_clean, vein_enhanced, texture_enhanced = preprocess_all_modalities(
            image_bytes
        )
        
        # Step 2: Run inference
        print("Running model inference...")
        predictions, preprocessed_inputs = classifier.predict(
            rgb_clean, vein_enhanced, texture_enhanced
        )
        
        # Step 3: Get top-3 predictions
        top3_predictions = classifier.get_top_predictions(predictions, top_k=3)
        
        # Step 4: Get predicted class and confidence
        predicted_class = top3_predictions[0]["class"]
        confidence = top3_predictions[0]["confidence"]
        
        print(f"Predicted: {predicted_class} (confidence: {confidence:.4f})")
        
        # Step 5: Retrieve knowledge for predicted class
        print("Retrieving medicinal knowledge...")
        knowledge_info = knowledge_db.get_formatted_info(predicted_class)
        
        # Step 6: Generate Grad-CAM++ visualization
        print("Generating Grad-CAM++ heatmap...")
        predicted_index = np.argmax(predictions[0])
        
        gradcam_overlay = generate_gradcam_overlay(
            model=classifier.model,
            rgb_image=rgb_clean,
            img_inputs=preprocessed_inputs,
            layer_name="fused_reduce",  # From your model architecture
            class_index=predicted_index,
            use_gradcam_plus_plus=True
        )
        
        # Step 7: Convert Grad-CAM image to base64
        gradcam_pil = Image.fromarray(gradcam_overlay)
        buffered = io.BytesIO()
        gradcam_pil.save(buffered, format="PNG")
        gradcam_base64 = base64.b64encode(buffered.getvalue()).decode("utf-8")
        
        # Step 8: Build response
        response = {
            "predicted_class": predicted_class,
            "confidence": confidence,
            "top3": top3_predictions,
            "knowledge": knowledge_info,
            "gradcam_image_base64": gradcam_base64
        }
        
        print("Prediction completed successfully!")
        return response
    
    except Exception as e:
        print(f"Error during prediction: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error processing image: {str(e)}"
        )


@app.get("/classes")
async def get_classes():
    """Get list of supported leaf classes."""
    return {
        "classes": classifier.classes,
        "num_classes": len(classifier.classes)
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
