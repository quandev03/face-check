#!/usr/bin/env python3

# Update code to use employee_code (varchar) instead of employee_id (integer)

# 1. Update face_service.py
with open('face_service.py', 'r') as f:
    content = f.read()

# Replace employee_id with employee_code in save_face_embedding method
old_save_method = '''    def save_face_embedding(self, employee_id: int, image_data: bytes, 
                          created_by: str = None, source: str = 'ENROLL',
                          content_type: str = 'image/jpeg') -> Dict[str, Any]:'''
new_save_method = '''    def save_face_embedding(self, employee_code: str, image_data: bytes, 
                          created_by: str = None, source: str = 'ENROLL',
                          content_type: str = 'image/jpeg') -> Dict[str, Any]:'''

content = content.replace(old_save_method, new_save_method)

# Update the insert query in save_face_embedding
old_insert = '''            # Insert into database
            insert_query = """
                INSERT INTO face_embeddings 
                (employee_id, vector, model_name, model_version, distance_metric, 
                 quality_score, bbox, source, image_url, sha256, created_by)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id
            """
            
            result = db_manager.execute_one(insert_query, ('''
new_insert = '''            # Insert into database
            insert_query = """
                INSERT INTO face_embeddings 
                (employee_id, vector, model_name, model_version, distance_metric, 
                 quality_score, bbox, source, image_url, sha256, created_by)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id
            """
            
            result = db_manager.execute_one(insert_query, ('''

content = content.replace(old_insert, new_insert)

# Update the parameter in the insert
old_param = '''                employee_id, embedding_list, self.model_name, self.model_version, 
                self.distance_metric, quality_score, bbox_array, source, 
                image_url, image_hash, created_by'''
new_param = '''                employee_code, embedding_list, self.model_name, self.model_version, 
                self.distance_metric, quality_score, bbox_array, source, 
                image_url, image_hash, created_by'''

content = content.replace(old_param, new_param)

# Update get_face_embeddings method
old_get_method = '''    def get_face_embeddings(self, employee_id: int = None) -> List[Dict[str, Any]]:'''
new_get_method = '''    def get_face_embeddings(self, employee_code: str = None) -> List[Dict[str, Any]]:'''

content = content.replace(old_get_method, new_get_method)

# Update the query in get_face_embeddings
old_query = '''            if employee_id:
                query = """
                    SELECT fe.*, e.employee_code, e.full_name
                    FROM face_embeddings fe
                    JOIN employees e ON fe.employee_id = e.id
                    WHERE fe.employee_id = %s AND fe.status = 'ACTIVE'
                    ORDER BY fe.created_at DESC
                """
                params = (employee_id,)'''
new_query = '''            if employee_code:
                query = """
                    SELECT fe.*, e.employee_code, e.full_name
                    FROM face_embeddings fe
                    JOIN employees e ON fe.employee_id = e.employee_code
                    WHERE fe.employee_id = %s AND fe.status = 'ACTIVE'
                    ORDER BY fe.created_at DESC
                """
                params = (employee_code,)'''

content = content.replace(old_query, new_query)

# Update recognize_face method query
old_recognize_query = '''            # Get all stored embeddings with employee info
            query = """
                SELECT fe.id, fe.employee_id, fe.vector, fe.quality_score,
                       e.employee_code, e.full_name, e.department, e.position
                FROM face_embeddings fe
                JOIN employees e ON fe.employee_id = e.id
                WHERE fe.status = 'ACTIVE' AND e.status = 'ACTIVE'
                ORDER BY fe.quality_score DESC
            """'''
new_recognize_query = '''            # Get all stored embeddings with employee info
            query = """
                SELECT fe.id, fe.employee_id, fe.vector, fe.quality_score,
                       e.employee_code, e.full_name, e.department, e.position
                FROM face_embeddings fe
                JOIN employees e ON fe.employee_id = e.employee_code
                WHERE fe.status = 'ACTIVE' AND e.status = 'ACTIVE'
                ORDER BY fe.quality_score DESC
            """'''

