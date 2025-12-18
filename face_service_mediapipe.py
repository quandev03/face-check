import mediapipe as mp
import numpy as np
import cv2
from PIL import Image
import io
import hashlib
import logging
from typing import List, Tuple, Optional, Dict, Any
from database import db_manager
from config import Config
from minio_service import minio_service
from sklearn.metrics.pairwise import cosine_similarity

logger = logging.getLogger(__name__)

class FaceService:
    def __init__(self):
        self.tolerance = Config.FACE_RECOGNITION_TOLERANCE
        self.model_name = Config.FACE_MODEL_NAME
        self.model_version = Config.FACE_MODEL_VERSION
        self.distance_metric = Config.DISTANCE_METRIC
        
        # Initialize MediaPipe Face Detection
        self.mp_face_detection = mp.solutions.face_detection
        self.mp_face_mesh = mp.solutions.face_mesh
        self.mp_drawing = mp.solutions.drawing_utils
        
        # Initialize face detection model
        self.face_detection = self.mp_face_detection.FaceDetection(
            model_selection=1,  # 0 for close-range, 1 for full-range
            min_detection_confidence=0.5
        )
        
        # Initialize face mesh for landmarks
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            static_image_mode=True,
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )

    def extract_face_embedding(self, image_data: bytes) -> Tuple[Optional[np.ndarray], Optional[Dict], float]:
        """
        Extract face embedding from image using MediaPipe
        Returns: (embedding_vector, bbox, quality_score)
        """
        try:
            # Load image using PIL (handles JPEG better)
            image = Image.open(io.BytesIO(image_data))
            
            # Convert to RGB if needed (PIL might load as RGBA or other modes)
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            image_array = np.array(image)
            image_rgb = image_array  # PIL already gives RGB
            
            # Validate image dimensions
            height, width = image_rgb.shape[:2]
            logger.info(f"Processing image: {width}x{height}, size: {len(image_data)} bytes")
            
            if height < 50 or width < 50:
                logger.warning(f"Image too small: {width}x{height}")
                return None, None, 0.0
            
            # Resize if too large (MediaPipe works better with reasonable sizes)
            # But keep smaller images as-is (might be cropped face)
            if width > 1920 or height > 1920:
                scale = min(1920/width, 1920/height)
                new_width = int(width * scale)
                new_height = int(height * scale)
                image_rgb = cv2.resize(image_rgb, (new_width, new_height), interpolation=cv2.INTER_AREA)
                logger.info(f"Resized image from {width}x{height} to {new_width}x{new_height}")
            
            # If image is very small (likely a cropped face), enhance it
            if width < 200 or height < 200:
                logger.info("Small image detected, enhancing for better detection")
                # Enhance contrast for better detection
                image_bgr = cv2.cvtColor(image_rgb, cv2.COLOR_RGB2BGR)
                lab = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2LAB)
                l, a, b = cv2.split(lab)
                clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
                l = clahe.apply(l)
                enhanced = cv2.merge([l, a, b])
                image_rgb = cv2.cvtColor(enhanced, cv2.COLOR_BGR2RGB)
            
            # Process with MediaPipe Face Detection
            results = self.face_detection.process(image_rgb)
            
            if not results.detections:
                logger.warning(f"No faces detected in image ({width}x{height})")
                # Try with lower confidence threshold
                logger.info("Trying with lower confidence threshold...")
                temp_detector = self.mp_face_detection.FaceDetection(
                    model_selection=0,  # Try close-range model
                    min_detection_confidence=0.3
                )
                results = temp_detector.process(image_rgb)
                temp_detector.close()
                
                if not results.detections:
                    return None, None, 0.0
            
            # Get the first face detection
            detection = results.detections[0]
            bbox = detection.location_data.relative_bounding_box
            
            # Convert relative coordinates to absolute
            x = int(bbox.xmin * width)
            y = int(bbox.ymin * height)
            w = int(bbox.width * width)
            h = int(bbox.height * height)
            
            # Extract face region
            face_region = image_rgb[y:y+h, x:x+w]
            
            if face_region.size == 0:
                logger.warning("Empty face region")
                return None, None, 0.0
            
            # Resize face to standard size for embedding
            face_resized = cv2.resize(face_region, (160, 160))
            
            # Generate embedding using face landmarks
            embedding = self._generate_face_embedding(face_resized)
            
            if embedding is None:
                logger.warning("Failed to generate face embedding")
                return None, None, 0.0
            
            # Calculate quality score based on detection confidence and face size
            confidence = detection.score[0]
            face_area = w * h
            image_area = width * height
            area_ratio = face_area / image_area
            
            # Quality score combines confidence and face size
            quality_score = float(confidence * 0.7 + min(area_ratio * 10, 0.3))
            
            bbox_dict = {
                'x': x,
                'y': y,
                'width': w,
                'height': h
            }
            
            logger.info(f"Face detected: confidence={confidence:.3f}, quality={quality_score:.3f}")
            return embedding, bbox_dict, quality_score
            
        except Exception as e:
            logger.error(f"Error extracting face embedding: {str(e)}")
            return None, None, 0.0

    def _generate_face_embedding(self, face_image: np.ndarray) -> Optional[np.ndarray]:
        """
        Generate face embedding using MediaPipe face mesh landmarks
        Returns 128-dimensional vector for database compatibility
        """
        try:
            # Process with face mesh to get landmarks
            results = self.face_mesh.process(face_image)
            
            if not results.multi_face_landmarks:
                return None
            
            # Get face landmarks
            landmarks = results.multi_face_landmarks[0]
            
            # Extract landmark coordinates (478 landmarks * 3 = 1434 dimensions)
            landmark_points = []
            for landmark in landmarks.landmark:
                landmark_points.extend([landmark.x, landmark.y, landmark.z])
            
            # Convert to numpy array
            full_embedding = np.array(landmark_points, dtype=np.float32)
            
            # Reduce to 128 dimensions using PCA-like approach
            # Method: Use first 42 landmarks (42 * 3 = 126) + 2 features from overall stats = 128
            # Or use a hash/compression approach
            
            # Option 1: Use subset of important landmarks (first 42 landmarks = 126 dims)
            # Then add 2 features: face width and height ratios
            if len(full_embedding) >= 126:
                # Take first 42 landmarks (126 dimensions)
                embedding = full_embedding[:126]
                
                # Calculate face bounding box from landmarks
                x_coords = [full_embedding[i] for i in range(0, len(full_embedding), 3)]
                y_coords = [full_embedding[i+1] for i in range(0, len(full_embedding), 3)]
                
                face_width = max(x_coords) - min(x_coords) if x_coords else 0.0
                face_height = max(y_coords) - min(y_coords) if y_coords else 0.0
                
                # Add 2 features: width and height ratios
                embedding = np.append(embedding, [face_width, face_height])
            else:
                # If not enough landmarks, pad with zeros
                embedding = np.pad(full_embedding, (0, 128 - len(full_embedding)), 'constant')[:128]
            
            # Ensure exactly 128 dimensions
            if len(embedding) > 128:
                embedding = embedding[:128]
            elif len(embedding) < 128:
                embedding = np.pad(embedding, (0, 128 - len(embedding)), 'constant')
            
            # Normalize the embedding
            norm = np.linalg.norm(embedding)
            if norm > 0:
                embedding = embedding / norm
            
            logger.debug(f"Generated embedding: {len(embedding)} dimensions")
            return embedding.astype(np.float32)
            
        except Exception as e:
            logger.error(f"Error generating face embedding: {str(e)}")
            return None

    def compare_faces(self, embedding1: np.ndarray, embedding2: np.ndarray) -> float:
        """
        Compare two face embeddings using cosine similarity
        """
        try:
            # Ensure embeddings are the same length
            min_len = min(len(embedding1), len(embedding2))
            emb1 = embedding1[:min_len].reshape(1, -1)
            emb2 = embedding2[:min_len].reshape(1, -1)
            
            # Calculate cosine similarity
            similarity = cosine_similarity(emb1, emb2)[0][0]
            
            # Convert to distance (1 - similarity)
            distance = 1.0 - similarity
            
            return float(distance)
            
        except Exception as e:
            logger.error(f"Error comparing faces: {str(e)}")
            return 1.0

    def save_face_embedding(self, employee_code: str, image_data: bytes, 
                          created_by: str = None, source: str = 'ENROLL', 
                          content_type: str = 'image/jpeg') -> Dict[str, Any]:
        """
        Save face embedding to database
        """
        try:
            # Extract face embedding
            embedding, bbox, quality_score = self.extract_face_embedding(image_data)
            
            if embedding is None:
                return {
                    'success': False,
                    'error': 'No face detected in image'
                }
            
            if quality_score < 0.3:
                return {
                    'success': False,
                    'error': f'Face quality too low: {quality_score:.3f}'
                }
            
            # Generate SHA256 hash
            sha256 = hashlib.sha256(image_data).hexdigest()
            
            # Store image in MinIO if available
            image_url = None
            minio_object_name = None
            if minio_service:
                try:
                    success, object_name, url = minio_service.upload_image(
                        image_data, employee_code, content_type=content_type
                    )
                    if success:
                        minio_object_name = object_name
                        image_url = url or f"/files/{object_name}"
                except Exception as e:
                    logger.warning(f"Failed to upload to MinIO: {str(e)}")
            
            # Convert embedding to string format for database
            embedding_str = '[' + ','.join(map(str, embedding)) + ']'
            
            # Save to database
            query = """
                INSERT INTO face_embeddings 
                (employee_id, vector, quality_score, bbox, source, image_url, sha256, created_by, created_at)
                VALUES (%s, %s::vector, %s, %s, %s::face_source, %s, %s, %s, now())
                RETURNING id
            """
            
            bbox_array = [bbox['x'], bbox['y'], bbox['width'], bbox['height']] if bbox else None
            
            result = db_manager.execute_one(query, (
                employee_code,
                embedding_str,
                quality_score,
                bbox_array,
                source,
                image_url,
                sha256,
                created_by
            ))
            
            if result:
                return {
                    'success': True,
                    'face_embedding_id': result['id'],
                    'quality_score': quality_score,
                    'bbox': bbox,
                    'image_url': image_url,
                    'minio_object_name': minio_object_name
                }
            else:
                return {
                    'success': False,
                    'error': 'Failed to save face embedding'
                }
                
        except Exception as e:
            logger.error(f"Error saving face embedding: {str(e)}")
            return {
                'success': False,
                'error': f'Database error: {str(e)}'
            }

    def recognize_face(self, image_data: bytes, device_code: str = None) -> Dict[str, Any]:
        """
        Recognize face in image
        """
        try:
            # Extract face embedding from input image
            embedding, bbox, quality_score = self.extract_face_embedding(image_data)
            
            if embedding is None:
                return {
                    'success': False,
                    'employee_code': None,
                    'confidence': 0.0,
                    'distance': 1.0,
                    'message': 'No face detected'
                }
            
            if quality_score < 0.3:
                return {
                    'success': False,
                    'employee_code': None,
                    'confidence': 0.0,
                    'distance': 1.0,
                    'message': f'Face quality too low: {quality_score:.3f}'
                }
            
            # Get all face embeddings from database
            query = """
                SELECT id, employee_id, vector, quality_score
                FROM face_embeddings 
                WHERE status = 'ACTIVE'
            """
            
            embeddings = db_manager.execute_query(query, fetch=True)
            
            if not embeddings:
                return {
                    'success': False,
                    'employee_code': None,
                    'confidence': 0.0,
                    'distance': 1.0,
                    'message': 'No registered faces found'
                }
            
            # Find best match
            best_match = None
            best_distance = float('inf')
            
            for emb in embeddings:
                try:
                    # Parse stored embedding
                    stored_embedding = np.array(eval(emb['vector']), dtype=np.float32)
                    
                    # Compare embeddings
                    distance = self.compare_faces(embedding, stored_embedding)
                    
                    if distance < best_distance:
                        best_distance = distance
                        best_match = emb
                        
                except Exception as e:
                    logger.warning(f"Error comparing with embedding {emb['id']}: {str(e)}")
                    continue
            
            # Check if match is good enough
            if best_match and best_distance <= self.tolerance:
                # Log attendance
                self._log_attendance(best_match['employee_id'], device_code, 
                                   best_distance, quality_score, bbox)
                
                return {
                    'success': True,
                    'employee_code': best_match['employee_id'],
                    'confidence': 1.0 - best_distance,
                    'distance': best_distance,
                    'quality_score': quality_score,
                    'message': 'Face recognized successfully'
                }
            else:
                return {
                    'success': False,
                    'employee_code': None,
                    'confidence': 0.0,
                    'distance': best_distance,
                    'message': f'No matching face found (distance: {best_distance:.3f})'
                }
                
        except Exception as e:
            logger.error(f"Error recognizing face: {str(e)}")
            return {
                'success': False,
                'employee_code': None,
                'confidence': 0.0,
                'distance': 1.0,
                'message': f'Recognition error: {str(e)}'
            }

    def _log_attendance(self, employee_code: str, device_code: str, 
                       distance: float, quality_score: float, bbox: Dict):
        """
        Log attendance recognition
        """
        try:
            query = """
                INSERT INTO attendance_logs 
                (employee_code, device_code, confidence, distance, quality_score, bbox, recognized_at)
                VALUES (%s, %s, %s, %s, %s, %s, now())
            """
            
            bbox_array = [bbox['x'], bbox['y'], bbox['width'], bbox['height']] if bbox else None
            
            db_manager.execute_query(query, (
                employee_code,
                device_code,
                1.0 - distance,  # confidence
                distance,
                quality_score,
                bbox_array
            ))
            
            logger.info(f"Attendance logged for {employee_code}")
            
        except Exception as e:
            logger.error(f"Error logging attendance: {str(e)}")

    def get_face_embeddings(self, employee_code: str = None) -> List[Dict]:
        """
        Get face embeddings from database
        """
        try:
            if employee_code:
                query = """
                    SELECT id, employee_id, quality_score, source, created_at
                    FROM face_embeddings 
                    WHERE employee_id = %s AND status = 'ACTIVE'
                    ORDER BY created_at DESC
                """
                params = (employee_code,)
            else:
                query = """
                    SELECT id, employee_id, quality_score, source, created_at
                    FROM face_embeddings 
                    WHERE status = 'ACTIVE'
                    ORDER BY created_at DESC
                """
                params = ()
            
            embeddings = db_manager.execute_query(query, params, fetch=True)
            return [dict(emb) for emb in embeddings]
            
        except Exception as e:
            logger.error(f"Error getting face embeddings: {str(e)}")
            return []

    def update_face_embedding(self, face_id: int, **kwargs) -> Dict[str, Any]:
        """
        Update face embedding
        """
        try:
            # Build update query dynamically
            update_fields = []
            params = []
            
            for field, value in kwargs.items():
                if field in ['quality_score', 'source', 'status']:
                    update_fields.append(f"{field} = %s")
                    params.append(value)
            
            if not update_fields:
                return {
                    'success': False,
                    'error': 'No valid fields to update'
                }
            
            query = f"""
                UPDATE face_embeddings 
                SET {', '.join(update_fields)}, updated_at = now()
                WHERE id = %s
                RETURNING id
            """
            params.append(face_id)
            
            result = db_manager.execute_one(query, tuple(params))
            
            if result:
                return {
                    'success': True,
                    'face_embedding_id': result['id']
                }
            else:
                return {
                    'success': False,
                    'error': 'Face embedding not found'
                }
                
        except Exception as e:
            logger.error(f"Error updating face embedding: {str(e)}")
            return {
                'success': False,
                'error': f'Update error: {str(e)}'
            }

    def delete_face_embedding(self, face_id: int, hard_delete: bool = False) -> Dict[str, Any]:
        """
        Delete face embedding
        """
        try:
            if hard_delete:
                query = "DELETE FROM face_embeddings WHERE id = %s"
                result = db_manager.execute_query(query, (face_id,))
                message = "Face embedding permanently deleted"
            else:
                query = "UPDATE face_embeddings SET status = 'DELETED' WHERE id = %s"
                result = db_manager.execute_query(query, (face_id,))
                message = "Face embedding marked as deleted"
            
            if result > 0:
                return {
                    'success': True,
                    'message': message
                }
            else:
                return {
                    'success': False,
                    'error': 'Face embedding not found'
                }
                
        except Exception as e:
            logger.error(f"Error deleting face embedding: {str(e)}")
            return {
                'success': False,
                'error': f'Delete error: {str(e)}'
            }

    def delete_face_embedding_by_employee_code(self, employee_code):
        """
        Xoá (hoặc disable) toàn bộ face embedding của nhân viên
        """
        try:
            query = """
                    DELETE FROM face_embeddings
                    WHERE employee_code = %s
                    RETURNING id 
                    """
            db_manager.execute_one(query, (employee_code,))
            return True

        except Exception as e:
            logger.error(
                f"Failed to delete face embedding for employee_code={employee_code}: {str(e)}"
            )
            raise
# Global face service instance
face_service = FaceService()










