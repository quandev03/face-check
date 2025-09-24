import face_recognition
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

logger = logging.getLogger(__name__)

class FaceService:
    def __init__(self):
        self.tolerance = Config.FACE_RECOGNITION_TOLERANCE
        self.model_name = Config.FACE_MODEL_NAME
        self.model_version = Config.FACE_MODEL_VERSION
        self.distance_metric = Config.DISTANCE_METRIC
    

    def extract_face_embedding(self, image_data: bytes) -> Tuple[Optional[np.ndarray], Optional[Dict], float]:
        """
        Extract face embedding from image with improved quality assessment
        Returns: (embedding_vector, bbox, quality_score)
        """
        try:
            # Load image
            image = Image.open(io.BytesIO(image_data))
            image_array = np.array(image)
            
            # Convert to RGB if needed
            if len(image_array.shape) == 3 and image_array.shape[2] == 3:
                image_rgb = cv2.cvtColor(image_array, cv2.COLOR_BGR2RGB)
            else:
                image_rgb = image_array
            
            # Resize image if too large (improve performance)
            height, width = image_rgb.shape[:2]
            if width > 1024 or height > 1024:
                scale = min(1024/width, 1024/height)
                new_width = int(width * scale)
                new_height = int(height * scale)
                image_rgb = cv2.resize(image_rgb, (new_width, new_height))
                logger.info(f"Resized image from {width}x{height} to {new_width}x{new_height}")
            
            # Find face locations with different models for better accuracy
            face_locations = face_recognition.face_locations(image_rgb, model='hog')
            
            if not face_locations:
                # Try with CNN model if HOG fails
                face_locations = face_recognition.face_locations(image_rgb, model='cnn')
                logger.info("HOG model failed, trying CNN model")
            
            if not face_locations:
                logger.warning("No face found in image")
                return None, None, 0.0
            
            if len(face_locations) > 1:
                logger.warning(f"Multiple faces found ({len(face_locations)}), using the largest one")
                # Use the largest face
                largest_face = max(face_locations, key=lambda x: (x[2]-x[0])*(x[1]-x[3]))
                face_location = largest_face
            else:
                face_location = face_locations[0]
            
            top, right, bottom, left = face_location
            
            # Extract face encoding with better parameters
            face_encodings = face_recognition.face_encodings(image_rgb, [face_location], num_jitters=2)
            
            if not face_encodings:
                logger.warning("Could not encode face")
                return None, None, 0.0
            
            embedding = face_encodings[0]
            
            # Calculate improved quality score
            face_width = right - left
            face_height = bottom - top
            face_area = face_width * face_height
            image_area = image_rgb.shape[0] * image_rgb.shape[1]
            
            # Quality factors
            size_ratio = face_area / image_area
            aspect_ratio = face_width / face_height if face_height > 0 else 0
            
            # Face should be 5-30% of image and have reasonable aspect ratio
            size_score = min(1.0, max(0.0, (size_ratio - 0.05) / 0.25))  # 5-30% range
            aspect_score = 1.0 - abs(aspect_ratio - 0.8) / 0.4  # Prefer 0.8 aspect ratio
            aspect_score = max(0.0, min(1.0, aspect_score))
            
            quality_score = (size_score * 0.7 + aspect_score * 0.3)
            
            bbox = {
                'top': int(top),
                'right': int(right), 
                'bottom': int(bottom),
                'left': int(left)
            }
            
            logger.info(f"Face quality: size_ratio={size_ratio:.3f}, aspect_ratio={aspect_ratio:.3f}, quality_score={quality_score:.3f}")
            
            return embedding, bbox, quality_score
            
        except Exception as e:
            logger.error(f"Error extracting face embedding: {e}")
            return None, None, 0.0
    def calculate_image_hash(self, image_data: bytes) -> str:
        """Calculate SHA256 hash of image data"""
        return hashlib.sha256(image_data).hexdigest()
    
    def save_face_embedding(self, employee_code: str, image_data: bytes, 
                          created_by: str = None, source: str = 'ENROLL',
                          content_type: str = 'image/jpeg') -> Dict[str, Any]:
        """
        Save face embedding to database and optionally store image in MinIO
        """
        try:
            # Extract face embedding
            embedding, bbox, quality_score = self.extract_face_embedding(image_data)
            
            if embedding is None:
                return {
                    'success': False,
                    'error': 'No face found in image or could not extract embedding'
                }
            
            # Calculate image hash
            image_hash = self.calculate_image_hash(image_data)
            
            # Check if this face already exists
            existing_query = """
                SELECT id FROM face_embeddings 
                WHERE sha256 = %s AND status = 'ACTIVE'
            """
            existing = db_manager.execute_one(existing_query, (image_hash,))
            
            if existing:
                return {
                    'success': False,
                    'error': 'This face image already exists in the database'
                }
            
            # Upload image to MinIO if service is available
            image_url = None
            minio_object_name = None
            
            if minio_service and Config.STORE_ORIGINAL_IMAGES:
                try:
                    success, object_name, url = minio_service.upload_image(
                        image_data, employee_code, content_type
                    )
                    if success:
                        image_url = url
                        minio_object_name = object_name
                        logger.info(f"Image uploaded to MinIO: {object_name}")
                    else:
                        logger.warning("Failed to upload image to MinIO, continuing without image storage")
                except Exception as e:
                    logger.warning(f"MinIO upload failed: {e}, continuing without image storage")
            
            # Convert embedding to list for database storage
            embedding_list = embedding.tolist()
            bbox_array = [bbox['top'], bbox['right'], bbox['bottom'], bbox['left']] if bbox else None
            
            # Insert into database
            insert_query = """
                INSERT INTO face_embeddings 
                (employee_id, vector, model_name, model_version, distance_metric, 
                 quality_score, bbox, source, image_url, sha256, created_by)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id
            """
            
            result = db_manager.execute_one(insert_query, (
                employee_code,
                embedding_list,
                self.model_name,
                self.model_version,
                self.distance_metric,
                quality_score,
                bbox_array,
                source,
                image_url,
                image_hash,
                created_by
            ))
            
            return {
                'success': True,
                'face_embedding_id': result['id'],
                'quality_score': quality_score,
                'bbox': bbox,
                'image_url': image_url,
                'minio_object_name': minio_object_name
            }
            
        except Exception as e:
            logger.error(f"Error saving face embedding: {e}")
            return {
                'success': False,
                'error': f'Database error: {str(e)}'
            }
    

    def recognize_face(self, image_data: bytes) -> Dict[str, Any]:
        """
        Recognize face with improved accuracy using multiple templates
        """
        try:
            # Extract face embedding from input image
            input_embedding, bbox, quality_score = self.extract_face_embedding(image_data)
            
            if input_embedding is None:
                return {
                    'success': False,
                    'error': 'No face found in image or could not extract embedding'
                }
            
            # Get all stored embeddings with employee info
            query = """
                SELECT fe.id, fe.employee_id, fe.vector, fe.quality_score,
                       e.employee_code, e.full_name, e.department, e.position
                FROM face_embeddings fe
                JOIN employees e ON fe.employee_id = e.employee_code
                WHERE fe.status = 'ACTIVE' AND e.status = 'ACTIVE'
                ORDER BY fe.quality_score DESC
            """
            
            stored_embeddings = db_manager.execute_query(query, fetch=True)
            
            if not stored_embeddings:
                return {
                    'success': False,
                    'error': 'No face templates found in database'
                }
            
            # Group embeddings by employee
            employee_embeddings = {}
            for stored in stored_embeddings:
                emp_code = stored['employee_id']  # This is now employee_code
                if emp_code not in employee_embeddings:
                    employee_embeddings[emp_code] = {
                        'employee_info': stored,
                        'embeddings': []
                    }
                employee_embeddings[emp_code]['embeddings'].append(stored)
            
            best_match = None
            best_distance = float('inf')
            best_employee_id = None
            
            # Compare with each employee's templates
            for emp_code, emp_data in employee_embeddings.items():
                employee_distances = []
                
                for stored in emp_data['embeddings']:
                    # Ensure stored_vector is a numpy array
                    if isinstance(stored['vector'], str):
                        # If it's a string, try to parse it
                        try:
                            import ast
                            vector_list = ast.literal_eval(stored['vector'])
                            stored_vector = np.array(vector_list, dtype=np.float64)
                        except:
                            logger.error(f"Could not parse vector string: {stored['vector'][:100]}...")
                            continue
                    elif isinstance(stored['vector'], list):
                        stored_vector = np.array(stored['vector'], dtype=np.float64)
                    else:
                        stored_vector = np.array(stored['vector'], dtype=np.float64)
                    
                    # Ensure both vectors have the same shape
                    if input_embedding.shape != stored_vector.shape:
                        logger.error(f"Vector shape mismatch: input {input_embedding.shape} vs stored {stored_vector.shape}")
                        continue
                    
                    # Calculate distance
                    if self.distance_metric == 'l2':
                        distance = np.linalg.norm(input_embedding - stored_vector)
                    else:  # cosine distance
                        dot_product = np.dot(input_embedding, stored_vector)
                        norms = np.linalg.norm(input_embedding) * np.linalg.norm(stored_vector)
                        distance = 1 - (dot_product / norms) if norms != 0 else 1
                    
                    employee_distances.append(distance)
                
                # Use the best (minimum) distance for this employee
                min_distance = min(employee_distances)
                
                if min_distance < best_distance:
                    best_distance = min_distance
                    best_match = emp_data['employee_info']
                    best_employee_id = emp_code
            
            # Check if best match is within tolerance
            if best_match and best_distance <= self.tolerance:
                # Calculate confidence based on distance and quality
                confidence = max(0.0, 1 - (best_distance / self.tolerance))
                
                # Boost confidence if input image has good quality
                if quality_score > 0.7:
                    confidence = min(1.0, confidence * 1.1)
                
                return {
                    'success': True,
                    'employee_id': best_match['employee_id'],  # This is now employee_code
                    'employee_code': best_match['employee_code'],
                    'full_name': best_match['full_name'],
                    'department': best_match['department'],
                    'position': best_match['position'],
                    'confidence': round(confidence, 3),
                    'distance': round(best_distance, 4),
                    'quality_score': round(quality_score, 3),
                    'templates_compared': len(stored_embeddings)
                }
            else:
                return {
                    'success': False,
                    'error': 'No matching face found',
                    'best_distance': round(best_distance, 4) if best_match else None,
                    'quality_score': round(quality_score, 3),
                    'tolerance': self.tolerance,
                    'templates_compared': len(stored_embeddings)
                }
                
        except Exception as e:
            logger.error(f"Error recognizing face: {e}")
            return {
                'success': False,
                'error': f'Recognition error: {str(e)}'
            }
    def get_face_embeddings(self, employee_code: str = None) -> List[Dict[str, Any]]:
        """Get face embeddings, optionally filtered by employee_code"""
        try:
            if employee_code:
                query = """
                    SELECT fe.*, e.employee_code, e.full_name
                    FROM face_embeddings fe
                    JOIN employees e ON fe.employee_id = e.employee_code
                    WHERE fe.employee_id = %s AND fe.status = 'ACTIVE'
                    ORDER BY fe.created_at DESC
                """
                params = (employee_code,)
            else:
                query = """
                    SELECT fe.*, e.employee_code, e.full_name
                    FROM face_embeddings fe
                    JOIN employees e ON fe.employee_id = e.employee_code
                    WHERE fe.status = 'ACTIVE'
                    ORDER BY fe.created_at DESC
                """
                params = None
            
            results = db_manager.execute_query(query, params, fetch=True)
            return [dict(row) for row in results]
            
        except Exception as e:
            logger.error(f"Error getting face embeddings: {e}")
            return []
    
    def update_face_embedding(self, face_id: int, **kwargs) -> Dict[str, Any]:
        """Update face embedding"""
        try:
            # Build dynamic update query
            allowed_fields = ['quality_score', 'liveness_score', 'status', 'created_by']
            update_fields = []
            params = []
            
            for field, value in kwargs.items():
                if field in allowed_fields:
                    update_fields.append(f"{field} = %s")
                    params.append(value)
            
            if not update_fields:
                return {'success': False, 'error': 'No valid fields to update'}
            
            params.append(face_id)
            query = f"""
                UPDATE face_embeddings 
                SET {', '.join(update_fields)}
                WHERE id = %s AND status != 'DELETED'
                RETURNING id
            """
            
            result = db_manager.execute_one(query, params)
            
            if result:
                return {'success': True, 'face_embedding_id': result['id']}
            else:
                return {'success': False, 'error': 'Face embedding not found'}
                
        except Exception as e:
            logger.error(f"Error updating face embedding: {e}")
            return {'success': False, 'error': f'Update error: {str(e)}'}
    
    def delete_face_embedding(self, face_id: int, hard_delete: bool = False) -> Dict[str, Any]:
        """Delete face embedding (soft delete by default)"""
        try:
            # First, get the face embedding info to get image URL
            get_query = """
                SELECT id, image_url FROM face_embeddings 
                WHERE id = %s AND status != 'DELETED'
            """
            
            face_info = db_manager.execute_one(get_query, (face_id,))
            
            if not face_info:
                return {'success': False, 'error': 'Face embedding not found'}
            
            image_url = face_info.get('image_url')
            
            if hard_delete:
                # Hard delete from database
                delete_query = """
                    DELETE FROM face_embeddings 
                    WHERE id = %s
                    RETURNING id
                """
            else:
                # Soft delete
                delete_query = """
                    UPDATE face_embeddings 
                    SET status = 'DELETED'
                    WHERE id = %s AND status != 'DELETED'
                    RETURNING id
                """
            
            result = db_manager.execute_one(delete_query, (face_id,))
            
            if result:
                # Try to delete image from MinIO if it exists
                if image_url and minio_service:
                    try:
                        # Extract object name from URL
                        object_name = self._extract_object_name_from_url(image_url)
                        if object_name:
                            success = minio_service.delete_image(object_name)
                            if success:
                                logger.info(f"Image deleted from MinIO: {object_name}")
                            else:
                                logger.warning(f"Failed to delete image from MinIO: {object_name}")
                    except Exception as e:
                        logger.warning(f"Error deleting image from MinIO: {e}")
                
                delete_type = "hard deleted" if hard_delete else "deleted"
                return {'success': True, 'message': f'Face embedding {delete_type} successfully'}
            else:
                return {'success': False, 'error': 'Face embedding not found'}
                
        except Exception as e:
            logger.error(f"Error deleting face embedding: {e}")
            return {'success': False, 'error': f'Delete error: {str(e)}'}
    
    def _extract_object_name_from_url(self, url: str) -> Optional[str]:
        """Extract object name from MinIO URL"""
        try:
            # URL format: http://endpoint/bucket/object_name?params
            if f"/{Config.MINIO_BUCKET_NAME}/" in url:
                parts = url.split(f"/{Config.MINIO_BUCKET_NAME}/", 1)
                if len(parts) == 2:
                    object_name = parts[1].split('?')[0]  # Remove query parameters
                    return object_name
            return None
        except Exception as e:
            logger.error(f"Error extracting object name from URL: {e}")
            return None

# Global face service instance
face_service = FaceService() 