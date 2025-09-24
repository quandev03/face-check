from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import logging
from werkzeug.utils import secure_filename
from marshmallow import ValidationError
import traceback

from config import Config
from database import init_database, db_manager
from face_service import face_service
from minio_service import minio_service
from schemas import (
    FaceEnrollRequestSchema,
    FaceUpdateRequestSchema, 
    FaceEmbeddingSchema,
    RecognitionResponseSchema,
    ApiResponseSchema
)

# Setup logging
log_level = getattr(logging, Config.LOG_LEVEL.upper(), logging.INFO)
logging.basicConfig(
    level=log_level,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__)
app.config.from_object(Config)

# Enable CORS
if Config.CORS_ORIGINS:
    CORS(app, origins=Config.CORS_ORIGINS)
else:
    CORS(app)

# Create upload directory
os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)

# Schema instances
face_enroll_schema = FaceEnrollRequestSchema()
face_update_schema = FaceUpdateRequestSchema()
face_embedding_schema = FaceEmbeddingSchema()
recognition_response_schema = RecognitionResponseSchema()
api_response_schema = ApiResponseSchema()

def allowed_file(filename):
    """Check if file extension is allowed"""
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def handle_error(error_msg, status_code=400):
    """Handle error responses"""
    return jsonify({
        'success': False,
        'error': error_msg
    }), status_code

@app.errorhandler(ValidationError)
def handle_validation_error(error):
    """Handle marshmallow validation errors"""
    return jsonify({
        'success': False,
        'error': 'Validation error',
        'details': error.messages
    }), 400

@app.errorhandler(Exception)
def handle_unexpected_error(error):
    """Handle unexpected errors"""
    logger.error(f"Unexpected error: {str(error)}")
    logger.error(traceback.format_exc())
    return jsonify({
        'success': False,
        'error': 'Internal server error'
    }), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'success': True,
        'message': 'Face Recognition Service is running',
        'version': '1.0.0'
    })

@app.route('/api/face/enroll', methods=['POST'])
def enroll_face():
    """
    API thêm mẫu khuôn mặt
    Expects: multipart/form-data with 'image' file and form fields
    """
    try:
        # Check if image file is present
        if 'image' not in request.files:
            return handle_error('No image file provided')
        
        file = request.files['image']
        if file.filename == '':
            return handle_error('No image file selected')
        
        if not allowed_file(file.filename):
            return handle_error('Invalid file type. Allowed: png, jpg, jpeg, gif, bmp')
        
        # Validate form data
        form_data = request.form.to_dict()
        try:
            validated_data = face_enroll_schema.load(form_data)
        except ValidationError as err:
            return handle_error(f'Validation error: {err.messages}')
        
        # Read image data
        image_data = file.read()
        if len(image_data) == 0:
            return handle_error('Empty image file')
        
        # Save face embedding
        result = face_service.save_face_embedding(
            employee_code=validated_data['employee_code'],
            image_data=image_data,
            created_by=validated_data.get('created_by'),
            source=validated_data.get('source', 'ENROLL'),
            content_type=file.content_type or 'image/jpeg'
        )
        
        if result['success']:
            return jsonify({
                'success': True,
                'message': 'Face enrolled successfully',
                'data': {
                    'face_embedding_id': result['face_embedding_id'],
                    'employee_code': validated_data['employee_code'],
                    'quality_score': result['quality_score'],
                    'bbox': result['bbox'],
                    'image_url': result.get('image_url'),
                    'minio_object_name': result.get('minio_object_name')
                }
            }), 201
        else:
            return handle_error(result['error'])
            
    except Exception as e:
        logger.error(f"Error in enroll_face: {str(e)}")
        return handle_error('Failed to enroll face', 500)

