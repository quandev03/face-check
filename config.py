import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Flask Configuration
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    FLASK_ENV = os.environ.get('FLASK_ENV') or 'development'
    FLASK_DEBUG = os.environ.get('FLASK_DEBUG', 'True').lower() in ['true', '1', 'yes']
    
    # Database Configuration
    DATABASE_URL = os.environ.get('DATABASE_URL') or 'postgresql://postgres:postgres@160.191.245.38:5433/face_attendance'
    
    # File Upload Configuration
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER') or 'uploads'
    MAX_CONTENT_LENGTH = int(os.environ.get('MAX_CONTENT_LENGTH') or 16 * 1024 * 1024)  # 16MB
    
    # Face Recognition Configuration
    FACE_RECOGNITION_TOLERANCE = float(os.environ.get('FACE_RECOGNITION_TOLERANCE') or 0.4)
    FACE_MODEL_NAME = os.environ.get('FACE_MODEL_NAME') or 'face_recognition'
    FACE_MODEL_VERSION = os.environ.get('FACE_MODEL_VERSION') or '1.0'
    DISTANCE_METRIC = os.environ.get('DISTANCE_METRIC') or 'l2'
    EMBEDDING_DIMENSION = 128
    
    # Server Configuration
    HOST = os.environ.get('HOST') or '0.0.0.0'
    PORT = int(os.environ.get('PORT') or 5555)
    
    # Logging Configuration
    LOG_LEVEL = os.environ.get('LOG_LEVEL') or 'INFO'
    
    # Security Configuration
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', '').split(',') if os.environ.get('CORS_ORIGINS') else None
    
    # Database Performance Tuning
    DB_POOL_MIN_CONN = int(os.environ.get('DB_POOL_MIN_CONN') or 1)
    DB_POOL_MAX_CONN = int(os.environ.get('DB_POOL_MAX_CONN') or 20)
    
    # MinIO Configuration
    MINIO_ENDPOINT = os.environ.get('MINIO_ENDPOINT') or '160.191.245.38:9000'
    MINIO_ACCESS_KEY = os.environ.get('MINIO_ACCESS_KEY') or 'admin'
    MINIO_SECRET_KEY = os.environ.get('MINIO_SECRET_KEY') or 'Ngoquan@2003'
    MINIO_BUCKET_NAME = os.environ.get('MINIO_BUCKET_NAME') or 'face-images'
    MINIO_SECURE = os.environ.get('MINIO_SECURE', 'False').lower() in ['true', '1', 'yes']
    MINIO_REGION = os.environ.get('MINIO_REGION') or 'us-east-1'
    
    # Image Storage Configuration
    STORE_ORIGINAL_IMAGES = os.environ.get('STORE_ORIGINAL_IMAGES', 'True').lower() in ['true', '1', 'yes']
    IMAGE_RETENTION_DAYS = int(os.environ.get('IMAGE_RETENTION_DAYS') or 365)
    
    # Additional Configuration
    AUTO_INIT_DB = os.environ.get('AUTO_INIT_DB', 'True').lower() in ['true', '1', 'yes']
    TIMEZONE = os.environ.get('TIMEZONE') or 'UTC'
    IMAGE_QUALITY = int(os.environ.get('IMAGE_QUALITY') or 85)
    MAX_FACES_PER_IMAGE = int(os.environ.get('MAX_FACES_PER_IMAGE') or 1) 