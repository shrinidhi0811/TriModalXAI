"""
Preprocessing utilities for tri-modal leaf classification.
Handles background removal, vein enhancement, and texture enhancement.
"""

import cv2
import numpy as np
from io import BytesIO
from PIL import Image
from rembg import remove
from skimage.filters import frangi
from skimage import exposure
from skimage.feature import local_binary_pattern
from skimage.filters import gabor
from skimage.util import img_as_ubyte
from skimage.filters import unsharp_mask


def remove_background(image_bytes: bytes) -> np.ndarray:
    """
    Remove background from an image using rembg library.
    
    Args:
        image_bytes: Raw image bytes (from uploaded file)
    
    Returns:
        RGB image array (H, W, 3) with background removed (black background)
    """
    # Remove background
    removed_bg = remove(image_bytes)
    
    # Convert bytes back to an image
    img = Image.open(BytesIO(removed_bg)).convert("RGBA")
    
    # Create a black background
    black_bg = Image.new("RGBA", img.size, (0, 0, 0, 255))
    
    # Paste the foreground object onto the black background
    final_img = Image.alpha_composite(black_bg, img)
    
    # Convert to RGB numpy array
    rgb_img = np.array(final_img.convert("RGB"))
    
    return rgb_img


def resize_image(image: np.ndarray, target_size: tuple = (224, 224)) -> np.ndarray:
    """
    Resize image to target size using high-quality interpolation.
    
    Args:
        image: Input image array (H, W, 3) or (H, W)
        target_size: Target size as (height, width)
    
    Returns:
        Resized image array
    """
    # Use INTER_AREA for shrinking (best quality), INTER_CUBIC for enlarging
    h, w = image.shape[:2]
    target_h, target_w = target_size
    
    if h > target_h or w > target_w:
        interpolation = cv2.INTER_AREA
    else:
        interpolation = cv2.INTER_CUBIC
    
    resized = cv2.resize(image, (target_w, target_h), interpolation=interpolation)
    
    return resized


def vein_enhancement(rgb_image: np.ndarray) -> np.ndarray:
    """
    Apply vein enhancement using CLAHE + Frangi filter + morphological top-hat.
    
    Args:
        rgb_image: RGB image array (H, W, 3)
    
    Returns:
        Vein-enhanced grayscale image (H, W)
    """
    # Step 1: Extract green channel
    green_channel = rgb_image[:, :, 1]
    
    # Step 2: Apply CLAHE
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    green_clahe = clahe.apply(green_channel)
    
    # Step 3: Apply Frangi filter
    frangi_filtered = frangi(green_clahe, scale_range=(1, 4), scale_step=1)
    
    # Normalize to 0–255
    frangi_norm = cv2.normalize(
        frangi_filtered, None, 0, 255, cv2.NORM_MINMAX
    ).astype(np.uint8)
    
    # Step 4: Morphological top-hat
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
    top_hat = cv2.morphologyEx(frangi_norm, cv2.MORPH_TOPHAT, kernel)
    
    # Step 5: Contrast stretching
    p2, p98 = np.percentile(top_hat, (2, 98))
    contrast_stretched = exposure.rescale_intensity(top_hat, in_range=(p2, p98))
    
    # Ensure uint8 format
    final_result = (
        (contrast_stretched * 255).astype(np.uint8)
        if contrast_stretched.max() <= 1
        else contrast_stretched
    )
    
    return final_result


def texture_enhancement(rgb_image: np.ndarray) -> np.ndarray:
    """
    Apply texture enhancement using LBP, Gabor filters, and unsharp masking.
    
    Args:
        rgb_image: RGB image array (H, W, 3)
    
    Returns:
        Texture-enhanced RGB image (H, W, 3)
    """
    # LBP and Gabor Parameters
    radius = 2
    n_points = 8 * radius
    method = "uniform"
    
    frequencies = [0.2, 0.3]
    orientations = [0, np.pi / 4, np.pi / 2, 3 * np.pi / 4]
    
    # Convert to grayscale
    gray = cv2.cvtColor(rgb_image, cv2.COLOR_RGB2GRAY)
    
    # Apply unsharp mask
    unsharp = unsharp_mask(gray, radius=1, amount=1)
    unsharp = img_as_ubyte(unsharp)
    
    # Local Binary Pattern
    lbp = local_binary_pattern(unsharp, n_points, radius, method).astype(np.uint8)
    
    # Gabor filter responses
    gabor_responses = []
    for theta in orientations:
        for freq in frequencies:
            real, imag = gabor(unsharp, frequency=freq, theta=theta)
            mag = np.sqrt(real**2 + imag**2)
            gabor_responses.append(mag)
    
    gabor_combined = np.max(np.array(gabor_responses), axis=0)
    gabor_combined = img_as_ubyte(gabor_combined / gabor_combined.max())
    
    # Merge into 3-channel image
    merged = cv2.merge([
        cv2.equalizeHist(lbp),
        gabor_combined,
        unsharp
    ])
    
    # Convert BGR to RGB (cv2.merge creates BGR)
    merged_rgb = cv2.cvtColor(merged, cv2.COLOR_BGR2RGB)
    
    return merged_rgb


def preprocess_all_modalities(image_bytes: bytes, target_size: tuple = (224, 224)) -> tuple:
    """
    Complete preprocessing pipeline: background removal -> vein & texture enhancement -> resize.
    
    Args:
        image_bytes: Raw image bytes from uploaded file
        target_size: Target size for model input (default: 224x224)
    
    Returns:
        Tuple of (rgb_clean, vein_enhanced, texture_enhanced) as numpy arrays,
        all resized to target_size
    """
    # Step 1: Remove background
    rgb_clean = remove_background(image_bytes)
    
    # Step 2: Vein enhancement (returns grayscale, need to convert to 3-channel)
    vein_gray = vein_enhancement(rgb_clean)
    vein_3ch = cv2.cvtColor(vein_gray, cv2.COLOR_GRAY2RGB)
    
    # Step 3: Texture enhancement
    texture_3ch = texture_enhancement(rgb_clean)
    
    # Step 4: Resize all modalities to target size (CRITICAL FOR MODEL!)
    rgb_resized = resize_image(rgb_clean, target_size)
    vein_resized = resize_image(vein_3ch, target_size)
    texture_resized = resize_image(texture_3ch, target_size)
    
    return rgb_resized, vein_resized, texture_resized