@app.route('/api/face/recognize', methods=['POST'])
def recognize_face():
    """
    API nhận diện khuôn mặt và trả ra mã nhân viên
    Expects: multipart/form-data with 'image' file
    """
    try:
        # Check if image file is present
        if 'image' not in request.files:
            return handle_error('No image file provided')
        
        file = request.files['image']
        if file.filename == '':
            return handle_error('No image file selected')
        
        if not allowed_file(file.filename):
            return handle_error('Invalid file type. Allowed: png, jpg, jpeg, gif, bmp')
        
        # Read image data
        image_data = file.read()
        if len(image_data) == 0:
            return handle_error('Empty image file')
        
        # Recognize face
        result = face_service.recognize_face(image_data)
        
        # Return result using schema
        return jsonify(recognition_response_schema.dump(result))
        
    except Exception as e:
        logger.error(f"Error in recognize_face: {str(e)}")
        return handle_error('Failed to recognize face', 500)

@app.route('/api/face/embeddings', methods=['GET'])
def get_face_embeddings():
    """
    API lấy danh sách face embeddings
    Query params: employee_code (optional)
    """
    try:
        employee_code = request.args.get('employee_code')
        
        embeddings = face_service.get_face_embeddings(employee_code)
        
        return jsonify({
            'success': True,
            'data': face_embedding_schema.dump(embeddings, many=True),
            'count': len(embeddings)
        })
        
    except Exception as e:
        logger.error(f"Error in get_face_embeddings: {str(e)}")
        return handle_error('Failed to get face embeddings', 500)

@app.route('/api/face/embeddings/<int:face_id>', methods=['GET'])
def get_face_embedding(face_id):
    """
    API lấy thông tin một face embedding
    """
    try:
        embeddings = face_service.get_face_embeddings()
        embedding = next((e for e in embeddings if e['id'] == face_id), None)
        
        if embedding:
            return jsonify({
                'success': True,
                'data': face_embedding_schema.dump(embedding)
            })
        else:
            return handle_error('Face embedding not found', 404)
            
    except Exception as e:
        logger.error(f"Error in get_face_embedding: {str(e)}")
        return handle_error('Failed to get face embedding', 500)

@app.route('/api/face/embeddings/<int:face_id>', methods=['PUT'])
def update_face_embedding(face_id):
    """
    API sửa face embedding
    """
    try:
        # Validate request data
        try:
            validated_data = face_update_schema.load(request.json or {})
        except ValidationError as err:
            return handle_error(f'Validation error: {err.messages}')
        
        if not validated_data:
            return handle_error('No valid fields to update')
        
        # Update face embedding
        result = face_service.update_face_embedding(face_id, **validated_data)
        
        if result['success']:
            return jsonify({
                'success': True,
                'message': 'Face embedding updated successfully',
                'data': {'face_embedding_id': result['face_embedding_id']}
            })
        else:
            return handle_error(result['error'], 404 if 'not found' in result['error'] else 400)
            
    except Exception as e:
        logger.error(f"Error in update_face_embedding: {str(e)}")
        return handle_error('Failed to update face embedding', 500)



@app.route('/api/employees', methods=['POST'])
def create_employee():
    """
    API tạo nhân viên mới (helper endpoint)
    """
    try:
        data = request.json
        if not data:
            return handle_error('No data provided')
        
        # Basic validation
        required_fields = ['employee_code', 'full_name']
        for field in required_fields:
            if field not in data or not data[field]:
                return handle_error(f'Missing required field: {field}')
        
        # Insert employee
        query = """
            INSERT INTO employees (employee_code, full_name, email, department, position)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id, employee_code, full_name
        """
        
        result = db_manager.execute_one(query, (
            data['employee_code'],
            data['full_name'],
            data.get('email'),
            data.get('department'),
            data.get('position')
        ))
        
        return jsonify({
            'success': True,
            'message': 'Employee created successfully',
            'data': dict(result)
        }), 201
        
    except Exception as e:
        logger.error(f"Error in create_employee: {str(e)}")
        if 'duplicate key' in str(e).lower():
            return handle_error('Employee code already exists', 409)
        return handle_error('Failed to create employee', 500)

