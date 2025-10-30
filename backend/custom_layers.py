"""
Custom Keras layers used in the tri-modal leaf classification model.
These layers must be registered before loading the model.
"""

import tensorflow as tf
from tensorflow.keras.layers import (
    Conv2D, Dense, LayerNormalization, Layer, MultiHeadAttention
)
from tensorflow.keras.utils import register_keras_serializable


@register_keras_serializable(package="Custom", name="ECA")
class ECA(Layer):
    """
    Efficient Channel Attention layer.
    Applies channel-wise attention using adaptive kernel size.
    """
    
    def __init__(self, k_size=3, **kwargs):
        super(ECA, self).__init__(**kwargs)
        self.k_size = k_size

    def build(self, input_shape):
        # Conv over channel dimension after reshaping to (B, C, 1, 1)
        self.conv = Conv2D(
            1, kernel_size=(self.k_size, 1), padding="same", use_bias=False
        )
        super(ECA, self).build(input_shape)

    def call(self, x):
        y = tf.reduce_mean(x, axis=[1, 2], keepdims=True)  # (B,1,1,C)
        y = tf.transpose(y, [0, 3, 1, 2])  # (B,C,1,1)
        y = self.conv(y)
        y = tf.transpose(y, [0, 2, 3, 1])  # (B,1,1,C)
        y = tf.sigmoid(y)
        return x * y

    def get_config(self):
        config = super(ECA, self).get_config()
        config.update({"k_size": self.k_size})
        return config


@register_keras_serializable(package="Custom", name="SpatialAttention")
class SpatialAttention(Layer):
    """
    Spatial Attention layer.
    Applies spatial-wise attention based on average and max pooling.
    """
    
    def __init__(self, **kwargs):
        super(SpatialAttention, self).__init__(**kwargs)

    def build(self, input_shape):
        self.conv = Conv2D(
            1, kernel_size=7, padding="same", activation="sigmoid"
        )
        super(SpatialAttention, self).build(input_shape)

    def call(self, x):
        avg_pool = tf.reduce_mean(x, axis=-1, keepdims=True)
        max_pool = tf.reduce_max(x, axis=-1, keepdims=True)
        concat = tf.concat([avg_pool, max_pool], axis=-1)
        attn = self.conv(concat)
        return x * attn

    def get_config(self):
        return super(SpatialAttention, self).get_config()


@register_keras_serializable(package="Custom", name="MobileViTBlock")
class MobileViTBlock(Layer):
    """
    MobileViT Block for contextual feature refinement.
    Combines convolutional features with transformer-based processing.
    """
    
    def __init__(
        self, num_heads=2, projection_dim=64, patch_h=1, patch_w=1, **kwargs
    ):
        super(MobileViTBlock, self).__init__(**kwargs)
        self.num_heads = num_heads
        self.projection_dim = projection_dim
        self.patch_h = patch_h
        self.patch_w = patch_w

    def build(self, input_shape):
        # input_shape: (B, H, W, C_in)
        _, H, W, C_in = input_shape
        
        # 1x1 conv to reduce channels to projection_dim
        self.proj_conv = Conv2D(
            self.projection_dim, kernel_size=1, padding="same", activation="relu"
        )
        self.norm = LayerNormalization(epsilon=1e-6)
        self.mha = MultiHeadAttention(
            num_heads=self.num_heads, key_dim=self.projection_dim
        )
        self.ffn = tf.keras.Sequential([
            Dense(self.projection_dim * 2, activation="relu"),
            Dense(self.projection_dim)
        ])
        
        # Token mapping layers
        self.to_tokens = Dense(self.projection_dim)
        self.to_patches = Dense(self.projection_dim)
        
        # Final projection back to projection_dim channels
        self.proj_back = Conv2D(
            self.projection_dim, kernel_size=1, padding="same"
        )

        super(MobileViTBlock, self).build(input_shape)

    def call(self, x):
        # Project channels
        y = self.proj_conv(x)  # (B,H,W,proj_dim)
        shape = tf.shape(y)
        b = shape[0]
        h = shape[1]
        w = shape[2]
        c = shape[3]

        # Flatten spatial dimension for token processing (B, H*W, C)
        y_flat = tf.reshape(y, [b, h * w, c])

        # Map to token dim used by MHA
        y_tokens = self.to_tokens(y_flat)  # (B, N, proj_dim)
        y_norm = self.norm(y_tokens)
        attn = self.mha(y_norm, y_norm)  # (B, N, proj_dim)
        y_tokens = y_tokens + attn
        y_tokens = y_tokens + self.ffn(y_tokens)

        # Map tokens back to spatial embeddings and reshape to H,W
        y_out = self.to_patches(y_tokens)  # (B, N, proj_dim)
        y_out = tf.reshape(y_out, [b, h, w, c])  # (B, H, W, proj_dim)
        y_out = self.proj_back(y_out)  # (B, H, W, proj_dim)

        return y_out

    def get_config(self):
        config = super(MobileViTBlock, self).get_config()
        config.update({
            "num_heads": self.num_heads,
            "projection_dim": self.projection_dim,
            "patch_h": self.patch_h,
            "patch_w": self.patch_w,
        })
        return config
