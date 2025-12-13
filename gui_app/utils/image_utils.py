"""
Image processing utilities
"""
import cv2
import numpy as np
from PIL import Image
from typing import Optional, Tuple
import io


def pil_to_cv2(pil_image: Image.Image) -> np.ndarray:
    """Convert PIL Image to OpenCV format (BGR)"""
    if pil_image.mode == 'RGB':
        return np.array(pil_image)[:, :, ::-1]  # RGB to BGR
    elif pil_image.mode == 'RGBA':
        return cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGBA2BGR)
    else:
        return np.array(pil_image)


def cv2_to_pil(cv2_image: np.ndarray) -> Image.Image:
    """Convert OpenCV image (BGR) to PIL Image (RGB)"""
    if len(cv2_image.shape) == 3:
        rgb_image = cv2.cvtColor(cv2_image, cv2.COLOR_BGR2RGB)
    else:
        rgb_image = cv2_image
    return Image.fromarray(rgb_image)


def resize_image(image: np.ndarray, max_width: int = 800, max_height: int = 600) -> np.ndarray:
    """Resize image maintaining aspect ratio"""
    height, width = image.shape[:2]
    
    if width <= max_width and height <= max_height:
        return image
    
    scale = min(max_width / width, max_height / height)
    new_width = int(width * scale)
    new_height = int(height * scale)
    
    return cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_AREA)


def image_to_bytes(image: np.ndarray, format: str = 'JPEG', quality: int = 95) -> bytes:
    """Convert OpenCV image to bytes"""
    pil_image = cv2_to_pil(image)
    buffer = io.BytesIO()
    pil_image.save(buffer, format=format, quality=quality)
    return buffer.getvalue()


def bytes_to_image(image_bytes: bytes) -> np.ndarray:
    """Convert image bytes to OpenCV format"""
    pil_image = Image.open(io.BytesIO(image_bytes))
    return pil_to_cv2(pil_image)


def enhance_image(image: np.ndarray) -> np.ndarray:
    """Enhance image for better face detection"""
    # Convert to LAB color space
    lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    
    # Apply CLAHE (Contrast Limited Adaptive Histogram Equalization)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    l = clahe.apply(l)
    
    # Merge channels and convert back
    enhanced = cv2.merge([l, a, b])
    enhanced = cv2.cvtColor(enhanced, cv2.COLOR_LAB2BGR)
    
    return enhanced