content = content.replace(old_recognize_query, new_recognize_query)

# Update the employee grouping logic
old_grouping = '''            # Group embeddings by employee
            employee_embeddings = {}
            for stored in stored_embeddings:
                emp_id = stored['employee_id']
                if emp_id not in employee_embeddings:
                    employee_embeddings[emp_id] = {
                        'employee_info': stored,
                        'embeddings': []
                    }
                employee_embeddings[emp_id]['embeddings'].append(stored)'''
new_grouping = '''            # Group embeddings by employee
            employee_embeddings = {}
            for stored in stored_embeddings:
                emp_code = stored['employee_id']  # This is now employee_code
                if emp_code not in employee_embeddings:
                    employee_embeddings[emp_code] = {
                        'employee_info': stored,
                        'embeddings': []
                    }
                employee_embeddings[emp_code]['embeddings'].append(stored)'''

content = content.replace(old_grouping, new_grouping)

# Update the comparison loop
old_comparison = '''            # Compare with each employee's templates
            for emp_id, emp_data in employee_embeddings.items():'''
new_comparison = '''            # Compare with each employee's templates
            for emp_code, emp_data in employee_embeddings.items():'''

content = content.replace(old_comparison, new_comparison)

# Update the best match assignment
old_best_match = '''                if min_distance < best_distance:
                    best_distance = min_distance
                    best_match = emp_data['employee_info']
                    best_employee_id = emp_id'''
new_best_match = '''                if min_distance < best_distance:
                    best_distance = min_distance
                    best_match = emp_data['employee_info']
                    best_employee_id = emp_code'''

content = content.replace(old_best_match, new_best_match)

# Update the return statement
old_return = '''                return {
                    'success': True,
                    'employee_id': best_match['employee_id'],
                    'employee_code': best_match['employee_code'],
                    'full_name': best_match['full_name'],
                    'department': best_match['department'],
                    'position': best_match['position'],
                    'confidence': round(confidence, 3),
                    'distance': round(best_distance, 4),
                    'quality_score': round(quality_score, 3),
                    'templates_compared': len(stored_embeddings)
                }'''
new_return = '''                return {
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
                }'''

content = content.replace(old_return, new_return)

with open('face_service.py', 'w') as f:
    f.write(content)

print("✅ Updated face_service.py to use employee_code (varchar)")

# 2. Update app.py
with open('app.py', 'r') as f:
    app_content = f.read()

# Update enroll_face endpoint
old_enroll = '''@app.route('/api/face/enroll', methods=['POST'])
def enroll_face():
    """Enroll a new face template"""
    try:
        # Validate request
        if 'image' not in request.files:
            return jsonify({
                'success': False,
                'error': 'No image file provided'
            }), 400
        
        if 'employee_id' not in request.form:
            return jsonify({
                'success': False,
                'error': 'employee_id is required'
            }), 400'''
new_enroll = '''@app.route('/api/face/enroll', methods=['POST'])
def enroll_face():
    """Enroll a new face template"""
    try:
        # Validate request
        if 'image' not in request.files:
            return jsonify({
                'success': False,
                'error': 'No image file provided'
            }), 400
        
        if 'employee_code' not in request.form:
            return jsonify({
                'success': False,
                'error': 'employee_code is required'
            }), 400'''

app_content = app_content.replace(old_enroll, new_enroll)

# Update the employee_id extraction
old_extract = '''        employee_id = int(request.form['employee_id'])'''
new_extract = '''        employee_code = request.form['employee_code']'''

app_content = app_content.replace(old_extract, new_extract)

# Update the face_service call
old_call = '''        result = face_service.save_face_embedding(
            employee_id=employee_id,
            image_data=image_data,
            created_by=created_by,
            source=source,
            content_type=content_type
        )'''
