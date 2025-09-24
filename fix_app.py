#!/usr/bin/env python3

# Fix app.py to use employee_code instead of employee_id

with open('app.py', 'r') as f:
    content = f.read()

# Fix the face_service call in enroll_face
old_call = '''        # Save face embedding
        result = face_service.save_face_embedding(
            employee_id=validated_data['employee_id'],
            image_data=image_data,
            created_by=validated_data.get('created_by'),
            source=validated_data.get('source', 'ENROLL'),
            content_type=file.content_type or 'image/jpeg'
        )'''

new_call = '''        # Save face embedding
        result = face_service.save_face_embedding(
            employee_code=validated_data['employee_code'],
            image_data=image_data,
            created_by=validated_data.get('created_by'),
            source=validated_data.get('source', 'ENROLL'),
            content_type=file.content_type or 'image/jpeg'
        )'''

content = content.replace(old_call, new_call)

# Fix the response in enroll_face
old_response = '''        if result['success']:
            return jsonify({
                'success': True,
                'message': 'Face enrolled successfully',
                'data': {
                    'face_embedding_id': result['face_embedding_id'],
                    'quality_score': result['quality_score'],
                    'bbox': result['bbox'],
                    'image_url': result.get('image_url'),
                    'minio_object_name': result.get('minio_object_name')
                }
            }), 201'''

new_response = '''        if result['success']:
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
            }), 201'''

content = content.replace(old_response, new_response)

with open('app.py', 'w') as f:
    f.write(content)

print("✅ Fixed app.py to use employee_code instead of employee_id")
