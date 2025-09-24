#!/usr/bin/env python3

import requests
import json
import base64
import os

def test_face_recognition_accuracy():
    """Test face recognition accuracy with sample data"""
    
    base_url = "http://localhost:5555"
    
    print("🧪 Testing Face Recognition Accuracy")
    print("=" * 50)
    
    # 1. Check health
    try:
        response = requests.get(f"{base_url}/health")
        if response.status_code == 200:
            print("✅ API is running")
        else:
            print("❌ API is not responding")
            return
    except Exception as e:
        print(f"❌ Cannot connect to API: {e}")
        return
    
    # 2. Get current tolerance setting
    try:
        response = requests.get(f"{base_url}/api/config")
        if response.status_code == 200:
            config = response.json()
            tolerance = config.get('data', {}).get('face_recognition_tolerance', 'Unknown')
            print(f"📊 Current tolerance: {tolerance}")
    except:
        print("📊 Tolerance: 0.4 (default)")
    
    # 3. Check existing employees
    try:
        response = requests.get(f"{base_url}/api/employees")
        if response.status_code == 200:
            employees = response.json().get('data', [])
            print(f"👥 Total employees: {len(employees)}")
            
            if len(employees) == 0:
                print("⚠️  No employees found. Please create employees first.")
                return
        else:
            print("❌ Cannot get employees list")
            return
    except Exception as e:
        print(f"❌ Error getting employees: {e}")
        return
    
    # 4. Check face embeddings
    try:
        response = requests.get(f"{base_url}/api/face/embeddings")
        if response.status_code == 200:
            embeddings = response.json().get('data', [])
            print(f"🎭 Total face embeddings: {len(embeddings)}")
            
            if len(embeddings) == 0:
                print("⚠️  No face embeddings found. Please enroll faces first.")
                return
        else:
            print("❌ Cannot get face embeddings")
            return
    except Exception as e:
        print(f"❌ Error getting face embeddings: {e}")
        return
    
    print("\n📋 Recommendations for better accuracy:")
    print("1. Use high-quality images (good lighting, clear face)")
    print("2. Face should be 20-30% of image size")
    print("3. Avoid multiple faces in one image")
    print("4. Use consistent lighting conditions")
    print("5. Enroll multiple templates per person")
    print("6. Current tolerance: 0.4 (lower = more strict)")
    
    print("\n🔧 To adjust tolerance:")
    print("   - Lower tolerance (0.3-0.35): More strict, fewer false positives")
    print("   - Higher tolerance (0.5-0.6): More lenient, more false positives")
    print("   - Set FACE_RECOGNITION_TOLERANCE in environment variables")

if __name__ == "__main__":
    test_face_recognition_accuracy()
