#!/bin/bash

# Updated curl examples for face recognition API with employee_code (varchar)

BASE_URL="http://localhost:5555"

echo "🎯 Face Recognition API Examples (Updated for employee_code)"
echo "=========================================================="

# 1. Health Check
echo "1. Health Check:"
curl -X GET $BASE_URL/health
echo -e "\n"

# 2. Create Employee
echo "2. Create Employee:"
curl -X POST $BASE_URL/api/employees \
  -H "Content-Type: application/json" \
  -d '{
    "employee_code": "EMP003",
    "full_name": "Lê Văn C",
    "email": "levanc@company.com",
    "department": "Finance",
    "position": "Accountant"
  }'
echo -e "\n"

# 3. Get All Employees
echo "3. Get All Employees:"
curl -X GET $BASE_URL/api/employees
echo -e "\n"

# 4. Get Employee by ID
echo "4. Get Employee by ID:"
curl -X GET $BASE_URL/api/employees/6
echo -e "\n"

# 5. Update Employee
echo "5. Update Employee:"
curl -X PUT $BASE_URL/api/employees/6 \
  -H "Content-Type: application/json" \
  -d '{
    "full_name": "Ngô Hồng Quân (Updated)",
    "department": "IT",
    "position": "Senior Developer"
  }'
echo -e "\n"

# 6. Enroll Face (using employee_code)
echo "6. Enroll Face (using employee_code):"
echo "Note: Replace 'path/to/face_image.jpg' with actual image path"
curl -X POST $BASE_URL/api/face/enroll \
  -F "image=@path/to/face_image.jpg" \
  -F "employee_code=QuanNH" \
  -F "created_by=admin" \
  -F "source=ENROLL"
echo -e "\n"

# 7. Get Face Embeddings
echo "7. Get All Face Embeddings:"
curl -X GET $BASE_URL/api/face/embeddings
echo -e "\n"

# 8. Get Face Embeddings by Employee Code
echo "8. Get Face Embeddings by Employee Code:"
curl -X GET "$BASE_URL/api/face/embeddings?employee_code=QuanNH"
echo -e "\n"

# 9. Recognize Face
echo "9. Recognize Face:"
echo "Note: Replace 'path/to/test_image.jpg' with actual image path"
curl -X POST $BASE_URL/api/face/recognize \
  -F "image=@path/to/test_image.jpg"
echo -e "\n"

# 10. Delete Face Embedding
echo "10. Delete Face Embedding (Soft Delete):"
curl -X DELETE $BASE_URL/api/face/embeddings/1
echo -e "\n"

# 11. Delete Face Embedding (Hard Delete)
echo "11. Delete Face Embedding (Hard Delete):"
curl -X DELETE $BASE_URL/api/face/embeddings/1 \
  -H "Content-Type: application/json" \
  -d '{"hard_delete": true}'
echo -e "\n"

# 12. Get Storage Stats
echo "12. Get Storage Stats:"
curl -X GET $BASE_URL/api/storage/stats
echo -e "\n"

# 13. Get Storage Health
echo "13. Get Storage Health:"
curl -X GET $BASE_URL/api/storage/health
echo -e "\n"

# 14. Get Employee Images
echo "14. Get Employee Images:"
curl -X GET $BASE_URL/api/employees/QuanNH/images
echo -e "\n"

# 15. Cleanup Old Images
echo "15. Cleanup Old Images:"
curl -X POST $BASE_URL/api/storage/cleanup \
  -H "Content-Type: application/json" \
  -d '{"days": 30}'
echo -e "\n"

echo "✅ All API examples completed!"
echo ""
echo "📋 Key Changes:"
echo "- employee_id parameter changed to employee_code"
echo "- employee_code is now varchar (string) instead of integer"
echo "- All face operations now use employee_code"
echo "- Foreign key constraint: face_embeddings.employee_id -> employees.employee_code"
