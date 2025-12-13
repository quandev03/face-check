"""
Camera Service for real-time face detection and capture
"""
import cv2
import numpy as np
import threading
import time
import logging
from typing import Optional, Callable, Dict, Any
from queue import Queue

# Import gui_app.config - PyInstaller will bundle it correctly
try:
    from gui_app.config import AppConfig
    from gui_app.utils.face_detector import FaceDetector
    from gui_app.utils.image_utils import resize_image, image_to_bytes
except ImportError:
    # Fallback if running from gui_app directory
    from config import AppConfig
    from utils.face_detector import FaceDetector
    from utils.image_utils import resize_image, image_to_bytes

logger = logging.getLogger(__name__)


class CameraService:
    """Service for camera capture and face detection"""
    
    def __init__(
        self,
        camera_index: int = None,
        width: int = None,
        height: int = None,
        face_detector: FaceDetector = None
    ):
        """
        Initialize camera service
        
        Args:
            camera_index: Camera device index (default: 0)
            width: Camera width (default: 640)
            height: Camera height (default: 480)
            face_detector: Face detector instance (creates new if None)
        """
        self.camera_index = camera_index or AppConfig.CAMERA_INDEX
        self.width = width or AppConfig.CAMERA_WIDTH
        self.height = height or AppConfig.CAMERA_HEIGHT
        
        self.cap: Optional[cv2.VideoCapture] = None
        self.is_running = False
        self.current_frame: Optional[np.ndarray] = None
        self.current_detection: Optional[Dict[str, Any]] = None
        
        # Initialize face detector with error handling
        try:
            self.face_detector = face_detector or FaceDetector(
                min_detection_confidence=AppConfig.FACE_DETECTION_CONFIDENCE
            )
        except Exception as e:
            logger.error(f"Failed to initialize FaceDetector: {str(e)}")
            raise
        
        # Callbacks
        self.frame_callback: Optional[Callable] = None
        self.detection_callback: Optional[Callable] = None
        
        # Auto-capture settings
        self.auto_capture_enabled = False
        self.auto_capture_delay = AppConfig.AUTO_CAPTURE_DELAY
        self.auto_capture_quality_threshold = AppConfig.FACE_QUALITY_THRESHOLD
        self.auto_capture_timer = None
        self.last_detection_time = None
        
        # Threading
        self.capture_thread: Optional[threading.Thread] = None
        self.lock = threading.Lock()
    
    def start(self) -> bool:
        """
        Start camera capture
        
        Returns:
            True if started successfully, False otherwise
        """
        if self.is_running:
            logger.warning("Camera is already running")
            return True
        
        try:
            self.cap = cv2.VideoCapture(self.camera_index)
            
            if not self.cap.isOpened():
                logger.error(f"Failed to open camera {self.camera_index}")
                return False
            
            # Set camera properties
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
            
            self.is_running = True
            self.capture_thread = threading.Thread(target=self._capture_loop, daemon=True)
            self.capture_thread.start()
            
            logger.info(f"Camera started: {self.camera_index} ({self.width}x{self.height})")
            return True
            
        except Exception as e:
            logger.error(f"Error starting camera: {str(e)}")
            self.is_running = False
            return False
    
    def stop(self):
        """Stop camera capture"""
        if not self.is_running:
            return
        
        self.is_running = False
        
        if self.capture_thread:
            self.capture_thread.join(timeout=2.0)
        
        if self.cap:
            self.cap.release()
            self.cap = None
        
        with self.lock:
            self.current_frame = None
            self.current_detection = None
        
        logger.info("Camera stopped")
    
    def _capture_loop(self):
        """Main capture loop running in separate thread"""
        while self.is_running:
            try:
                ret, frame = self.cap.read()
                
                if not ret:
                    logger.warning("Failed to read frame from camera")
                    time.sleep(0.1)
                    continue
                
                # Resize frame if needed
                frame = resize_image(frame, max_width=800, max_height=600)
                
                # Detect faces
                detections = self.face_detector.detect_faces(frame)
                best_detection = detections[0] if detections else None
                
                # Update current frame and detection
                with self.lock:
                    self.current_frame = frame.copy()
                    self.current_detection = best_detection
                
                # Call frame callback
                if self.frame_callback:
                    try:
                        self.frame_callback(frame, best_detection)
                    except Exception as e:
                        logger.error(f"Error in frame callback: {str(e)}")
                
                # Handle auto-capture
                if self.auto_capture_enabled and best_detection:
                    self._handle_auto_capture(best_detection, frame)
                elif not best_detection:
                    self._reset_auto_capture()
                
                # Call detection callback
                if self.detection_callback and best_detection:
                    try:
                        self.detection_callback(best_detection, frame)
                    except Exception as e:
                        logger.error(f"Error in detection callback: {str(e)}")
                
                # Small delay to prevent excessive CPU usage
                time.sleep(0.03)  # ~30 FPS
                
            except Exception as e:
                logger.error(f"Error in capture loop: {str(e)}")
                time.sleep(0.1)
    
    def _handle_auto_capture(self, detection: Dict[str, Any], frame: np.ndarray):
        """Handle auto-capture logic"""
        current_time = time.time()
        
        # Check quality threshold
        x, y, w, h = detection['bbox']
        quality_score = self.face_detector.calculate_quality_score(frame, (x, y, w, h))
        
        if quality_score < self.auto_capture_quality_threshold:
            self._reset_auto_capture()
            return
        
        # Check if face detected continuously for delay period
        if self.last_detection_time is None:
            self.last_detection_time = current_time
        
        elapsed = current_time - self.last_detection_time
        
        if elapsed >= self.auto_capture_delay:
            # Trigger auto-capture
            self._reset_auto_capture()
            if hasattr(self, 'auto_capture_callback'):
                try:
                    self.auto_capture_callback(frame, detection, quality_score)
                except Exception as e:
                    logger.error(f"Error in auto-capture callback: {str(e)}")
        else:
            # Update timer display if callback exists
            if hasattr(self, 'auto_capture_timer_callback'):
                try:
                    remaining = self.auto_capture_delay - elapsed
                    self.auto_capture_timer_callback(remaining)
                except Exception as e:
                    logger.error(f"Error in timer callback: {str(e)}")
    
    def _reset_auto_capture(self):
        """Reset auto-capture timer"""
        self.last_detection_time = None
    
    def get_current_frame(self) -> Optional[np.ndarray]:
        """Get current frame (thread-safe)"""
        with self.lock:
            return self.current_frame.copy() if self.current_frame is not None else None
    
    def get_current_detection(self) -> Optional[Dict[str, Any]]:
        """Get current face detection (thread-safe)"""
        with self.lock:
            return self.current_detection.copy() if self.current_detection else None
    
    def capture_frame(self) -> Optional[np.ndarray]:
        """Capture current frame"""
        return self.get_current_frame()
    
    def capture_face_image(self) -> Optional[bytes]:
        """
        Capture face image from current frame
        
        Returns:
            Image bytes (JPEG) or None if no face detected
        """
        frame = self.get_current_frame()
        detection = self.get_current_detection()
        
        if frame is None or detection is None:
            return None
        
        # Extract face region
        x, y, w, h = detection['bbox']
        face_region = self.face_detector.extract_face_region(frame, (x, y, w, h))
        
        if face_region is None:
            return None
        
        # Convert to bytes
        return image_to_bytes(face_region, format='JPEG', quality=95)
    
    def set_frame_callback(self, callback: Callable):
        """Set callback for new frames"""
        self.frame_callback = callback
    
    def set_detection_callback(self, callback: Callable):
        """Set callback for face detections"""
        self.detection_callback = callback
    
    def set_auto_capture_callback(self, callback: Callable):
        """Set callback for auto-capture"""
        self.auto_capture_callback = callback
    
    def set_auto_capture_timer_callback(self, callback: Callable):
        """Set callback for auto-capture timer updates"""
        self.auto_capture_timer_callback = callback
    
    def enable_auto_capture(self, enabled: bool = True):
        """Enable/disable auto-capture"""
        self.auto_capture_enabled = enabled
        if not enabled:
            self._reset_auto_capture()
    
    def set_auto_capture_delay(self, delay: float):
        """Set auto-capture delay in seconds"""
        self.auto_capture_delay = delay
    
    def set_auto_capture_quality_threshold(self, threshold: float):
        """Set minimum quality score for auto-capture"""
        self.auto_capture_quality_threshold = threshold
    
    def get_frame_with_detection(self) -> Optional[np.ndarray]:
        """
        Get current frame with detection overlay drawn
        
        Returns:
            Frame with detection drawn or None
        """
        frame = self.get_current_frame()
        detection = self.get_current_detection()
        
        if frame is None:
            return None
        
        if detection:
            # Draw detection
            frame = self.face_detector.draw_detection(frame, detection)
            
            # Draw quality score
            x, y, w, h = detection['bbox']
            quality_score = self.face_detector.calculate_quality_score(frame, (x, y, w, h))
            quality_text = f"Quality: {quality_score:.2f}"
            cv2.putText(frame, quality_text, (x, y + h + 20),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        
        return frame
    
    def cleanup(self):
        """Cleanup resources"""
        self.stop()
        if self.face_detector:
            self.face_detector.cleanup()

