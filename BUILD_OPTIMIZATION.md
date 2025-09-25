# 🚀 Docker Build Optimization Guide

## Vấn đề
Build Docker image bị chậm ở bước cài đặt `dlib` (hơn 17 phút) vì package này cần compile từ source code.

## Giải pháp

### 1. Sử dụng Dockerfile tối ưu (Khuyến nghị)
```bash
./build-optimized.sh
```

### 2. Build thủ công với các tùy chọn

#### Tùy chọn A: Multi-stage build (Nhanh nhất)
```bash
docker build -f Dockerfile.optimized -t face_check-app .
```

#### Tùy chọn B: Pre-built image
```bash
docker build -f Dockerfile.prebuilt -t face_check-app .
```

#### Tùy chọn C: Dockerfile gốc đã tối ưu
```bash
docker build -f Dockerfile -t face_check-app .
```

### 3. Tối ưu hóa bổ sung

#### Sử dụng BuildKit
```bash
export DOCKER_BUILDKIT=1
docker build -f Dockerfile.optimized -t face_check-app .
```

#### Build với cache từ registry
```bash
docker build --cache-from face_check-app:latest -f Dockerfile.optimized -t face_check-app .
```

#### Build song song (nếu có nhiều service)
```bash
docker-compose build --parallel
```

## So sánh thời gian build

| Method | Estimated Time | Pros | Cons |
|--------|---------------|------|------|
| Original | 20+ minutes | Simple | Very slow |
| Optimized | 5-8 minutes | Faster, better caching | More complex |
| Multi-stage | 3-5 minutes | Fastest, smaller image | Most complex |
| Pre-built | 2-3 minutes | Fastest | Larger base image |

## Troubleshooting

### Nếu build vẫn chậm:
1. Kiểm tra RAM: Cần ít nhất 4GB free RAM
2. Kiểm tra CPU: Sử dụng tất cả cores
3. Tăng Docker memory limit trong Docker Desktop

### Nếu gặp lỗi memory:
```bash
# Tăng swap space
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

### Nếu gặp lỗi dlib:
```bash
# Thử cài đặt dlib riêng trước
pip install dlib==19.24.2
```

## Monitoring Build Progress
```bash
# Xem logs build real-time
docker build --progress=plain -f Dockerfile.optimized -t face_check-app .

# Xem resource usage
docker stats
```
