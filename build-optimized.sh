#!/bin/bash

echo "🚀 Building Face Recognition API with optimized Docker setup..."

# Stop any running containers
echo "📦 Stopping existing containers..."
docker-compose down

# Remove old images to force rebuild
echo "🗑️  Removing old images..."
docker rmi face_check-app 2>/dev/null || true

# Build with optimized Dockerfile
echo "🔨 Building with optimized Dockerfile..."
docker build -f Dockerfile.optimized -t face_check-app .

if [ $? -eq 0 ]; then
    echo "✅ Build successful! Starting services..."
    docker-compose up -d
    echo "🎉 Face Recognition API is running!"
    echo "📊 Check status: docker-compose ps"
    echo "📝 View logs: docker-compose logs -f"
else
    echo "❌ Build failed. Trying fallback method..."
    echo "🔨 Building with pre-built image..."
    docker build -f Dockerfile.prebuilt -t face_check-app .
    
    if [ $? -eq 0 ]; then
        echo "✅ Fallback build successful! Starting services..."
        docker-compose up -d
    else
        echo "❌ All build methods failed. Please check the logs."
        exit 1
    fi
fi
