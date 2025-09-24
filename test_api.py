#!/usr/bin/env python3
"""
Script để test các API của Face Recognition Service
"""

import requests
import json
import os
from pathlib import Path

# Configuration
BASE_URL = "http://localhost:5555"
TEST_IMAGE_PATH = "test_images"  # Thư mục chứa ảnh test

class FaceAPITester:
    def __init__(self, base_url=BASE_URL):
        self.base_url = base_url
        self.session = requests.Session()
        
    def test_health_check(self):
        """Test health check endpoint"""
        print("\n=== Testing Health Check ===")
        try:
            response = self.session.get(f"{self.base_url}/health")
            print(f"Status: {response.status_code}")
            print(f"Response: {response.json()}")
            return response.status_code == 200
        except Exception as e:
            print(f"Error: {e}")
            return False
    
    def create_test_employee(self, employee_code="TEST001", full_name="Test User"):
        """Tạo nhân viên test"""
        print(f"\n=== Creating Test Employee: {employee_code} ===")
        try:
            data = {
                "employee_code": employee_code,
                "full_name": full_name,
                "email": f"{employee_code.lower()}@test.com",
                "department": "IT",
                "position": "Tester"
            }
            
            response = self.session.post(
                f"{self.base_url}/api/employees",
                json=data,
                headers={"Content-Type": "application/json"}
            )
            
            print(f"Status: {response.status_code}")
            result = response.json()
            print(f"Response: {json.dumps(result, indent=2)}")
            
            if response.status_code == 201:
                return result['data']['id']
            elif response.status_code == 409:
                # Employee already exists, get ID
                employees = self.get_employees()
                for emp in employees:
                    if emp['employee_code'] == employee_code:
                        print(f"Employee already exists with ID: {emp['id']}")
                        return emp['id']
            return None
            
        except Exception as e:
            print(f"Error: {e}")
            return None
    
    def get_employees(self):
        """Lấy danh sách nhân viên"""
        print("\n=== Getting Employees ===")
        try:
            response = self.session.get(f"{self.base_url}/api/employees")
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"Found {result['count']} employees")
                return result['data']
            return []
            
        except Exception as e:
            print(f"Error: {e}")
            return []
    
    def enroll_face(self, employee_id, image_path, created_by="tester"):
        """Test face enrollment"""
        print(f"\n=== Enrolling Face for Employee {employee_id} ===")
        
        if not os.path.exists(image_path):
            print(f"Image file not found: {image_path}")
            return None
        
        try:
            with open(image_path, 'rb') as image_file:
                files = {'image': image_file}
                data = {
                    'employee_id': str(employee_id),
                    'created_by': created_by,
                    'source': 'ENROLL'
                }
                
                response = self.session.post(
                    f"{self.base_url}/api/face/enroll",
                    files=files,
                    data=data
                )
            
            print(f"Status: {response.status_code}")
            result = response.json()
            print(f"Response: {json.dumps(result, indent=2)}")
            
            if response.status_code == 201:
                return result['data']['face_embedding_id']
            return None
            
        except Exception as e:
            print(f"Error: {e}")
            return None
    
    def recognize_face(self, image_path):
        """Test face recognition"""
        print(f"\n=== Recognizing Face ===")
        
        if not os.path.exists(image_path):
            print(f"Image file not found: {image_path}")
            return None
        
        try:
            with open(image_path, 'rb') as image_file:
                files = {'image': image_file}
                
                response = self.session.post(
                    f"{self.base_url}/api/face/recognize",
                    files=files
                )
            
            print(f"Status: {response.status_code}")
            result = response.json()
            print(f"Response: {json.dumps(result, indent=2)}")
            
            return result
            
        except Exception as e:
            print(f"Error: {e}")
            return None
    
    def get_face_embeddings(self, employee_id=None):
        """Test getting face embeddings"""
        print(f"\n=== Getting Face Embeddings ===")
        
        try:
            url = f"{self.base_url}/api/face/embeddings"
            if employee_id:
                url += f"?employee_id={employee_id}"
            
            response = self.session.get(url)
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"Found {result['count']} face embeddings")
                return result['data']
            return []
            
        except Exception as e:
            print(f"Error: {e}")
            return []
    
    def update_face_embedding(self, face_id, **kwargs):
        """Test updating face embedding"""
        print(f"\n=== Updating Face Embedding {face_id} ===")
        
        try:
            response = self.session.put(
                f"{self.base_url}/api/face/embeddings/{face_id}",
                json=kwargs,
                headers={"Content-Type": "application/json"}
            )
            
            print(f"Status: {response.status_code}")
            result = response.json()
            print(f"Response: {json.dumps(result, indent=2)}")
            
            return response.status_code == 200
            
        except Exception as e:
            print(f"Error: {e}")
            return False
    
    def delete_face_embedding(self, face_id, hard_delete=False):
        """Test deleting face embedding"""
        print(f"\n=== Deleting Face Embedding {face_id} ===")
        
        try:
            data = {"hard_delete": hard_delete} if hard_delete else {}
            response = self.session.delete(
                f"{self.base_url}/api/face/embeddings/{face_id}",
                json=data if data else None,
                headers={"Content-Type": "application/json"} if data else None
            )
            
            print(f"Status: {response.status_code}")
            result = response.json()
            print(f"Response: {json.dumps(result, indent=2)}")
            
            return response.status_code == 200
            
        except Exception as e:
            print(f"Error: {e}")
            return False
    
    def test_storage_health(self):
        """Test storage health check"""
        print("\n=== Testing Storage Health ===")
        try:
            response = self.session.get(f"{self.base_url}/api/storage/health")
            print(f"Status: {response.status_code}")
            result = response.json()
            print(f"Response: {json.dumps(result, indent=2)}")
            return response.status_code == 200
        except Exception as e:
            print(f"Error: {e}")
            return False
    
    def get_storage_stats(self):
        """Test getting storage statistics"""
        print("\n=== Getting Storage Stats ===")
        try:
            response = self.session.get(f"{self.base_url}/api/storage/stats")
            print(f"Status: {response.status_code}")
            result = response.json()
            print(f"Response: {json.dumps(result, indent=2)}")
            return result if response.status_code == 200 else None
        except Exception as e:
            print(f"Error: {e}")
            return None
    
    def get_employee_images(self, employee_id):
        """Test getting employee images from MinIO"""
        print(f"\n=== Getting Images for Employee {employee_id} ===")
        try:
            response = self.session.get(f"{self.base_url}/api/employees/{employee_id}/images")
            print(f"Status: {response.status_code}")
            result = response.json()
            print(f"Response: {json.dumps(result, indent=2)}")
            return result if response.status_code == 200 else None
        except Exception as e:
            print(f"Error: {e}")
            return None
    
    def cleanup_old_images(self, days=30):
        """Test cleanup old images"""
        print(f"\n=== Cleaning up images older than {days} days ===")
        try:
            data = {"days": days}
            response = self.session.post(
                f"{self.base_url}/api/storage/cleanup",
                json=data,
                headers={"Content-Type": "application/json"}
            )
            print(f"Status: {response.status_code}")
            result = response.json()
            print(f"Response: {json.dumps(result, indent=2)}")
            return response.status_code == 200
        except Exception as e:
            print(f"Error: {e}")
            return False

