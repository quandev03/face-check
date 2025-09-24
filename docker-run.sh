#!/bin/bash

# Face Recognition Docker Runner
# Compatible with macOS, Windows (Git Bash/WSL), Ubuntu

echo "🚀 Starting Face Recognition Application with Docker..."

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p uploads
mkdir -p logs

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Check if docker-compose is available
if command -v docker-compose > /dev/null 2>&1; then
    COMPOSE_CMD="docker-compose"
elif docker compose version > /dev/null 2>&1; then
    COMPOSE_CMD="docker compose"
else
    echo "❌ Docker Compose is not available. Please install Docker Compose."
    exit 1
fi

echo "🔧 Using: $COMPOSE_CMD"

# Function to handle cleanup
cleanup() {
    echo "🛑 Stopping containers..."
    $COMPOSE_CMD down
    exit 0
}

# Set trap for cleanup on script exit
trap cleanup INT TERM

# Build and start the application
echo "🔨 Building Docker image..."
$COMPOSE_CMD build --no-cache

if [ $? -ne 0 ]; then
    echo "❌ Failed to build Docker image"
    exit 1
fi

echo "🚀 Starting application..."
$COMPOSE_CMD up -d

if [ $? -ne 0 ]; then
    echo "❌ Failed to start application"
    exit 1
fi

echo "✅ Application started successfully!"
echo ""
echo "📋 Service Information:"
echo "   🌐 Application: http://localhost:5000"
echo "   📊 Health Check: http://localhost:5000/health"
echo "   📚 API Docs: See README.md"
echo ""
echo "📝 Logs:"
echo "   View logs: $COMPOSE_CMD logs -f"
echo "   App logs only: $COMPOSE_CMD logs -f face-recognition-app"
echo ""
echo "🛠️ Management:"
echo "   Stop: $COMPOSE_CMD down"
echo "   Restart: $COMPOSE_CMD restart"
echo "   Rebuild: $COMPOSE_CMD up --build"
echo ""

# Wait for application to be healthy
echo "⏳ Waiting for application to be ready..."
for i in {1..30}; do
    if curl -f http://localhost:5000/health > /dev/null 2>&1; then
        echo "✅ Application is ready!"
        break
    fi
    echo "   Attempt $i/30: Waiting..."
    sleep 2
done

# Check if app is running
if curl -f http://localhost:5000/health > /dev/null 2>&1; then
    echo ""
    echo "🎉 Face Recognition Service is now running!"
    echo "   Test it: curl http://localhost:5000/health"
else
    echo ""
    echo "⚠️  Application may not be fully ready yet."
    echo "   Check logs: $COMPOSE_CMD logs face-recognition-app"
fi

echo ""
echo "💡 Tips:"
echo "   - Check container status: docker ps"
echo "   - View real-time logs: $COMPOSE_CMD logs -f"
echo "   - Stop application: $COMPOSE_CMD down"
echo "   - Run tests: python test_api.py (after installing dependencies locally)" 