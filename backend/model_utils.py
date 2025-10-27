import tensorflow as tf
import numpy as np
import cv2
import base64
from io import BytesIO
from PIL import Image
from tensorflow.keras.preprocessing.image import img_to_array
from tensorflow.keras import layers
from tensorflow.keras.layers import Conv2D, Dense, LayerNormalization
import keras

# Target size for model input
TARGET_SIZE = (224, 224)

# Define custom layers from the training notebook

# 1. ECA (Efficient Channel Attention)
@keras.saving.register_keras_serializable()
class ECA(tf.keras.layers.Layer):
    def __init__(self, k_size=3, **kwargs):
        super(ECA, self).__init__(**kwargs)
        self.k_size = k_size

    def build(self, input_shape):
        # conv over channel dimension after reshaping to (B, C, 1, 1)
        self.conv = Conv2D(1, kernel_size=(self.k_size, 1), padding="same", use_bias=False)

    def call(self, x):
        y = tf.reduce_mean(x, axis=[1, 2], keepdims=True)  # (B,1,1,C)
        y = tf.transpose(y, [0, 3, 1, 2])                  # (B,C,1,1)
        y = self.conv(y)
        y = tf.transpose(y, [0, 2, 3, 1])                  # (B,1,1,C)
        y = tf.sigmoid(y)
        return x * y
    
    def get_config(self):
        config = super(ECA, self).get_config()
        config.update({"k_size": self.k_size})
        return config

# 2. Spatial Attention
@keras.saving.register_keras_serializable()
class SpatialAttention(tf.keras.layers.Layer):
    def build(self, input_shape):
        self.conv = Conv2D(1, kernel_size=7, padding="same", activation="sigmoid")

    def call(self, x):
        avg_pool = tf.reduce_mean(x, axis=-1, keepdims=True)
        max_pool = tf.reduce_max(x, axis=-1, keepdims=True)
        concat = tf.concat([avg_pool, max_pool], axis=-1)
        attn = self.conv(concat)
        return x * attn

# 3. MobileViTBlock
@keras.saving.register_keras_serializable()
class MobileViTBlock(tf.keras.layers.Layer):
    def __init__(self, num_heads=2, projection_dim=64, patch_h=1, patch_w=1, **kwargs):
        super(MobileViTBlock, self).__init__(**kwargs)
        self.num_heads = num_heads
        self.projection_dim = projection_dim
        self.patch_h = patch_h
        self.patch_w = patch_w

    def build(self, input_shape):
        # input_shape: (B, H, W, C_in)
        _, H, W, C_in = input_shape
        # 1x1 conv to reduce channels to projection_dim
        self.proj_conv = Conv2D(self.projection_dim, kernel_size=1, padding="same", activation="relu")
        self.norm = LayerNormalization(epsilon=1e-6)
        self.mha = tf.keras.layers.MultiHeadAttention(num_heads=self.num_heads, key_dim=self.projection_dim)
        self.ffn = tf.keras.Sequential([
            Dense(self.projection_dim * 2, activation="relu"),
            Dense(self.projection_dim)
        ])
        # token mapping layers
        self.to_tokens = Dense(self.projection_dim)
        self.to_patches = Dense(self.projection_dim)
        # final projection back to projection_dim channels
        self.proj_back = Conv2D(self.projection_dim, kernel_size=1, padding="same")

        super(MobileViTBlock, self).build(input_shape)

    def call(self, x):
        # Project channels
        y = self.proj_conv(x)  # (B,H,W,proj_dim)
        shape = tf.shape(y)
        b = shape[0]; h = shape[1]; w = shape[2]; c = shape[3]

        # Flatten spatial dimension for token processing (B, H*W, C)
        y_flat = tf.reshape(y, [b, h * w, c])

        # Map to token dim used by MHA
        y_tokens = self.to_tokens(y_flat)           # (B, N, proj_dim)
        y_norm = self.norm(y_tokens)
        attn = self.mha(y_norm, y_norm)             # (B, N, proj_dim)
        y_tokens = y_tokens + attn
        y_tokens = y_tokens + self.ffn(y_tokens)

        # Map tokens back to spatial embeddings and reshape to H,W
        y_out = self.to_patches(y_tokens)           # (B, N, proj_dim)
        y_out = tf.reshape(y_out, [b, h, w, c])     # (B, H, W, proj_dim)
        y_out = self.proj_back(y_out)               # (B, H, W, proj_dim)

        return y_out
    
    def get_config(self):
        config = super(MobileViTBlock, self).get_config()
        config.update({
            "num_heads": self.num_heads,
            "projection_dim": self.projection_dim,
            "patch_h": self.patch_h,
            "patch_w": self.patch_w
        })
        return config

