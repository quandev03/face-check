#!/usr/bin/env python3

# Fix vector conversion in face_service.py

with open('face_service.py', 'r') as f:
    content = f.read()

# Fix the vector conversion in recognize_face method
old_vector_conversion = '''                for stored in emp_data['embeddings']:
                    stored_vector = np.array(stored['vector'])
                    
                    # Calculate distance
                    if self.distance_metric == 'l2':
                        distance = np.linalg.norm(input_embedding - stored_vector)
                    else:  # cosine distance
                        dot_product = np.dot(input_embedding, stored_vector)
                        norms = np.linalg.norm(input_embedding) * np.linalg.norm(stored_vector)
                        distance = 1 - (dot_product / norms) if norms != 0 else 1'''

new_vector_conversion = '''                for stored in emp_data['embeddings']:
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
                        distance = 1 - (dot_product / norms) if norms != 0 else 1'''

content = content.replace(old_vector_conversion, new_vector_conversion)

with open('face_service.py', 'w') as f:
    f.write(content)

print("✅ Fixed vector conversion in face_service.py")
