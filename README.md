# Face Recognition Attendance System

Hệ thống nhận diện khuôn mặt để chấm công nhân viên sử dụng Flask, PostgreSQL và thư viện face_recognition.

## Tính năng

- **Thêm mẫu khuôn mặt**: API để đăng ký khuôn mặt nhân viên
- **Nhận diện khuôn mặt**: API để nhận diện và trả về thông tin nhân viên
- **Quản lý dữ liệu**: API để sửa, xóa thông tin khuôn mặt
- **Lưu trữ vector**: Sử dụng pgvector để lưu trữ và tìm kiếm embedding hiệu quả

## Yêu cầu hệ thống

- Python 3.8+
- PostgreSQL 12+ với extension pgvector
- MinIO Server (cho lưu trữ ảnh)
- OpenCV dependencies
- CMake (cho face_recognition)

## Cài đặt

### 1. Clone repository

```bash
git clone <repository_url>
cd Face_check
```

### 2. Tạo virtual environment

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# hoặc
venv\Scripts\activate  # Windows
```

### 3. Cài đặt dependencies

```bash
pip install -r requirements.txt
```

### 4. Cấu hình database

Tạo database PostgreSQL và cài đặt extension pgvector:

```sql
CREATE DATABASE face_attendance;
\c face_attendance;
CREATE EXTENSION vector;
```

### 5. Cấu hình MinIO Server

Khởi động MinIO server hoặc sử dụng server có sẵn:

```bash
# Nếu cài đặt local
minio server /data --console-address ":9001"

# Hoặc sử dụng Docker
docker run -p 9000:9000 -p 9001:9001 \
  -e "MINIO_ROOT_USER=admin" \
  -e "MINIO_ROOT_PASSWORD=Ngoquan@2003" \
  minio/minio server /data --console-address ":9001"
```

### 6. Cấu hình environment variables

Copy file cấu hình mẫu và chỉnh sửa:

```bash
cp config.env.example .env
```

Cấu hình cơ bản trong file `.env`:

```bash
# Database
DATABASE_URL=postgresql://postgres:postgres@160.191.245.38:5433/face_attendance

# MinIO
MINIO_ENDPOINT=160.191.245.38:9000
MINIO_ACCESS_KEY=admin
MINIO_SECRET_KEY=Ngoquan@2003
MINIO_BUCKET_NAME=face-images

# App settings
FLASK_ENV=development
FLASK_DEBUG=True
SECRET_KEY=your-secret-key-here
FACE_RECOGNITION_TOLERANCE=0.6
```

### 7. Chạy ứng dụng

```bash
python app.py
```

Server sẽ chạy tại `http://localhost:5555`

## API Documentation

### Health Check

```
GET /health
```

### Quản lý nhân viên

#### Tạo nhân viên mới
```
POST /api/employees
Content-Type: application/json

{
    "employee_code": "EMP001",
    "full_name": "Nguyễn Văn A",
    "email": "nguyenvana@company.com",
    "department": "IT",
    "position": "Developer"
}
```

#### Lấy danh sách nhân viên
```
GET /api/employees
```

### Quản lý khuôn mặt

#### Thêm mẫu khuôn mặt
```
POST /api/face/enroll
Content-Type: multipart/form-data

Form fields:
- image: file (required) - Ảnh khuôn mặt
- employee_id: integer (required) - ID nhân viên
- created_by: string (optional) - Người tạo
- source: string (optional) - Nguồn (ENROLL/VERIFY/IMPORT)
```

**Response:**
```json
{
    "success": true,
    "message": "Face enrolled successfully",
    "data": {
        "face_embedding_id": 1,
        "quality_score": 0.85,
        "bbox": {
            "top": 100,
            "right": 200,
            "bottom": 250,
            "left": 50
        },
        "image_url": "http://160.191.245.38:9000/face-images/employees/1/faces/20231201_143022_abc12345.jpg?X-Amz-...",
        "minio_object_name": "employees/1/faces/20231201_143022_abc12345.jpg"
    }
}
```

#### Nhận diện khuôn mặt
```
POST /api/face/recognize
Content-Type: multipart/form-data

Form fields:
- image: file (required) - Ảnh cần nhận diện
```

**Response (thành công):**
```json
{
    "success": true,
    "employee_id": 1,
    "employee_code": "EMP001",
    "full_name": "Nguyễn Văn A",
    "department": "IT",
    "position": "Developer",
    "confidence": 0.92,
    "distance": 0.28,
    "quality_score": 0.87
}
```

