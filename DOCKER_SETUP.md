# Docker Setup Guide

Hướng dẫn thiết lập và sử dụng Docker cho hệ thống Face Recognition với PostgreSQL và MinIO.

## Tổng Quan

Docker Compose setup bao gồm:
- **PostgreSQL** với pgvector extension cho lưu trữ dữ liệu nhân viên và face embeddings
- **MinIO** cho lưu trữ ảnh khuôn mặt
- **Face Recognition App** (Flask API)

## Yêu Cầu

- Docker Engine 20.10+
- Docker Compose 2.0+

## Cấu Trúc

```
docker-compose.yml          # Full stack (database + app)
docker-compose.database.yml # Chỉ database services
docker/postgres/init.sql    # Database initialization script
```

## Sử Dụng

### 1. Chạy Toàn Bộ Stack

Chạy tất cả services (PostgreSQL, MinIO, và Face Recognition App):

```bash
docker-compose up -d
```

### 2. Chỉ Chạy Database Services

Nếu bạn muốn chạy database services riêng và kết nối từ ứng dụng bên ngoài:

```bash
docker-compose -f docker-compose.database.yml up -d
```

### 3. Xem Logs

```bash
# Tất cả services
docker-compose logs -f

# Chỉ một service
docker-compose logs -f postgres
docker-compose logs -f minio
docker-compose logs -f face-recognition-app
```

### 4. Dừng Services

```bash
docker-compose down
```

### 5. Dừng và Xóa Volumes

```bash
docker-compose down -v
```

⚠️ **Cảnh báo**: Lệnh này sẽ xóa tất cả dữ liệu!

## Services

### PostgreSQL

- **Port**: 5432
- **User**: postgres
- **Password**: postgres
- **Database**: face_attendance
- **Volume**: `postgres_data` (persistent storage)

**Kết nối từ bên ngoài**:
```bash
psql -h localhost -p 5432 -U postgres -d face_attendance
```

### MinIO

- **API Port**: 9000
- **Console Port**: 9001
- **Access Key**: admin
- **Secret Key**: Ngoquan@2003
- **Bucket**: face-check (tự động tạo)
- **Volume**: `minio_data` (persistent storage)

**Truy cập Console**:
- URL: http://localhost:9001
- Username: admin
- Password: Ngoquan@2003

### Face Recognition App

- **Port**: 5555
- **Health Check**: http://localhost:5555/health

## Cấu Hình

### Environment Variables

Các biến môi trường có thể được cấu hình trong `docker-compose.yml`:

**PostgreSQL**:
- `POSTGRES_USER`: Tên user (mặc định: postgres)
- `POSTGRES_PASSWORD`: Mật khẩu (mặc định: postgres)
- `POSTGRES_DB`: Tên database (mặc định: face_attendance)

**MinIO**:
- `MINIO_ROOT_USER`: Access key (mặc định: admin)
- `MINIO_ROOT_PASSWORD`: Secret key (mặc định: Ngoquan@2003)

**Face Recognition App**:
- `DATABASE_URL`: Connection string đến PostgreSQL
- `MINIO_ENDPOINT`: Endpoint của MinIO
- `MINIO_ACCESS_KEY`: MinIO access key
- `MINIO_SECRET_KEY`: MinIO secret key
- `MINIO_BUCKET_NAME`: Tên bucket (mặc định: face-check)

### Volumes

Dữ liệu được lưu trong Docker volumes:
- `postgres_data`: Dữ liệu PostgreSQL
- `minio_data`: Dữ liệu MinIO

Để backup, bạn có thể export volumes:

```bash
# Backup PostgreSQL
docker run --rm -v face_check_postgres_data:/data -v $(pwd):/backup \
  alpine tar czf /backup/postgres_backup.tar.gz -C /data .

# Backup MinIO
docker run --rm -v face_check_minio_data:/data -v $(pwd):/backup \
  alpine tar czf /backup/minio_backup.tar.gz -C /data .
```

## Database Initialization

Database được tự động khởi tạo khi container PostgreSQL chạy lần đầu. Script `docker/postgres/init.sql` sẽ:

1. Tạo pgvector extension
2. Tạo enum types (face_source, face_status)
3. Tạo các bảng:
   - `employees`
   - `face_embeddings`
   - `attendance_logs`
4. Tạo indexes

## MinIO Bucket Setup

Bucket `face-check` được tự động tạo bởi service `minio-setup` với quyền download công khai.

## Kết Nối Từ Ứng Dụng Bên Ngoài

Nếu bạn chạy GUI app hoặc các ứng dụng khác từ máy host:

**PostgreSQL**:
```
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/face_attendance
```

**MinIO**:
```
MINIO_ENDPOINT=localhost:9000
MINIO_ACCESS_KEY=admin
MINIO_SECRET_KEY=Ngoquan@2003
MINIO_BUCKET_NAME=face-check
MINIO_SECURE=False
```

## Troubleshooting

### PostgreSQL không khởi động

- Kiểm tra port 5432 có bị chiếm dụng không
- Xem logs: `docker-compose logs postgres`
- Kiểm tra volume permissions

### MinIO không khởi động

- Kiểm tra ports 9000 và 9001 có bị chiếm dụng không
- Xem logs: `docker-compose logs minio`

### Face Recognition App không kết nối database

- Kiểm tra service `postgres` đã healthy chưa: `docker-compose ps`
- Kiểm tra `DATABASE_URL` trong environment variables
- Xem logs: `docker-compose logs face-recognition-app`

### Dữ liệu bị mất sau khi restart

- Đảm bảo volumes được mount đúng
- Kiểm tra volumes: `docker volume ls`
- Không sử dụng `docker-compose down -v` trừ khi muốn xóa dữ liệu

## Production Considerations

⚠️ **Cảnh báo**: Cấu hình hiện tại chỉ phù hợp cho development!

Cho production, bạn nên:

1. **Thay đổi mật khẩu mặc định**:
   - PostgreSQL password
   - MinIO root credentials

2. **Sử dụng secrets management**:
   - Docker secrets
   - Environment files với quyền hạn chế

3. **Cấu hình network**:
   - Sử dụng custom network
   - Giới hạn expose ports

4. **Backup strategy**:
   - Tự động backup database
   - Backup MinIO data

5. **Monitoring**:
   - Health checks
   - Log aggregation
   - Resource monitoring

6. **Security**:
   - Enable MinIO TLS
   - PostgreSQL SSL connections
   - Firewall rules

## Commands Reference

```bash
# Start services
docker-compose up -d

# Stop services
docker-compose down

# Restart a service
docker-compose restart postgres

# View logs
docker-compose logs -f [service_name]

# Execute command in container
docker-compose exec postgres psql -U postgres -d face_attendance

# Scale services (if needed)
docker-compose up -d --scale face-recognition-app=3

# Check service status
docker-compose ps

# View resource usage
docker stats
```





