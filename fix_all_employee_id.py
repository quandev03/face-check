#!/usr/bin/env python3

# Fix all remaining employee_id references

# 1. Fix app.py
with open('app.py', 'r') as f:
    content = f.read()

# Fix get_face_embeddings endpoint
old_get_embeddings = '''@app.route('/api/face/embeddings', methods=['GET'])
def get_face_embeddings():
    """Get face embeddings, optionally filtered by employee_code"""
    try:
        employee_code = request.args.get('employee_code')
        embeddings = face_service.get_face_embeddings(employee_code)
        
        return jsonify({
            'success': True,
            'data': embeddings,
            'count': len(embeddings)
        })
    except Exception as e:
        logger.error(f"Error getting face embeddings: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500'''

# This should already be correct, but let's make sure
content = content.replace(
    "employee_id = request.args.get('employee_id', type=int)",
    "employee_code = request.args.get('employee_code')"
)
content = content.replace(
    "embeddings = face_service.get_face_embeddings(employee_id)",
    "embeddings = face_service.get_face_embeddings(employee_code)"
)

# Fix get_employee_images endpoint
content = content.replace(
    "@app.route('/api/employees/<int:employee_id>/images', methods=['GET'])",
    "@app.route('/api/employees/<string:employee_code>/images', methods=['GET'])"
)
content = content.replace(
    "def get_employee_images(employee_id):",
    "def get_employee_images(employee_code):"
)
content = content.replace(
    "images = minio_service.list_employee_images(employee_id)",
    "images = minio_service.list_employee_images(employee_code)"
)

with open('app.py', 'w') as f:
    f.write(content)

print("✅ Fixed app.py")

# 2. Fix face_service.py
with open('face_service.py', 'r') as f:
    content = f.read()

# Fix minio_service call
content = content.replace(
    "image_data, employee_id, content_type",
    "image_data, employee_code, content_type"
)

# Fix insert query parameters
content = content.replace(
    "employee_id, embedding_list, self.model_name, self.model_version,",
    "employee_code, embedding_list, self.model_name, self.model_version,"
)

# Fix get_face_embeddings method signature
content = content.replace(
    "def get_face_embeddings(self, employee_code: str = None) -> List[Dict[str, Any]]:",
    "def get_face_embeddings(self, employee_code: str = None) -> List[Dict[str, Any]]:"
)

# Fix the query in get_face_embeddings
content = content.replace(
    "JOIN employees e ON fe.employee_id = e.id",
    "JOIN employees e ON fe.employee_id = e.employee_code"
)

with open('face_service.py', 'w') as f:
    f.write(content)

print("✅ Fixed face_service.py")

# 3. Fix minio_service.py
with open('minio_service.py', 'r') as f:
    content = f.read()

# Fix method signatures
content = content.replace(
    "def generate_object_name(self, employee_id: int, file_extension: str = \"jpg\") -> str:",
    "def generate_object_name(self, employee_code: str, file_extension: str = \"jpg\") -> str:"
)
content = content.replace(
    "def upload_image(self, image_data: bytes, employee_id: int,",
    "def upload_image(self, image_data: bytes, employee_code: str,"
)
content = content.replace(
    "def list_employee_images(self, employee_id: int) -> list:",
    "def list_employee_images(self, employee_code: str) -> list:"
)

# Fix method implementations
content = content.replace(
    "return f\"employees/{employee_id}/faces/{timestamp}_{unique_id}.{file_extension}\"",
    "return f\"employees/{employee_code}/faces/{timestamp}_{unique_id}.{file_extension}\""
)
content = content.replace(
    "object_name = self.generate_object_name(employee_id, file_extension)",
    "object_name = self.generate_object_name(employee_code, file_extension)"
)
content = content.replace(
    "'employee_id': str(employee_id),",
    "'employee_code': str(employee_code),"
)
content = content.replace(
    "prefix = f\"employees/{employee_id}/faces/\"",
    "prefix = f\"employees/{employee_code}/faces/\""
)
content = content.replace(
    "logger.error(f\"Error listing images for employee {employee_id}: {e}\")",
    "logger.error(f\"Error listing images for employee {employee_code}: {e}\")"
)

# Fix the employee_id extraction in cleanup
content = content.replace(
    "employee_id = int(parts[1])",
    "employee_code = parts[1]"
)
content = content.replace(
    "employees.add(employee_id)",
    "employees.add(employee_code)"
)

with open('minio_service.py', 'w') as f:
    f.write(content)

print("✅ Fixed minio_service.py")

print("✅ All employee_id references fixed!")
