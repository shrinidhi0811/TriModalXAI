"""
Example usage of the TriModal XAI Backend API.
This script demonstrates how to interact with the API programmatically.
"""

import base64
import json
from pathlib import Path

import requests
from PIL import Image
from io import BytesIO


class TriModalAPIClient:
    """Simple client for interacting with the TriModal XAI API."""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        """
        Initialize the API client.
        
        Args:
            base_url: Base URL of the API server
        """
        self.base_url = base_url.rstrip("/")
    
    def health_check(self) -> dict:
        """Check if the API is running."""
        response = requests.get(f"{self.base_url}/health")
        response.raise_for_status()
        return response.json()
    
    def get_classes(self) -> dict:
        """Get list of supported plant classes."""
        response = requests.get(f"{self.base_url}/classes")
        response.raise_for_status()
        return response.json()
    
    def predict(self, image_path: str) -> dict:
        """
        Predict the class of a leaf image.
        
        Args:
            image_path: Path to the image file
        
        Returns:
            Prediction results including class, confidence, knowledge, and Grad-CAM
        """
        with open(image_path, "rb") as f:
            files = {"file": f}
            response = requests.post(f"{self.base_url}/predict", files=files)
        
        response.raise_for_status()
        return response.json()
    
    def save_gradcam(self, base64_image: str, output_path: str):
        """
        Save the Grad-CAM heatmap to a file.
        
        Args:
            base64_image: Base64-encoded image string
            output_path: Path to save the image
        """
        image_bytes = base64.b64decode(base64_image)
        image = Image.open(BytesIO(image_bytes))
        image.save(output_path)
        print(f"Grad-CAM heatmap saved to: {output_path}")


def example_usage():
    """Example of using the API client."""
    
    # Initialize client
    client = TriModalAPIClient()
    
    print("=" * 70)
    print("TriModal XAI API - Example Usage")
    print("=" * 70)
    
    # 1. Health check
    print("\n1️⃣ Checking API health...")
    try:
        health = client.health_check()
        print(f"✅ API Status: {health['status']}")
        print(f"   Model loaded: {health['model_loaded']}")
        print(f"   Knowledge DB loaded: {health['knowledge_db_loaded']}")
    except Exception as e:
        print(f"❌ Error: {e}")
        print("Make sure the server is running!")
        return
    
    # 2. Get classes
    print("\n2️⃣ Getting supported classes...")
    try:
        classes_info = client.get_classes()
        print(f"✅ Supported classes ({classes_info['num_classes']}):")
        for i, cls in enumerate(classes_info['classes'], 1):
            print(f"   {i}. {cls}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # 3. Make prediction
    print("\n3️⃣ Making prediction...")
    image_path = input("Enter path to leaf image (or press Enter to skip): ").strip()
    
    if not image_path:
        print("⏭️ Skipping prediction example")
        return
    
    if not Path(image_path).exists():
        print(f"❌ File not found: {image_path}")
        return
    
    try:
        print(f"📤 Uploading image: {image_path}")
        result = client.predict(image_path)
        
        print("\n📊 Prediction Results:")
        print(f"   Predicted Class: {result['predicted_class']}")
        print(f"   Confidence: {result['confidence']:.4f} ({result['confidence']*100:.2f}%)")
        
        print("\n   Top-3 Predictions:")
        for i, pred in enumerate(result['top3'], 1):
            print(f"      {i}. {pred['class']:30s} - {pred['confidence']:.4f}")
        
        print("\n📚 Medicinal Knowledge:")
        knowledge = result['knowledge']
        print(f"   Scientific Name: {knowledge['Scientific Name']}")
        print(f"   Medicinal Uses: {len(knowledge['Medicinal Uses'])} listed")
        print(f"   Active Compounds: {len(knowledge['Active Compounds'])} listed")
        print(f"   Precautions: {knowledge['Precautions'][:100]}...")
        
        # Save Grad-CAM heatmap
        if result.get('gradcam_image_base64'):
            output_dir = Path("output")
            output_dir.mkdir(exist_ok=True)
            
            gradcam_path = output_dir / f"gradcam_{result['predicted_class']}.png"
            client.save_gradcam(result['gradcam_image_base64'], str(gradcam_path))
            print(f"\n🎨 Grad-CAM++ heatmap saved to: {gradcam_path}")
        
        # Optionally save full result as JSON
        save_json = input("\nSave full result as JSON? (y/n): ").strip().lower()
        if save_json == 'y':
            output_json = output_dir / f"result_{result['predicted_class']}.json"
            with open(output_json, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            print(f"💾 Full result saved to: {output_json}")
        
        print("\n✅ Prediction completed successfully!")
        
    except Exception as e:
        print(f"❌ Error during prediction: {e}")


def batch_prediction_example():
    """Example of batch processing multiple images."""
    
    print("\n" + "=" * 70)
    print("Batch Prediction Example")
    print("=" * 70)
    
    client = TriModalAPIClient()
    
    # Get directory with images
    image_dir = input("Enter directory containing leaf images: ").strip()
    
    if not image_dir or not Path(image_dir).exists():
        print("Invalid directory!")
        return
    
    # Find all image files
    image_files = []
    for ext in ['.jpg', '.jpeg', '.png', '.webp']:
        image_files.extend(Path(image_dir).glob(f"*{ext}"))
        image_files.extend(Path(image_dir).glob(f"*{ext.upper()}"))
    
    if not image_files:
        print("No image files found!")
        return
    
    print(f"\nFound {len(image_files)} images")
    
    results = []
    for i, img_path in enumerate(image_files, 1):
        print(f"\n[{i}/{len(image_files)}] Processing: {img_path.name}")
        try:
            result = client.predict(str(img_path))
            results.append({
                "filename": img_path.name,
                "predicted_class": result['predicted_class'],
                "confidence": result['confidence']
            })
            print(f"   ✅ {result['predicted_class']} ({result['confidence']:.4f})")
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    # Summary
    print("\n" + "=" * 70)
    print("Batch Prediction Summary")
    print("=" * 70)
    for r in results:
        print(f"{r['filename']:30s} → {r['predicted_class']:30s} ({r['confidence']:.4f})")


if __name__ == "__main__":
    import sys
    
    print("\nTriModal XAI API - Example Scripts")
    print("1. Single prediction example")
    print("2. Batch prediction example")
    print("3. Exit")
    
    choice = input("\nSelect option (1-3): ").strip()
    
    if choice == "1":
        example_usage()
    elif choice == "2":
        batch_prediction_example()
    else:
        print("Goodbye!")
