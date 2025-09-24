# 🐳 Docker Deployment Guide

Hướng dẫn chạy Face Recognition Service bằng Docker trên macOS, Windows và Ubuntu.

## 📋 Yêu cầu

- **Docker Desktop** (macOS/Windows) hoặc **Docker Engine** (Ubuntu)
- **Docker Compose** (thường đi kèm với Docker Desktop)
- **Database PostgreSQL** và **MinIO** đã chạy sẵn

## 🚀 Cách chạy nhanh

### 1️⃣ macOS / Linux / WSL
```bash
# Cấp quyền thực thi
chmod +x docker-run.sh

# Chạy script
./docker-run.sh
```

### 2️⃣ Windows (Command Prompt/PowerShell)
```cmd
# Chạy script
docker-run.bat
```

### 3️⃣ Manual (tất cả OS)
```bash
# Build và chạy
docker-compose up --build -d

# Xem logs
docker-compose logs -f

# Dừng
docker-compose down
```

## ⚙️ Cấu hình

### Database & MinIO Connection
Ứng dụng sẽ kết nối với:
- **PostgreSQL**: `160.191.245.38:5433` (database server có sẵn)
- **MinIO**: `160.191.245.38:9000` (MinIO server có sẵn)

### Environment Variables
Chỉnh sửa trong `docker-compose.yml`:
```yaml
environment:
  # Database
  DATABASE_URL: postgresql://postgres:postgres@160.191.245.38:5433/face_attendance
  
  # MinIO
  MINIO_ENDPOINT: 160.191.245.38:9000
  MINIO_ACCESS_KEY: admin
  MINIO_SECRET_KEY: Ngoquan@2003
  
  # App settings
  FACE_RECOGNITION_TOLERANCE: 0.6
```

## 🔧 Troubleshooting

### 1. Database Connection Issues

**Lỗi**: `could not connect to server`

**Giải pháp**:
- Đảm bảo PostgreSQL đang chạy tại `160.191.245.38:5433`
- Kiểm tra firewall cho phép kết nối port 5433
- Test kết nối: `telnet 160.191.245.38 5433`

```yaml
# Trong docker-compose.yml
DATABASE_URL: postgresql://postgres:postgres@160.191.245.38:5433/face_attendance
```

### 2. MinIO Connection Issues

**Lỗi**: `MinIO service not available`

**Giải pháp**:
- Kiểm tra MinIO server đang chạy tại `160.191.245.38:9000`
- Test kết nối: `curl http://160.191.245.38:9000/minio/health/live`
- Kiểm tra credentials trong docker-compose.yml

### 3. Docker Build Issues

**Lỗi**: `face_recognition` build failed

**Giải pháp macOS**:
```bash
# Cài đặt dependencies
brew install cmake

# Build với platform cụ thể
docker-compose build --build-arg BUILDPLATFORM=linux/amd64
```

**Giải pháp Windows**:
```cmd
# Đảm bảo Docker Desktop đang chạy Linux containers
# Build với WSL2 backend
```

**Giải pháp Ubuntu**:
```bash
# Cài đặt build dependencies
sudo apt-get update
sudo apt-get install build-essential cmake

# Build
docker-compose build
```

### 4. Platform-specific Solutions

#### macOS (Apple Silicon M1/M2)
```yaml
# Trong docker-compose.yml, thêm:
services:
  face-recognition-app:
    platform: linux/amd64  # Force x86_64
    # ... rest of config
```

#### Windows
```yaml
# Sử dụng Windows containers (nếu cần)
services:
  face-recognition-app:
    # Sử dụng Windows base image
    build:
      context: .
      dockerfile: Dockerfile.windows  # Tạo riêng nếu cần
```

## 📊 Monitoring

### Health Checks
```bash
# Kiểm tra container status
docker ps

# Health check endpoint
curl http://localhost:5555/health

# Container health status
docker inspect face_attendance_app --format='{{.State.Health.Status}}'
```

### Logs
```bash
# All logs
docker-compose logs -f

# App logs only
docker-compose logs -f face-recognition-app

# Last 100 lines
docker-compose logs --tail=100 face-recognition-app
```

### Resource Usage
```bash
# Container stats
docker stats face_attendance_app

# Detailed info
docker inspect face_attendance_app
```

## 🛠️ Development

### Development Mode
```bash
# Mount source code for development
docker-compose -f docker-compose.dev.yml up
```

### Debug Mode
```yaml
# Trong docker-compose.yml
environment:
  FLASK_DEBUG: "True"
  LOG_LEVEL: DEBUG
```

### Hot Reload
```yaml
# Mount source code
volumes:
  - .:/app
  - ./uploads:/app/uploads
```

## 🔒 Production Deployment

### Security Settings
```yaml
environment:
  FLASK_ENV: production
  FLASK_DEBUG: "False"
  SECRET_KEY: your-very-secure-production-key
  LOG_LEVEL: WARNING
```

### Performance Tuning
```yaml
environment:
  DB_POOL_MAX_CONN: 50
  WORKER_PROCESSES: 4
```

### SSL/HTTPS
```yaml
# Use reverse proxy (nginx/traefik)
labels:
  - "traefik.enable=true"
  - "traefik.http.routers.face-app.rule=Host(`your-domain.com`)"
  - "traefik.http.routers.face-app.tls.certresolver=letsencrypt"
```

## 📈 Scaling

### Multiple Replicas
```bash
# Scale to 3 instances
docker-compose up --scale face-recognition-app=3
```

### Load Balancer
```yaml
# nginx.conf
upstream face_recognition {
    server localhost:5555;
    server localhost:5001;
    server localhost:5002;
}
```

## 🧪 Testing

### Run Tests
```bash
# Install test dependencies locally first
pip install requests

# Run API tests against Docker container
python test_api.py
```

### Integration Tests
```bash
# Test all endpoints
curl http://localhost:5555/health
curl http://localhost:5555/api/employees
curl http://localhost:5555/api/storage/health
```

## 📚 Useful Commands

```bash
# Build without cache
docker-compose build --no-cache

# Restart specific service
docker-compose restart face-recognition-app

# View container details
docker inspect face_attendance_app

# Execute command in container
docker exec -it face_attendance_app bash

# Copy files from container
docker cp face_attendance_app:/app/logs ./local-logs

# Remove everything
docker-compose down -v --rmi all
```

## 🆘 Support

Nếu gặp vấn đề:

1. **Check logs**: `docker-compose logs -f`
2. **Verify connections**: Test database và MinIO connectivity
3. **Resource limits**: Ensure Docker has enough memory (4GB+ recommended)
4. **Platform issues**: Try different base images for your architecture

## 📝 Notes

- Container sử dụng port `5000` (có thể thay đổi trong docker-compose.yml)
- Uploads folder được mount để persist data
- Logs folder được tạo để lưu application logs
- Health checks đảm bảo container ready trước khi serve traffic 