**Response (không tìm thấy):**
```json
{
    "success": false,
    "error": "No matching face found",
    "best_distance": 0.75,
    "quality_score": 0.82
}
```

#### Lấy danh sách face embeddings
```
GET /api/face/embeddings
GET /api/face/embeddings?employee_id=1
```

#### Lấy thông tin một face embedding
```
GET /api/face/embeddings/{face_id}
```

#### Cập nhật face embedding
```
PUT /api/face/embeddings/{face_id}
Content-Type: application/json

{
    "quality_score": 0.9,
    "liveness_score": 0.8,
    "status": "ACTIVE",
    "created_by": "admin"
}
```

#### Xóa face embedding
```
DELETE /api/face/embeddings/{face_id}
Content-Type: application/json

{
    "hard_delete": false  // true để xóa vĩnh viễn, false để soft delete
}
```

### Quản lý Storage (MinIO)

#### Kiểm tra tình trạng storage
```
GET /api/storage/health
```

#### Lấy thống kê storage
```
GET /api/storage/stats
```

#### Lấy danh sách ảnh của nhân viên
```
GET /api/employees/{employee_id}/images
```

#### Dọn dẹp ảnh cũ
```
POST /api/storage/cleanup
Content-Type: application/json

{
    "days": 30  // Xóa ảnh cũ hơn 30 ngày
}
```

## Cấu trúc Database

### Bảng employees
```sql
CREATE TABLE employees (
    id BIGSERIAL PRIMARY KEY,
    employee_code VARCHAR(50) UNIQUE NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    email VARCHAR(255),
    department VARCHAR(100),
    position VARCHAR(100),
    status VARCHAR(20) DEFAULT 'ACTIVE',
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);
```

### Bảng face_embeddings
```sql
CREATE TABLE face_embeddings (
    id BIGSERIAL PRIMARY KEY,
    employee_id BIGINT NOT NULL REFERENCES employees(id) ON DELETE CASCADE,
    vector vector(128) NOT NULL,
    model_name VARCHAR(64) NOT NULL DEFAULT 'face_recognition',
    model_version VARCHAR(32) NOT NULL DEFAULT '1.0',
    distance_metric VARCHAR(8) NOT NULL DEFAULT 'l2',
    quality_score REAL,
    liveness_score REAL,
    bbox INT4[4],
    source face_source NOT NULL DEFAULT 'ENROLL',
    status face_status NOT NULL DEFAULT 'ACTIVE',
    image_url TEXT,
    sha256 CHAR(64) NOT NULL,
    created_by VARCHAR(64),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

### Enum Types
```sql
CREATE TYPE face_source AS ENUM ('ENROLL', 'VERIFY', 'IMPORT');
CREATE TYPE face_status AS ENUM ('ACTIVE', 'INACTIVE', 'DELETED');
```

## Cấu hình

### Các tham số có thể điều chỉnh

- `FACE_RECOGNITION_TOLERANCE`: Ngưỡng nhận diện (mặc định: 0.6)
- `EMBEDDING_DIMENSION`: Số chiều của vector embedding (128)
- `DISTANCE_METRIC`: Phương pháp tính khoảng cách ('l2' hoặc 'cosine')
- `MAX_CONTENT_LENGTH`: Kích thước file tối đa (16MB)

## Lưu ý kỹ thuật

1. **Chất lượng ảnh**: Ảnh đầu vào nên có khuôn mặt rõ nét, đủ sáng
2. **Kích thước khuôn mặt**: Khuôn mặt nên chiếm ít nhất 10% diện tích ảnh
3. **Múi giờ**: Tất cả timestamp được lưu theo UTC
4. **Bảo mật**: Hash SHA256 được sử dụng để tránh trùng lặp ảnh
5. **Performance**: Sử dụng connection pool để tối ưu database

## Troubleshooting

### Lỗi cài đặt face_recognition
```bash
# Ubuntu/Debian
sudo apt-get install cmake libopenblas-dev liblapack-dev

# macOS
brew install cmake

# Windows
# Cài đặt Visual Studio Build Tools
```

### Lỗi pgvector
```bash
# Cài đặt pgvector extension
git clone https://github.com/pgvector/pgvector.git
cd pgvector
make
sudo make install
```

### Lỗi OpenCV
```bash
# Ubuntu/Debian
sudo apt-get install libopencv-dev python3-opencv

# macOS
brew install opencv
```

## License

MIT License 