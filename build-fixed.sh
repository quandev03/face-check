#!/bin/bash

echo "🚀 Building Face Recognition API with fixed Docker setup..."

# Stop any running containers
echo "📦 Stopping existing containers..."
docker-compose down

# Remove old images to force rebuild
echo "🗑️  Removing old images..."
docker rmi face_check-app 2>/dev/null || true

# Try method 1: Pre-built dlib wheel
echo "🔨 Method 1: Trying pre-built dlib wheel..."
docker build -f Dockerfile.prebuilt-fixed -t face_check-app .

if [ $? -eq 0 ]; then
    echo "✅ Pre-built wheel method successful!"
    docker-compose up -d
    echo "🎉 Face Recognition API is running!"
    exit 0
fi

echo "❌ Pre-built wheel failed. Trying method 2..."

# Try method 2: Fixed CMake version
echo "🔨 Method 2: Trying fixed CMake version..."
docker build -f Dockerfile.fixed -t face_check-app .

if [ $? -eq 0 ]; then
    echo "✅ Fixed CMake method successful!"
    docker-compose up -d
    echo "🎉 Face Recognition API is running!"
    exit 0
fi

echo "❌ Fixed CMake failed. Trying method 3..."

# Try method 3: Alternative library (MediaPipe)
echo "🔨 Method 3: Trying MediaPipe alternative..."
docker build -f Dockerfile.mediapipe -t face_check-app .

if [ $? -eq 0 ]; then
    echo "✅ MediaPipe method successful!"
    echo "⚠️  Note: Using MediaPipe instead of dlib. You may need to update face recognition code."
    docker-compose up -d
    echo "🎉 Face Recognition API is running!"
    exit 0
fi

echo "❌ All methods failed. Please check the logs and try manual build."
exit 1