@app.route('/api/employees', methods=['GET'])
def get_employees():
    """
    API lấy danh sách nhân viên
    """
    try:
        query = """
            SELECT id, employee_code, full_name, email, department, position, status, created_at
            FROM employees
            WHERE status = 'ACTIVE'
            ORDER BY created_at DESC
        """
        
        employees = db_manager.execute_query(query, fetch=True)
        
        return jsonify({
            'success': True,
            'data': [dict(emp) for emp in employees],
            'count': len(employees)
        })
        
    except Exception as e:
        logger.error(f"Error in get_employees: {str(e)}")
        return handle_error('Failed to get employees', 500)

@app.route('/api/storage/stats', methods=['GET'])
def get_storage_stats():
    """
    API lấy thống kê storage
    """
    try:
        if not minio_service:
            return handle_error('MinIO service not available', 503)
        
        stats = minio_service.get_storage_stats()
        
        return jsonify({
            'success': True,
            'data': stats
        })
        
    except Exception as e:
        logger.error(f"Error in get_storage_stats: {str(e)}")
        return handle_error('Failed to get storage stats', 500)

@app.route('/api/storage/health', methods=['GET'])
def check_storage_health():
    """
    API kiểm tra tình trạng MinIO
    """
    try:
        if not minio_service:
            return jsonify({
                'success': False,
                'data': {
                    'status': 'unavailable',
                    'error': 'MinIO service not initialized'
                }
            })
        
        health = minio_service.health_check()
        
        return jsonify({
            'success': health['status'] == 'healthy',
            'data': health
        })
        
    except Exception as e:
        logger.error(f"Error in check_storage_health: {str(e)}")
        return handle_error('Failed to check storage health', 500)

@app.route('/api/storage/cleanup', methods=['POST'])
def cleanup_old_images():
    """
    API dọn dẹp ảnh cũ
    """
    try:
        if not minio_service:
            return handle_error('MinIO service not available', 503)
        
        data = request.json or {}
        days = data.get('days', Config.IMAGE_RETENTION_DAYS)
        
        if days <= 0:
            return handle_error('Days must be greater than 0')
        
        deleted_count = minio_service.cleanup_old_images(days)
        
        return jsonify({
            'success': True,
            'message': f'Cleaned up {deleted_count} old images',
            'data': {
                'deleted_count': deleted_count,
                'retention_days': days
            }
        })
        
    except Exception as e:
        logger.error(f"Error in cleanup_old_images: {str(e)}")
        return handle_error('Failed to cleanup old images', 500)

@app.route('/api/employees/<string:employee_code>/images', methods=['GET'])
def get_employee_images(employee_code):
    """
    API lấy danh sách ảnh của nhân viên
    """
    try:
        if not minio_service:
            return handle_error('MinIO service not available', 503)
        
        images = minio_service.list_employee_images(employee_code)
        
        return jsonify({
            'success': True,
            'data': images,
            'count': len(images)
        })
        
    except Exception as e:
        logger.error(f"Error in get_employee_images: {str(e)}")
        return handle_error('Failed to get employee images', 500)

@app.route('/api/face/embeddings/<int:face_id>', methods=['DELETE'])
def delete_face_embedding_with_options(face_id):
    """
    API xoá face embedding với options
    """
    try:
        data = request.json or {}
        hard_delete = data.get('hard_delete', False)
        
        result = face_service.delete_face_embedding(face_id, hard_delete=hard_delete)
        
        if result['success']:
            return jsonify({
                'success': True,
                'message': result['message']
            })
        else:
            return handle_error(result['error'], 404 if 'not found' in result['error'] else 400)
            
    except Exception as e:
        logger.error(f"Error in delete_face_embedding: {str(e)}")
        return handle_error('Failed to delete face embedding', 500)

# Database initialization moved to main block

if __name__ == '__main__':
    # Initialize database if auto init is enabled
    if Config.AUTO_INIT_DB:
        try:
            init_database()
            logger.info("Database initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            exit(1)
    
    # Run the application
    app.run(
        host=Config.HOST,
        port=Config.PORT,
        debug=Config.FLASK_DEBUG
    ) 