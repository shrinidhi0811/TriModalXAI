"""
Explainable AI utilities for Grad-CAM and Grad-CAM++ visualization.
"""

import cv2
import numpy as np
import tensorflow as tf
from typing import List, Optional


def get_gradcam_heatmap(
    model: tf.keras.Model,
    img_inputs: List[np.ndarray],
    layer_name: str,
    class_index: Optional[int] = None,
    use_gradcam_plus_plus: bool = False
) -> np.ndarray:
    """
    Generates Grad-CAM or Grad-CAM++ heatmap for a multimodal model.
    
    Args:
        model: Trained Keras model
        img_inputs: List of input arrays [rgb, vein, tex], each shaped (1, H, W, 3)
        layer_name: Name of the last convolutional layer (string)
        class_index: Target class index (int), if None uses predicted class
        use_gradcam_plus_plus: True for Grad-CAM++, False for standard Grad-CAM
    
    Returns:
        Heatmap array (H, W) normalized to [0, 1]
    """
    grad_model = tf.keras.models.Model(
        inputs=model.inputs,
        outputs=[model.get_layer(layer_name).output, model.output]
    )
    
    with tf.GradientTape() as tape:
        conv_outputs, predictions = grad_model(img_inputs)
        predictions = (
            predictions if isinstance(predictions, tf.Tensor) else predictions[0]
        )
        if class_index is None:
            class_index = tf.argmax(predictions[0])
        output = predictions[:, class_index]
    
    grads = tape.gradient(output, conv_outputs)
    
    if use_gradcam_plus_plus:
        # --- Grad-CAM++ variant ---
        grads_power_2 = tf.pow(grads, 2)
        grads_power_3 = tf.pow(grads, 3)
        sum_grads = tf.reduce_sum(conv_outputs * grads_power_3, axis=(1, 2))
        
        # Ensure shape compatibility for broadcasting
        sum_grads = tf.reshape(
            sum_grads, [tf.shape(sum_grads)[0], 1, 1, tf.shape(sum_grads)[-1]]
        )
        
        eps = 1e-8
        alpha_num = grads_power_2
        alpha_denom = 2 * grads_power_2 + sum_grads
        alpha_denom = tf.where(
            alpha_denom != 0.0, alpha_denom, eps
        )
        alphas = alpha_num / alpha_denom
        weights = tf.reduce_sum(alphas * tf.nn.relu(grads), axis=(1, 2))
    else:
        # --- Standard Grad-CAM ---
        weights = tf.reduce_mean(grads, axis=(1, 2))
    
    cam = tf.reduce_sum(
        tf.multiply(weights[:, tf.newaxis, tf.newaxis, :], conv_outputs), axis=-1
    )
    heatmap = tf.nn.relu(cam)
    heatmap = heatmap / tf.reduce_max(heatmap)
    heatmap = heatmap[0].numpy()
    
    return heatmap


def generate_gradcam_overlay(
    model: tf.keras.Model,
    rgb_image: np.ndarray,
    img_inputs: List[np.ndarray],
    layer_name: str = "fused_reduce",
    class_index: Optional[int] = None,
    use_gradcam_plus_plus: bool = True
) -> np.ndarray:
    """
    Generate Grad-CAM++ heatmap overlay on RGB image.
    
    Args:
        model: Trained Keras model
        rgb_image: Original RGB image (H, W, 3) - not preprocessed
        img_inputs: Preprocessed model inputs [rgb, vein, tex], each (1, 224, 224, 3)
        layer_name: Name of the last convolutional layer
        class_index: Target class index, if None uses predicted class
        use_gradcam_plus_plus: True for Grad-CAM++
    
    Returns:
        Heatmap overlay image as RGB array (H, W, 3)
    """
    # Generate Grad-CAM heatmap
    heatmap = get_gradcam_heatmap(
        model, img_inputs, layer_name, class_index, use_gradcam_plus_plus
    )
    
    # Resize heatmap to match original image size
    heatmap_resized = cv2.resize(heatmap, (rgb_image.shape[1], rgb_image.shape[0]))
    heatmap_uint8 = np.uint8(255 * heatmap_resized)
    
    # Apply colormap
    heatmap_colored = cv2.applyColorMap(heatmap_uint8, cv2.COLORMAP_JET)
    
    # Convert RGB to BGR for cv2.addWeighted
    rgb_bgr = cv2.cvtColor(rgb_image, cv2.COLOR_RGB2BGR)
    
    # Overlay heatmap on image
    superimposed_img = cv2.addWeighted(rgb_bgr, 0.6, heatmap_colored, 0.4, 0)
    
    # Convert back to RGB
    superimposed_rgb = cv2.cvtColor(superimposed_img, cv2.COLOR_BGR2RGB)
    
    return superimposed_rgb
