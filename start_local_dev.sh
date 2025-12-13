#!/bin/bash
# Script to start local development environment

cd "$(dirname "$0")"

echo "🚀 Starting Local Development Environment"
echo ""

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker Desktop first."
    exit 1
fi

# Start database services
echo "📦 Starting PostgreSQL and MinIO..."
docker-compose -f docker-compose.database.yml up -d

# Wait for services to be ready
echo ""
echo "⏳ Waiting for services to be ready..."
sleep 5

# Check PostgreSQL
echo "Checking PostgreSQL..."
for i in {1..30}; do
    if docker exec face_attendance_postgres pg_isready -U postgres > /dev/null 2>&1; then
        echo "✅ PostgreSQL is ready"
        break
    fi
    if [ $i -eq 30 ]; then
        echo "❌ PostgreSQL failed to start"
        exit 1
    fi
    sleep 1
done

# Check MinIO
echo "Checking MinIO..."
for i in {1..30}; do
    if curl -s http://localhost:9000/minio/health/live > /dev/null 2>&1; then
        echo "✅ MinIO is ready"
        break
    fi
    if [ $i -eq 30 ]; then
        echo "⚠️  MinIO may not be ready yet, but continuing..."
    fi
    sleep 1
done

echo ""
echo "✅ Database services are running!"
echo ""
echo "📊 Service URLs:"
echo "  - PostgreSQL: localhost:5432"
echo "  - MinIO API: http://localhost:9000"
echo "  - MinIO Console: http://localhost:9001"
echo ""
echo "🔑 MinIO Credentials:"
echo "  - Username: admin"
echo "  - Password: Ngoquan@2003"
# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    if [ -f ".env.local" ]; then
        echo "📝 Creating .env from .env.local..."
        cp .env.local .env
    else
        echo "⚠️  No .env file found. Creating default .env..."
        cat > .env << EOF
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/face_attendance
MINIO_ENDPOINT=localhost:9000
MINIO_ACCESS_KEY=admin
MINIO_SECRET_KEY=Ngoquan@2003
MINIO_BUCKET_NAME=face-check
MINIO_SECURE=False
FLASK_ENV=development
FLASK_DEBUG=True
PORT=5555
EOF
    fi
fi

echo ""
echo "🚀 Starting API server..."
echo ""

# Activate venv and start API server
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
    python app.py
else
    echo "❌ Virtual environment not found. Please run setup_venv.sh first."
    exit 1
fi

