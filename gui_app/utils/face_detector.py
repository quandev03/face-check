"""
Face Detection Utilities using MediaPipe
"""
import mediapipe as mp
import numpy as np
import cv2
from typing import Optional, Tuple, Dict, Any
import logging
import sys
import os

logger = logging.getLogger(__name__)


class FaceDetector:
    """Face detection using MediaPipe"""
    
    def __init__(self, min_detection_confidence: float = 0.5):
        """
        Initialize face detector
        
        Args:
            min_detection_confidence: Minimum confidence for face detection (0.0-1.0)
        """
        self.min_detection_confidence = min_detection_confidence
        
        try:
            # Initialize MediaPipe Face Detection
            self.mp_face_detection = mp.solutions.face_detection
            self.face_detection = self.mp_face_detection.FaceDetection(
                model_selection=1,  # 0 for close-range, 1 for full-range
                min_detection_confidence=min_detection_confidence
            )
            
            # Initialize face mesh for landmarks (optional, for better quality assessment)
            self.mp_face_mesh = mp.solutions.face_mesh
            self.face_mesh = self.mp_face_mesh.FaceMesh(
                static_image_mode=False,
                max_num_faces=1,
                refine_landmarks=True,
                min_detection_confidence=0.5,
                min_tracking_confidence=0.5
            )
            
            logger.info("MediaPipe FaceDetector initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing MediaPipe FaceDetector: {str(e)}")
            logger.error(f"Error type: {type(e).__name__}")
            # Re-raise with more context
            raise Exception(f"Failed to initialize face detector: {str(e)}") from e
    
    def detect_faces(self, image: np.ndarray) -> list:
        """
        Detect faces in image
        
        Args:
            image: BGR or RGB image array
        
        Returns:
            List of detection results, each containing:
            - bbox: (x, y, w, h) bounding box
            - confidence: Detection confidence
            - landmarks: Face landmarks (if available)
        """
        # Convert BGR to RGB if needed
        if len(image.shape) == 3 and image.shape[2] == 3:
            # Check if it's BGR (OpenCV default)
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        else:
            image_rgb = image
        
        height, width = image_rgb.shape[:2]
        
        # Process with MediaPipe
        results = self.face_detection.process(image_rgb)
        
        detections = []
        if results.detections:
            for detection in results.detections:
                # Get bounding box
                bbox = detection.location_data.relative_bounding_box
                
                # Convert relative coordinates to absolute
                x = int(bbox.xmin * width)
                y = int(bbox.ymin * height)
                w = int(bbox.width * width)
                h = int(bbox.height * height)
                
                # Ensure coordinates are within image bounds
                x = max(0, x)
                y = max(0, y)
                w = min(w, width - x)
                h = min(h, height - y)
                
                detections.append({
                    'bbox': (x, y, w, h),
                    'confidence': detection.score[0],
                    'landmarks': detection.location_data.relative_keypoints if hasattr(detection.location_data, 'relative_keypoints') else None
                })
        
        return detections
    
    def get_best_face(self, image: np.ndarray) -> Optional[Dict[str, Any]]:
        """
        Get the best (largest) face from image
        
        Args:
            image: BGR or RGB image array
        
        Returns:
            Best face detection result or None
        """
        detections = self.detect_faces(image)
        
        if not detections:
            return None
        
        # Return the face with largest area
        best_face = max(detections, key=lambda d: d['bbox'][2] * d['bbox'][3])
        return best_face
    
    def calculate_quality_score(self, image: np.ndarray, bbox: Tuple[int, int, int, int]) -> float:
        """
        Calculate quality score for a face region
        
        Args:
            image: BGR or RGB image array
            bbox: (x, y, w, h) bounding box
        
        Returns:
            Quality score (0.0-1.0)
        """
        x, y, w, h = bbox
        
        # Extract face region
        if len(image.shape) == 3:
            face_region = image[y:y+h, x:x+w]
        else:
            face_region = image[y:y+h, x:x+w]
        
        if face_region.size == 0:
            return 0.0
        
        # Convert to grayscale for analysis
        if len(face_region.shape) == 3:
            gray = cv2.cvtColor(face_region, cv2.COLOR_BGR2GRAY)
        else:
            gray = face_region
        
        # Calculate quality metrics
        scores = []
        
        # 1. Face size score (larger is better, but not too large)
        face_area = w * h
        image_area = image.shape[0] * image.shape[1]
        size_ratio = face_area / image_area
        # Optimal size is around 10-30% of image
        if 0.1 <= size_ratio <= 0.3:
            size_score = 1.0
        elif size_ratio < 0.1:
            size_score = size_ratio / 0.1
        else:
            size_score = max(0.0, 1.0 - (size_ratio - 0.3) / 0.7)
        scores.append(size_score)
        
        # 2. Blur detection (Laplacian variance)
        laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
        blur_score = min(1.0, laplacian_var / 100.0)  # Normalize
        scores.append(blur_score)
        
        # 3. Brightness score (not too dark, not too bright)
        mean_brightness = np.mean(gray)
        # Optimal brightness is around 100-180
        if 100 <= mean_brightness <= 180:
            brightness_score = 1.0
        elif mean_brightness < 100:
            brightness_score = mean_brightness / 100.0
        else:
            brightness_score = max(0.0, 1.0 - (mean_brightness - 180) / 75.0)
        scores.append(brightness_score)
        
        # 4. Contrast score
        contrast = np.std(gray)
        contrast_score = min(1.0, contrast / 50.0)  # Normalize
        scores.append(contrast_score)
        
        # Weighted average
        quality_score = (
            size_score * 0.3 +
            blur_score * 0.3 +
            brightness_score * 0.2 +
            contrast_score * 0.2
        )
        
        return float(quality_score)
    
    def extract_face_region(self, image: np.ndarray, bbox: Tuple[int, int, int, int], 
                           padding: int = 20) -> Optional[np.ndarray]:
        """
        Extract face region from image with padding
        
        Args:
            image: BGR or RGB image array
            bbox: (x, y, w, h) bounding box
            padding: Padding pixels around face
        
        Returns:
            Extracted face region or None
        """
        x, y, w, h = bbox
        
        # Add padding
        x = max(0, x - padding)
        y = max(0, y - padding)
        w = min(w + 2 * padding, image.shape[1] - x)
        h = min(h + 2 * padding, image.shape[0] - y)
        
        # Extract region
        face_region = image[y:y+h, x:x+w]
        
        if face_region.size == 0:
            return None
        
        return face_region
    
    def draw_detection(self, image: np.ndarray, detection: Dict[str, Any], 
                      color: Tuple[int, int, int] = (0, 255, 0),
                      thickness: int = 2) -> np.ndarray:
        """
        Draw face detection on image
        
        Args:
            image: BGR or RGB image array
            detection: Detection result dictionary
            color: BGR color tuple
            thickness: Line thickness
        
        Returns:
            Image with detection drawn
        """
        image_copy = image.copy()
        x, y, w, h = detection['bbox']
        
        # Draw rectangle
        cv2.rectangle(image_copy, (x, y), (x + w, y + h), color, thickness)
        
        # Draw confidence score
        confidence = detection.get('confidence', 0.0)
        label = f"Face: {confidence:.2f}"
        cv2.putText(image_copy, label, (x, y - 10),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, thickness)
        
        return image_copy
    
    def cleanup(self):
        """Cleanup resources"""
        if hasattr(self, 'face_detection'):
            self.face_detection.close()
        if hasattr(self, 'face_mesh'):
            self.face_mesh.close()

