#!/usr/bin/env python3

# Improve face recognition accuracy

# 1. Update config.py with better tolerance
with open('config.py', 'r') as f:
    content = f.read()

# Change tolerance from 0.6 to 0.4 (lower = more strict)
old_tolerance = "FACE_RECOGNITION_TOLERANCE = float(os.environ.get('FACE_RECOGNITION_TOLERANCE') or 0.6)"
new_tolerance = "FACE_RECOGNITION_TOLERANCE = float(os.environ.get('FACE_RECOGNITION_TOLERANCE') or 0.4)"

content = content.replace(old_tolerance, new_tolerance)

with open('config.py', 'w') as f:
    f.write(content)

print("✅ Updated tolerance from 0.6 to 0.4 (more strict)")

# 2. Create improved face_service.py with better recognition logic
with open('face_service.py', 'r') as f:
    face_content = f.read()

# Add better face detection and quality assessment
improved_recognition = '''
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
'''

# Replace the old method
old_method_start = "    def extract_face_embedding(self, image_data: bytes) -> Tuple[Optional[np.ndarray], Optional[Dict], float]:"
old_method_end = "            return None, None, 0.0"

# Find and replace the method
start_idx = face_content.find(old_method_start)
if start_idx != -1:
    # Find the end of the method (next method or end of class)
    end_idx = face_content.find("    def ", start_idx + 1)
    if end_idx == -1:
        end_idx = len(face_content)
    
    # Replace the method
    new_content = face_content[:start_idx] + improved_recognition + face_content[end_idx:]
    
    with open('face_service.py', 'w') as f:
        f.write(new_content)
    
    print("✅ Updated face_service.py with improved recognition logic")
else:
    print("❌ Could not find extract_face_embedding method to replace")

print("✅ Face recognition accuracy improvements completed!")
