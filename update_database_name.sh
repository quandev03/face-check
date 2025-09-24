#!/bin/bash

echo "🔄 Updating database name from face_check to face_attendance..."

# Update docker-compose.yml
sed -i '' 's/face_check/face_attendance/g' docker-compose.yml

# Update config files
sed -i '' 's/face_check/face_attendance/g' config.env.example
sed -i '' 's/face_check/face_attendance/g' config.py

# Update documentation
sed -i '' 's/face_check/face_attendance/g' README.md
sed -i '' 's/face_check/face_attendance/g' SETUP.md
sed -i '' 's/face_check/face_attendance/g' DOCKER.md

# Update test files
sed -i '' 's/face_check/face_attendance/g' test_api.py
sed -i '' 's/face_check/face_attendance/g' test_connection.py

echo "✅ Database name updated to face_attendance in all files"
echo ""
echo "🚀 Now restart the container:"
echo "   docker-compose down && docker-compose up -d"
