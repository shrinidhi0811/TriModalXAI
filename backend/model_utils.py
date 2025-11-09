"""
Model utilities for loading and running inference with memory optimization.
"""

import os
import cv2
import numpy as np

# TensorFlow memory optimization
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
os.environ['TF_FORCE_GPU_ALLOW_GROWTH'] = 'true'

import tensorflow as tf
from tensorflow.keras.applications.mobilenet_v3 import preprocess_input
from typing import List, Tuple

# Configure TensorFlow for low memory
tf.config.optimizer.set_jit(False)  # Disable XLA
tf.config.threading.set_intra_op_parallelism_threads(2)
tf.config.threading.set_inter_op_parallelism_threads(2)

# Import custom layers to register them before model loading
from custom_layers import ECA, SpatialAttention, MobileViTBlock


class TriModalClassifier:
    """
    Wrapper class for tri-modal leaf classification model with memory optimization.
    """
    
    def __init__(self, model_path: str):
        """
        Initialize the classifier with memory-efficient settings.
        
        Args:
            model_path: Path to the saved Keras model (.keras file)
        """
        print(f"Loading model from {model_path} with memory optimization...")
        
        # Define custom objects for model loading
        custom_objects = {
            'ECA': ECA,
            'SpatialAttention': SpatialAttention,
            'MobileViTBlock': MobileViTBlock
        }
        
        # Load model with custom objects and memory optimization
        self.model = tf.keras.models.load_model(
            model_path, 
            custom_objects=custom_objects,
            compile=False  # Don't compile - saves memory
        )
        
        print(f"Model loaded successfully (memory-optimized mode)")
        
        self.classes = [
            "alpinia_galanga",
            "azadirachta_indica",
            "basella_alba",
            "jasminum",
            "nerium_oleander",
            "plectranthus_amboinicus",
            "trigonella_foenum_graecum"
        ]
        self.img_size = (224, 224)
    
    def preprocess_for_model(
        self, rgb: np.ndarray, vein: np.ndarray, texture: np.ndarray
    ) -> List[np.ndarray]:
        """
        Preprocess the three modalities for model input.
        
        Args:
            rgb: RGB image (H, W, 3)
            vein: Vein-enhanced image (H, W, 3)
            texture: Texture-enhanced image (H, W, 3)
        
        Returns:
            List of preprocessed arrays [rgb, vein, texture], each (1, 224, 224, 3)
        """
        preprocessed = []
        
        for img in [rgb, vein, texture]:
            # Resize to model input size
            img_resized = cv2.resize(img, self.img_size)
            
            # Apply MobileNetV3 preprocessing
            img_preprocessed = preprocess_input(img_resized.astype(np.float32))
            
            # Add batch dimension
            img_batch = np.expand_dims(img_preprocessed, axis=0)
            
            preprocessed.append(img_batch)
        
        return preprocessed
    
    def predict(
        self, rgb: np.ndarray, vein: np.ndarray, texture: np.ndarray
    ) -> Tuple[np.ndarray, List[np.ndarray]]:
        """
        Run inference on the three modalities.
        
        Args:
            rgb: RGB image (H, W, 3)
            vein: Vein-enhanced image (H, W, 3)
            texture: Texture-enhanced image (H, W, 3)
        
        Returns:
            Tuple of (predictions, preprocessed_inputs)
            - predictions: Softmax probabilities array (1, num_classes)
            - preprocessed_inputs: List of preprocessed inputs for Grad-CAM
        """
        # Preprocess inputs
        preprocessed_inputs = self.preprocess_for_model(rgb, vein, texture)
        
        # Run inference
        predictions = self.model.predict(preprocessed_inputs, verbose=0)
        
        # Handle potential tuple output
        if not isinstance(predictions, np.ndarray):
            predictions = predictions[0]
        
        return predictions, preprocessed_inputs
    
    def get_top_predictions(
        self, predictions: np.ndarray, top_k: int = 3
    ) -> List[dict]:
        """
        Get top-k predictions with class names and confidence scores.
        
        Args:
            predictions: Softmax probabilities array (1, num_classes)
            top_k: Number of top predictions to return
        
        Returns:
            List of dicts with 'class' and 'confidence' keys
        """
        probs = predictions[0]
        top_indices = np.argsort(probs)[::-1][:top_k]
        
        top_predictions = []
        for idx in top_indices:
            top_predictions.append({
                "class": self.classes[idx],
                "confidence": float(probs[idx])
            })
        
        return top_predictions