def create_test_images_info():
    """Tạo thông tin về ảnh test cần thiết"""
    print("\n" + "="*50)
    print("HƯỚNG DẪN CHUẨN BỊ ẢNH TEST")
    print("="*50)
    print("Để test API, bạn cần chuẩn bị ảnh test:")
    print(f"1. Tạo thư mục '{TEST_IMAGE_PATH}' trong thư mục hiện tại")
    print("2. Đặt các file ảnh có khuôn mặt vào thư mục đó:")
    print("   - person1.jpg (để enroll)")
    print("   - person1_test.jpg (để test recognition - cùng người)")
    print("   - person2.jpg (để test recognition - người khác)")
    print("3. Ảnh nên có:")
    print("   - Khuôn mặt rõ nét, đủ sáng")
    print("   - Kích thước khuôn mặt ít nhất 10% diện tích ảnh")
    print("   - Format: jpg, jpeg, png, gif, bmp")
    print("="*50)

def main():
    """Main test function"""
    print("Face Recognition API Tester")
    print("=" * 40)
    
    # Initialize tester
    tester = FaceAPITester()
    
    # Test 1: Health check
    if not tester.test_health_check():
        print("❌ Health check failed. Make sure server is running.")
        return
    
    print("✅ Health check passed")
    
    # Test 2: Create test employee
    employee_id = tester.create_test_employee()
    if not employee_id:
        print("❌ Failed to create test employee")
        return
    
    print(f"✅ Test employee created with ID: {employee_id}")
    
    # Test 3: Get employees
    employees = tester.get_employees()
    print(f"✅ Retrieved {len(employees)} employees")
    
    # Check if test images exist
    test_image_dir = Path(TEST_IMAGE_PATH)
    if not test_image_dir.exists():
        create_test_images_info()
        return
    
    # Find test images
    test_images = list(test_image_dir.glob("*.jpg")) + list(test_image_dir.glob("*.jpeg")) + list(test_image_dir.glob("*.png"))
    
    if not test_images:
        print(f"❌ No test images found in {TEST_IMAGE_PATH}")
        create_test_images_info()
        return
    
    print(f"Found {len(test_images)} test images")
    
    # Test 4: Enroll face
    enroll_image = test_images[0]  # Use first image for enrollment
    face_id = tester.enroll_face(employee_id, str(enroll_image))
    
    if not face_id:
        print("❌ Failed to enroll face")
        return
    
    print(f"✅ Face enrolled with ID: {face_id}")
    
    # Test 5: Get face embeddings
    embeddings = tester.get_face_embeddings(employee_id)
    print(f"✅ Retrieved {len(embeddings)} face embeddings")
    
    # Test 6: Recognize face (same image)
    print("\n--- Testing recognition with same image ---")
    recognition_result = tester.recognize_face(str(enroll_image))
    
    if recognition_result and recognition_result.get('success'):
        print("✅ Face recognition successful (same image)")
    else:
        print("❌ Face recognition failed (same image)")
    
    # Test 7: Test with different image if available
    if len(test_images) > 1:
        print("\n--- Testing recognition with different image ---")
        test_image = test_images[1]
        recognition_result = tester.recognize_face(str(test_image))
        
        if recognition_result:
            if recognition_result.get('success'):
                print("✅ Face recognized (different image)")
            else:
                print("ℹ️ Face not recognized (different person or low quality)")
    
    # Test 8: Update face embedding
    update_success = tester.update_face_embedding(
        face_id,
        quality_score=0.95,
        created_by="api_tester"
    )
    
    if update_success:
        print("✅ Face embedding updated successfully")
    else:
        print("❌ Failed to update face embedding")
    
    # Test 9: Get updated embedding
    embeddings = tester.get_face_embeddings(employee_id)
    if embeddings:
        print("✅ Retrieved updated face embeddings")
    
    # Test 10: Test MinIO features
    print("\n--- Testing MinIO Storage Features ---")
    
    # Test storage health
    health_ok = tester.test_storage_health()
    if health_ok:
        print("✅ MinIO storage health check passed")
    else:
        print("⚠️ MinIO storage health check failed or not available")
    
    # Test storage stats
    stats = tester.get_storage_stats()
    if stats:
        print("✅ Retrieved storage statistics")
    else:
        print("⚠️ Failed to get storage statistics")
    
    # Test employee images
    images = tester.get_employee_images(employee_id)
    if images:
        print(f"✅ Retrieved {images['count']} images for employee")
    else:
        print("⚠️ Failed to get employee images or no images found")
    
    # Test 11: Delete face embedding (optional - uncomment to test)
    print("\n--- Skipping delete test (uncomment to enable) ---")
    # delete_success = tester.delete_face_embedding(face_id, hard_delete=False)
    # if delete_success:
    #     print("✅ Face embedding deleted successfully")
    # else:
    #     print("❌ Failed to delete face embedding")
    
    # Test cleanup (commented out to avoid deleting test data)
    # cleanup_success = tester.cleanup_old_images(days=365)
    # if cleanup_success:
    #     print("✅ Cleanup old images completed")
    
    print("\n" + "="*40)
    print("✅ All tests completed!")
    print("Note: MinIO features require MinIO server to be running")
    print("="*40)

if __name__ == "__main__":
    main() 