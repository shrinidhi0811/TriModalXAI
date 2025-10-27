import tensorflow as tf
import numpy as np
import cv2
import base64
from io import BytesIO
from PIL import Image
from keras.applications import mobilenet_v3
from keras.preprocessing.image import img_to_array

# Target size for model input
TARGET_SIZE = (224, 224)

def load_model(model_path: str) -> tf.keras.Model:
    """Load the trained Keras model."""
    return tf.keras.models.load_model(model_path)

def preprocess_image(image_bytes: bytes) -> tuple[np.ndarray, np.ndarray]:
    """Preprocess the uploaded image for model prediction."""
    # Convert bytes to PIL Image
    image = Image.open(BytesIO(image_bytes))
    image = image.convert('RGB')
    
    # Convert to array and resize
    image_array = img_to_array(image)
    original_img = cv2.resize(image_array, TARGET_SIZE)
    
    # Preprocess like MobileNetV3
    preprocessed_img = mobilenet_v3.preprocess_input(original_img.copy())
    
    return preprocessed_img, original_img

def generate_gradcam(model: tf.keras.Model, preprocessed_img: np.ndarray,
                    layer_name: str = 'Conv_2') -> np.ndarray:
    """Generate Grad-CAM heatmap for the given image."""
    # Create GradCAM model
    grad_model = tf.keras.Model(
        [model.inputs],
        [model.get_layer(layer_name).output, model.output]
    )
    
    # Get gradients
    with tf.GradientTape() as tape:
        conv_outputs, predictions = grad_model(preprocessed_img[np.newaxis])
        loss = predictions[:, tf.argmax(predictions[0])]
        
    # Extract gradients
    grads = tape.gradient(loss, conv_outputs)
    
    # Global average pooling
    pooled_grads = tf.reduce_mean(grads, axis=(0, 1, 2))
    
    # Weight the channels by gradients
    conv_outputs = conv_outputs[0]
    heatmap = tf.reduce_sum(tf.multiply(pooled_grads, conv_outputs), axis=-1)
    
    # Normalize heatmap
    heatmap = np.maximum(heatmap, 0) / (np.max(heatmap) or 1)
    return heatmap

def create_gradcam_overlay(original_img: np.ndarray, heatmap: np.ndarray) -> str:
    """Create Grad-CAM overlay and convert to base64 string."""
    # Resize heatmap to match original image
    heatmap = cv2.resize(heatmap, TARGET_SIZE)
    
    # Convert heatmap to RGB
    heatmap = np.uint8(255 * heatmap)
    heatmap = cv2.applyColorMap(heatmap, cv2.COLORMAP_JET)
    
    # Superimpose heatmap on original image
    overlay = cv2.addWeighted(original_img, 0.6, heatmap, 0.4, 0)
    
    # Convert to base64
    _, buffer = cv2.imencode('.png', overlay)
    overlay_base64 = base64.b64encode(buffer).decode('utf-8')
    
    return overlay_base64