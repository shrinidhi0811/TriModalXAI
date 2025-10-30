"""
Simple test script to verify the backend setup and API functionality.
"""

import requests
import json
from pathlib import Path


def test_health_check():
    """Test the health check endpoint."""
    print("\n🏥 Testing health check endpoint...")
    try:
        response = requests.get("http://localhost:8000/health")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health check passed: {json.dumps(data, indent=2)}")
            return True
        else:
            print(f"❌ Health check failed with status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        print("Make sure the server is running: uv run uvicorn app:app --reload")
        return False


def test_get_classes():
    """Test the get classes endpoint."""
    print("\n📚 Testing get classes endpoint...")
    try:
        response = requests.get("http://localhost:8000/classes")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Classes endpoint passed:")
            print(f"   Number of classes: {data['num_classes']}")
            print(f"   Classes: {', '.join(data['classes'])}")
            return True
        else:
            print(f"❌ Classes endpoint failed with status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_predict(image_path: str):
    """Test the prediction endpoint with an image."""
    print(f"\n🔍 Testing prediction endpoint with image: {image_path}")
    
    # Check if file exists
    if not Path(image_path).exists():
        print(f"❌ Image file not found: {image_path}")
        print("Please provide a valid image path to test predictions")
        return False
    
    try:
        with open(image_path, "rb") as f:
            files = {"file": f}
            response = requests.post("http://localhost:8000/predict", files=files)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Prediction successful!")
            print(f"\n   Predicted Class: {data['predicted_class']}")
            print(f"   Confidence: {data['confidence']:.4f}")
            print(f"\n   Top-3 Predictions:")
            for i, pred in enumerate(data['top3'], 1):
                print(f"      {i}. {pred['class']} - {pred['confidence']:.4f}")
            
            print(f"\n   Knowledge Retrieved:")
            print(f"      Scientific Name: {data['knowledge']['Scientific Name']}")
            print(f"      Medicinal Uses: {len(data['knowledge']['Medicinal Uses'])} listed")
            print(f"      Active Compounds: {len(data['knowledge']['Active Compounds'])} listed")
            
            # Check if Grad-CAM image is present
            if data.get('gradcam_image_base64'):
                print(f"\n   ✅ Grad-CAM++ heatmap generated (Base64 encoded)")
            else:
                print(f"\n   ⚠️  No Grad-CAM++ heatmap in response")
            
            return True
        else:
            print(f"❌ Prediction failed with status {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def main():
    """Run all tests."""
    print("=" * 70)
    print("🧪 TriModal XAI Backend Test Suite")
    print("=" * 70)
    
    # Test 1: Health check
    health_ok = test_health_check()
    
    if not health_ok:
        print("\n❌ Server is not running or not responding")
        print("Please start the server with: uv run uvicorn app:app --reload")
        return
    
    # Test 2: Get classes
    classes_ok = test_get_classes()
    
    # Test 3: Prediction (optional - requires image)
    print("\n" + "=" * 70)
    print("📸 Prediction Test (Optional)")
    print("=" * 70)
    image_path = input("\nEnter path to a test image (or press Enter to skip): ").strip()
    
    if image_path:
        test_predict(image_path)
    else:
        print("⏭️  Skipping prediction test")
    
    # Summary
    print("\n" + "=" * 70)
    print("📊 Test Summary")
    print("=" * 70)
    print(f"   Health Check: {'✅ PASSED' if health_ok else '❌ FAILED'}")
    print(f"   Get Classes:  {'✅ PASSED' if classes_ok else '❌ FAILED'}")
    print("=" * 70)


if __name__ == "__main__":
    main()
