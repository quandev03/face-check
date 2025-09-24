#!/usr/bin/env python3

# Additional improvements for face recognition accuracy

# 1. Update face_service.py with better recognition logic
with open('face_service.py', 'r') as f:
    content = f.read()

# Add multiple template matching
improved_recognize = '''
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
                JOIN employees e ON fe.employee_id = e.id
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
                emp_id = stored['employee_id']
                if emp_id not in employee_embeddings:
                    employee_embeddings[emp_id] = {
                        'employee_info': stored,
                        'embeddings': []
                    }
                employee_embeddings[emp_id]['embeddings'].append(stored)
            
            best_match = None
            best_distance = float('inf')
            best_employee_id = None
            
            # Compare with each employee's templates
            for emp_id, emp_data in employee_embeddings.items():
                employee_distances = []
                
                for stored in emp_data['embeddings']:
                    stored_vector = np.array(stored['vector'])
                    
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
                    best_employee_id = emp_id
            
            # Check if best match is within tolerance
            if best_match and best_distance <= self.tolerance:
                # Calculate confidence based on distance and quality
                confidence = max(0.0, 1 - (best_distance / self.tolerance))
                
                # Boost confidence if input image has good quality
                if quality_score > 0.7:
                    confidence = min(1.0, confidence * 1.1)
                
                return {
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
'''

# Replace the old recognize_face method
old_method_start = "    def recognize_face(self, image_data: bytes) -> Dict[str, Any]:"
old_method_end = "                'error': f'Recognition error: {str(e)}'"

# Find and replace the method
start_idx = content.find(old_method_start)
if start_idx != -1:
    # Find the end of the method (next method or end of class)
    end_idx = content.find("    def ", start_idx + 1)
    if end_idx == -1:
        end_idx = len(content)
    
    # Replace the method
    new_content = content[:start_idx] + improved_recognize + content[end_idx:]
    
    with open('face_service.py', 'w') as f:
        f.write(new_content)
    
    print("✅ Updated recognize_face method with improved accuracy")
else:
    print("❌ Could not find recognize_face method to replace")

# 2. Add environment variable for tolerance
with open('config.env.example', 'r') as f:
    env_content = f.read()

# Add tolerance setting
if 'FACE_RECOGNITION_TOLERANCE' not in env_content:
    env_content += "\n# Face Recognition Accuracy\nFACE_RECOGNITION_TOLERANCE=0.4\n"
    
    with open('config.env.example', 'w') as f:
        f.write(env_content)
    
    print("✅ Added FACE_RECOGNITION_TOLERANCE to config.env.example")

print("✅ Additional accuracy improvements completed!")