def load_model(model_path: str) -> tf.keras.Model:
    """Load the trained Keras model with custom layers."""
    return tf.keras.models.load_model(model_path, custom_objects={
        'ECA': ECA,
        'SpatialAttention': SpatialAttention,
        'MobileViTBlock': MobileViTBlock
    })

def preprocess_image(image_bytes: bytes):
    """Preprocess the uploaded image for model prediction.
    
    The model expects 3 inputs: RGB, vein, and texture.
    Since we only have RGB input, we'll create synthetic vein and texture representations.
    """
    try:
        # Convert bytes to PIL Image
        image = Image.open(BytesIO(image_bytes))
        image = image.convert('RGB')
        
        # Convert to array and resize
        image_array = img_to_array(image)
        print(f"DEBUG: image_array shape: {image_array.shape}, dtype: {image_array.dtype}")
        original_img = cv2.resize(image_array, TARGET_SIZE).astype(np.uint8)
        print(f"DEBUG: original_img shape after resize: {original_img.shape}, dtype: {original_img.dtype}")
    except Exception as e:
        print(f"ERROR in image loading/resizing: {e}")
        import traceback
        traceback.print_exc()
        raise
    
    # Create RGB input
    rgb_img = original_img.copy().astype('float32')
    
    # Create vein representation (using edge detection on grayscale)
    gray = cv2.cvtColor(original_img, cv2.COLOR_RGB2GRAY)
    # Enhance edges for vein-like structure
    vein_img = cv2.Canny(gray, 50, 150)
    # Convert to 3-channel
    vein_img = cv2.cvtColor(vein_img, cv2.COLOR_GRAY2RGB).astype('float32')
    
    # Create texture representation (using Laplacian for texture details)
    laplacian = cv2.Laplacian(gray, cv2.CV_64F)
    laplacian = np.uint8(np.absolute(laplacian))
    # Enhance contrast
    texture_img = cv2.equalizeHist(laplacian)
    # Convert to 3-channel
    texture_img = cv2.cvtColor(texture_img, cv2.COLOR_GRAY2RGB).astype('float32')
    
    # Preprocess all three modalities like MobileNetV3
    # MobileNetV3 preprocessing: scale to [-1, 1]
    rgb_preprocessed = (rgb_img / 127.5) - 1.0
    vein_preprocessed = (vein_img / 127.5) - 1.0
    texture_preprocessed = (texture_img / 127.5) - 1.0
    
    # Return list of all three inputs and original RGB for visualization
    return [rgb_preprocessed, vein_preprocessed, texture_preprocessed], original_img

def generate_gradcam(model: tf.keras.Model, preprocessed_imgs: list,
                    layer_name: str = 'fused_reduce') -> np.ndarray:
    """Generate Grad-CAM heatmap for the given image.
    
    Args:
        model: The trained model
        preprocessed_imgs: List of [rgb, vein, texture] preprocessed images
        layer_name: Name of the layer to visualize (default: 'fused_reduce' for the fusion layer)
    """
    # Create GradCAM model
    grad_model = tf.keras.Model(
        model.inputs,
        [model.get_layer(layer_name).output, model.output]
    )
    
    # Expand dimensions for batch - preprocessed_imgs is a list of 3 arrays
    rgb_batch = np.expand_dims(preprocessed_imgs[0], axis=0)
    vein_batch = np.expand_dims(preprocessed_imgs[1], axis=0)
    texture_batch = np.expand_dims(preprocessed_imgs[2], axis=0)
    
    # Get gradients
    with tf.GradientTape() as tape:
        conv_outputs, predictions = grad_model([rgb_batch, vein_batch, texture_batch])
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