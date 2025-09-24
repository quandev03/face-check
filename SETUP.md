# 🚀 Quick Setup Guide

## 1. Cấu hình Environment Variables

Copy file cấu hình mẫu và chỉnh sửa:

```bash
cp config.env.example .env
```

Sau đó chỉnh sửa file `.env` với thông tin của bạn:

### 📊 **Database Configuration**
```bash
# Thông tin database có sẵn
DATABASE_URL=postgresql://postgres:postgres@160.191.245.38:5433/face_attendance
```

### 🔐 **Security Configuration**
```bash
# Tạo secret key mới (quan trọng cho production!)
SECRET_KEY=your-random-secret-key-here-make-it-long-and-complex
```

### ⚙️ **Face Recognition Tuning**
```bash
# Điều chỉnh độ nhạy nhận diện (0.0 - 1.0)
FACE_RECOGNITION_TOLERANCE=0.6  # Giảm để nghiêm ngặt hơn, tăng để dễ dàng hơn
```

## 2. Setup Database

### Tạo database:
```sql
-- Kết nối PostgreSQL và tạo database
CREATE DATABASE face_attendance;

-- Chuyển sang database mới
\c face_attendance;

-- Cài đặt extension pgvector
CREATE EXTENSION vector;
```

### Hoặc sử dụng command line:
```bash
# Tạo database
createdb face_attendance

# Cài đặt extension
psql -d face_attendance -c "CREATE EXTENSION vector;"
```

## 3. Cài đặt Dependencies

```bash
# Tạo virtual environment
python -m venv venv

# Activate virtual environment
# Linux/Mac:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# Cài đặt packages
pip install -r requirements.txt
```

## 4. Chạy Application

```bash
python app.py
```

Server sẽ chạy tại: `http://localhost:5555`

## 5. Test API

```bash
# Test với script có sẵn
python test_api.py

# Hoặc test health check
curl http://localhost:5555/health
```

## 📋 **Checklist Setup**

- [ ] ✅ Copy `config.env.example` thành `.env`
- [ ] ✅ Cấu hình `DATABASE_URL` trong `.env`
- [ ] ✅ Tạo database PostgreSQL
- [ ] ✅ Cài đặt pgvector extension
- [ ] ✅ Tạo virtual environment
- [ ] ✅ Cài đặt dependencies
- [ ] ✅ Chạy `python app.py`
- [ ] ✅ Test API với `python test_api.py`

## 🔧 **Common Issues & Solutions**

### 1. Database Connection Error
```
psycopg2.OperationalError: could not connect to server
```
**Solution:** Kiểm tra PostgreSQL đã chạy và thông tin kết nối trong `.env`

### 2. pgvector Extension Error
```
ERROR: extension "vector" is not available
```
**Solution:** Cài đặt pgvector extension:
```bash
git clone https://github.com/pgvector/pgvector.git
cd pgvector
make
sudo make install
```

### 3. Face Recognition Import Error
```
ImportError: No module named 'face_recognition'
```
**Solution:** Cài đặt dependencies hệ thống:
```bash
# Ubuntu/Debian
sudo apt-get install cmake libopenblas-dev liblapack-dev

# macOS
brew install cmake
```

### 4. OpenCV Error
```
ImportError: No module named 'cv2'
```
**Solution:** Cài đặt OpenCV:
```bash
# Ubuntu/Debian
sudo apt-get install libopencv-dev python3-opencv

# macOS
brew install opencv
```

## 🎯 **Production Configuration**

Khi deploy production, hãy cập nhật các giá trị sau trong `.env`:

```bash
# Production settings
FLASK_ENV=production
FLASK_DEBUG=False
SECRET_KEY=your-very-secure-random-key

# Security
CORS_ORIGINS=https://your-frontend-domain.com

# Performance
DB_POOL_MAX_CONN=50
LOG_LEVEL=WARNING
```

## 📊 **Environment Variables Reference**

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | `postgresql://...` | PostgreSQL connection string |
| `FLASK_ENV` | `development` | Flask environment |
| `FLASK_DEBUG` | `True` | Enable debug mode |
| `SECRET_KEY` | `dev-secret...` | Flask secret key |
| `UPLOAD_FOLDER` | `uploads` | File upload directory |
| `MAX_CONTENT_LENGTH` | `16777216` | Max file size (bytes) |
| `FACE_RECOGNITION_TOLERANCE` | `0.6` | Face matching tolerance |
| `HOST` | `0.0.0.0` | Server host |
| `PORT` | `5555` | Server port |
| `LOG_LEVEL` | `INFO` | Logging level |

Xem file `config.env.example` để biết đầy đủ các options có thể cấu hình. 