new_call = '''        result = face_service.save_face_embedding(
            employee_code=employee_code,
            image_data=image_data,
            created_by=created_by,
            source=source,
            content_type=content_type
        )'''

app_content = app_content.replace(old_call, new_call)

# Update the response
old_response = '''        if result['success']:
            return jsonify({
                'success': True,
                'message': 'Face template enrolled successfully',
                'data': {
                    'face_id': result['face_id'],
                    'employee_id': employee_id,
                    'quality_score': result['quality_score'],
                    'image_url': result.get('image_url'),
                    'minio_object_name': result.get('minio_object_name')
                }
            }), 201'''
new_response = '''        if result['success']:
            return jsonify({
                'success': True,
                'message': 'Face template enrolled successfully',
                'data': {
                    'face_id': result['face_id'],
                    'employee_code': employee_code,
                    'quality_score': result['quality_score'],
                    'image_url': result.get('image_url'),
                    'minio_object_name': result.get('minio_object_name')
                }
            }), 201'''

app_content = app_content.replace(old_response, new_response)

# Update get_face_embeddings endpoint
old_get_endpoint = '''@app.route('/api/face/embeddings', methods=['GET'])
def get_face_embeddings():
    """Get face embeddings, optionally filtered by employee_id"""
    try:
        employee_id = request.args.get('employee_id', type=int)
        embeddings = face_service.get_face_embeddings(employee_id)
        
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
new_get_endpoint = '''@app.route('/api/face/embeddings', methods=['GET'])
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

app_content = app_content.replace(old_get_endpoint, new_get_endpoint)

with open('app.py', 'w') as f:
    f.write(app_content)

print("✅ Updated app.py to use employee_code (varchar)")

# 3. Update schemas.py
with open('schemas.py', 'r') as f:
    schema_content = f.read()

# Update FaceEmbeddingSchema
old_schema = '''class FaceEmbeddingSchema(Schema):
    id = fields.Int(dump_only=True)
    employee_id = fields.Int(required=True)
    vector = fields.List(fields.Float(), dump_only=True)
    model_name = fields.Str(dump_only=True)
    model_version = fields.Str(dump_only=True)
    distance_metric = fields.Str(dump_only=True)
    quality_score = fields.Float(dump_only=True)
    liveness_score = fields.Float(dump_only=True)
    bbox = fields.List(fields.Int(), dump_only=True)
    source = fields.Str(dump_only=True)
    image_url = fields.Str(dump_only=True)
    minio_object_name = fields.Str(dump_only=True)
    sha256 = fields.Str(dump_only=True)
    created_at = fields.DateTime(dump_only=True)
    created_by = fields.Str(dump_only=True)
    status = fields.Str(dump_only=True)'''
new_schema = '''class FaceEmbeddingSchema(Schema):
    id = fields.Int(dump_only=True)
    employee_id = fields.Str(required=True)  # Now varchar (employee_code)
    vector = fields.List(fields.Float(), dump_only=True)
    model_name = fields.Str(dump_only=True)
    model_version = fields.Str(dump_only=True)
    distance_metric = fields.Str(dump_only=True)
    quality_score = fields.Float(dump_only=True)
    liveness_score = fields.Float(dump_only=True)
    bbox = fields.List(fields.Int(), dump_only=True)
    source = fields.Str(dump_only=True)
    image_url = fields.Str(dump_only=True)
    minio_object_name = fields.Str(dump_only=True)
    sha256 = fields.Str(dump_only=True)
    created_at = fields.DateTime(dump_only=True)
    created_by = fields.Str(dump_only=True)
    status = fields.Str(dump_only=True)'''

schema_content = schema_content.replace(old_schema, new_schema)

with open('schemas.py', 'w') as f:
    f.write(schema_content)

print("✅ Updated schemas.py to use employee_code (varchar)")

print("✅ All code updated to use employee_code (varchar) instead of employee_id (integer)")
