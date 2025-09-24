import io
import hashlib
import logging
from datetime import datetime, timedelta
from typing import Optional, Tuple, Dict, Any
from minio import Minio
from minio.error import S3Error
from PIL import Image
import uuid

from config import Config

logger = logging.getLogger(__name__)

class MinIOService:
    def __init__(self):
        """Initialize MinIO client"""
        try:
            self.client = Minio(
                Config.MINIO_ENDPOINT,
                access_key=Config.MINIO_ACCESS_KEY,
                secret_key=Config.MINIO_SECRET_KEY,
                secure=Config.MINIO_SECURE,
                region=Config.MINIO_REGION
            )
            self.bucket_name = Config.MINIO_BUCKET_NAME
            self._ensure_bucket_exists()
            logger.info(f"MinIO client initialized successfully. Bucket: {self.bucket_name}")
        except Exception as e:
            logger.error(f"Failed to initialize MinIO client: {e}")
            raise
    
    def _ensure_bucket_exists(self):
        """Ensure the bucket exists, create if it doesn't"""
        try:
            if not self.client.bucket_exists(self.bucket_name):
                self.client.make_bucket(self.bucket_name, location=Config.MINIO_REGION)
                logger.info(f"Created bucket: {self.bucket_name}")
                
                # Set bucket policy for public read (optional)
                # self._set_bucket_policy()
        except S3Error as e:
            logger.error(f"Error ensuring bucket exists: {e}")
            raise
    
    def _set_bucket_policy(self):
        """Set bucket policy for public read access (optional)"""
        policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Principal": {"AWS": "*"},
                    "Action": ["s3:GetObject"],
                    "Resource": [f"arn:aws:s3:::{self.bucket_name}/*"]
                }
            ]
        }
        
        try:
            import json
            self.client.set_bucket_policy(self.bucket_name, json.dumps(policy))
            logger.info(f"Set public read policy for bucket: {self.bucket_name}")
        except S3Error as e:
            logger.warning(f"Could not set bucket policy: {e}")
    
    def generate_object_name(self, employee_code: str, file_extension: str = "jpg") -> str:
        """Generate unique object name for storing image"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_id = str(uuid.uuid4())[:8]
        return f"employees/{employee_code}/faces/{timestamp}_{unique_id}.{file_extension}"
    
    def upload_image(self, image_data: bytes, employee_code: str, 
                    content_type: str = "image/jpeg") -> Tuple[bool, str, Optional[str]]:
        """
        Upload image to MinIO
        Returns: (success, object_name, url)
        """
        if not Config.STORE_ORIGINAL_IMAGES:
            return True, "", None
        
        try:
            # Generate object name
            file_extension = content_type.split('/')[-1] if '/' in content_type else 'jpg'
            object_name = self.generate_object_name(employee_code, file_extension)
            
            # Create image stream
            image_stream = io.BytesIO(image_data)
            image_size = len(image_data)
            
            # Upload to MinIO
            result = self.client.put_object(
                bucket_name=self.bucket_name,
                object_name=object_name,
                data=image_stream,
                length=image_size,
                content_type=content_type,
                metadata={
                    'employee_code': str(employee_code),
                    'upload_timestamp': datetime.now().isoformat(),
                    'content_type': content_type
                }
            )
            
            # Generate URL
            image_url = self.get_object_url(object_name)
            
            logger.info(f"Image uploaded successfully: {object_name}")
            return True, object_name, image_url
            
        except S3Error as e:
            logger.error(f"MinIO error uploading image: {e}")
            return False, "", None
        except Exception as e:
            logger.error(f"Error uploading image: {e}")
            return False, "", None
    
    def get_object_url(self, object_name: str, expires: timedelta = timedelta(hours=24)) -> str:
        """Get presigned URL for object"""
        try:
            url = self.client.presigned_get_object(
                bucket_name=self.bucket_name,
                object_name=object_name,
                expires=expires
            )
            return url
        except S3Error as e:
            logger.error(f"Error generating presigned URL: {e}")
            return ""
    
    def get_public_url(self, object_name: str) -> str:
        """Get public URL for object (if bucket has public read policy)"""
        protocol = "https" if Config.MINIO_SECURE else "http"
        return f"{protocol}://{Config.MINIO_ENDPOINT}/{self.bucket_name}/{object_name}"
    
    def download_image(self, object_name: str) -> Optional[bytes]:
        """Download image from MinIO"""
        try:
            response = self.client.get_object(self.bucket_name, object_name)
            image_data = response.read()
            response.close()
            response.release_conn()
            return image_data
        except S3Error as e:
            logger.error(f"Error downloading image {object_name}: {e}")
            return None
        except Exception as e:
            logger.error(f"Error downloading image {object_name}: {e}")
            return None
    
    def delete_image(self, object_name: str) -> bool:
        """Delete image from MinIO"""
        try:
            self.client.remove_object(self.bucket_name, object_name)
            logger.info(f"Image deleted successfully: {object_name}")
            return True
        except S3Error as e:
            logger.error(f"Error deleting image {object_name}: {e}")
            return False
        except Exception as e:
            logger.error(f"Error deleting image {object_name}: {e}")
            return False
    
    def list_employee_images(self, employee_code: str) -> list:
        """List all images for an employee"""
        try:
            prefix = f"employees/{employee_code}/faces/"
            objects = self.client.list_objects(
                bucket_name=self.bucket_name,
                prefix=prefix,
                recursive=True
            )
            
            image_list = []
            for obj in objects:
                image_info = {
                    'object_name': obj.object_name,
                    'size': obj.size,
                    'last_modified': obj.last_modified,
                    'url': self.get_object_url(obj.object_name)
                }
                image_list.append(image_info)
            
            return image_list
        except S3Error as e:
            logger.error(f"Error listing images for employee {employee_code}: {e}")
            return []
    
    def cleanup_old_images(self, days: int = None) -> int:
        """Clean up images older than specified days"""
        if days is None:
            days = Config.IMAGE_RETENTION_DAYS
        
        if days <= 0:
            return 0
        
        try:
            cutoff_date = datetime.now() - timedelta(days=days)
            objects = self.client.list_objects(
                bucket_name=self.bucket_name,
                recursive=True
            )
            
            deleted_count = 0
            for obj in objects:
                if obj.last_modified < cutoff_date:
                    if self.delete_image(obj.object_name):
                        deleted_count += 1
            
            logger.info(f"Cleaned up {deleted_count} old images (older than {days} days)")
            return deleted_count
            
        except S3Error as e:
            logger.error(f"Error during cleanup: {e}")
            return 0
    
    def get_storage_stats(self) -> Dict[str, Any]:
        """Get storage statistics"""
        try:
            objects = self.client.list_objects(
                bucket_name=self.bucket_name,
                recursive=True
            )
            
            total_objects = 0
            total_size = 0
            employees = set()
            
            for obj in objects:
                total_objects += 1
                total_size += obj.size
                
                # Extract employee ID from object name
                parts = obj.object_name.split('/')
                if len(parts) >= 2 and parts[0] == 'employees':
                    try:
                        employee_code = parts[1]
                        employees.add(employee_code)
                    except ValueError:
                        pass
            
            return {
                'total_objects': total_objects,
                'total_size_bytes': total_size,
                'total_size_mb': round(total_size / (1024 * 1024), 2),
                'unique_employees': len(employees),
                'bucket_name': self.bucket_name
            }
            
        except S3Error as e:
            logger.error(f"Error getting storage stats: {e}")
            return {}
    
    def health_check(self) -> Dict[str, Any]:
        """Check MinIO service health"""
        try:
            # Try to list objects to test connection
            list(self.client.list_objects(self.bucket_name, max_keys=1))
            
            return {
                'status': 'healthy',
                'endpoint': Config.MINIO_ENDPOINT,
                'bucket': self.bucket_name,
                'secure': Config.MINIO_SECURE
            }
        except Exception as e:
            return {
                'status': 'unhealthy',
                'error': str(e),
                'endpoint': Config.MINIO_ENDPOINT,
                'bucket': self.bucket_name
            }

# Global MinIO service instance
try:
    minio_service = MinIOService()
except Exception as e:
    logger.error(f"Failed to initialize MinIO service: {e}")
    minio_service = None 