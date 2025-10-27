from fastapi import FastAPI, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import numpy as np
from typing import Dict, Any
import os

from model_utils import load_model, preprocess_image, generate_gradcam, create_gradcam_overlay
from knowledge_utils import KnowledgeBase

# Initialize FastAPI app
app = FastAPI(
    title="Leaf Classification API",
    description="API for leaf classification with Grad-CAM visualization",
    version="1.0.0"
)

# Enable CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variables for model and knowledge base
model = None
knowledge_base = None

# Leaf classes
LEAF_CLASSES = [
    "alpinia_galanga", "azadirachta_indica", "basella_alba",
    "jasminum", "nerium_oleander", "plectranthus_amboinicus",
    "trigonella_foenum_graecum"
]

@app.on_event("startup")
async def startup_event():
    """Load model and knowledge base on startup."""
    global model, knowledge_base
    try:
        # Get the absolute path to the backend directory
        backend_dir = os.path.dirname(os.path.abspath(__file__))
        model_path = os.path.join(backend_dir, "best_model.keras")
        knowledge_path = os.path.join(backend_dir, "knowledge_db.json")
        
        model = load_model(model_path)
        knowledge_base = KnowledgeBase(knowledge_path)
    except Exception as e:
        print(f"Error during startup: {str(e)}")
        raise

@app.post("/predict")
async def predict(file: UploadFile) -> Dict[str, Any]:
    """Predict leaf class and return info with Grad-CAM visualization."""
    # Validate file
    if not file.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    try:
        # Read and preprocess image (returns [rgb, vein, texture] and original)
        contents = await file.read()
        preprocessed_imgs, original_img = preprocess_image(contents)
        
        # Get model prediction - model expects list of 3 inputs
        # Expand dimensions for batch
        rgb_batch = np.expand_dims(preprocessed_imgs[0], axis=0)
        vein_batch = np.expand_dims(preprocessed_imgs[1], axis=0)
        texture_batch = np.expand_dims(preprocessed_imgs[2], axis=0)
        
        prediction = model.predict([rgb_batch, vein_batch, texture_batch], verbose=0)
        predicted_idx = np.argmax(prediction[0])
        confidence = float(prediction[0][predicted_idx])
        predicted_class = LEAF_CLASSES[predicted_idx]
        
        # Get knowledge base info
        knowledge = knowledge_base.get_leaf_info(predicted_class)
        
        # Generate Grad-CAM
        heatmap = generate_gradcam(model, preprocessed_imgs)
        heatmap_base64 = create_gradcam_overlay(original_img, heatmap)
        
        # Return response
        return {
            "predicted_class": predicted_class,
            "confidence": confidence,
            "knowledge": knowledge,
            "heatmap_image_base64": heatmap_base64
        }
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)