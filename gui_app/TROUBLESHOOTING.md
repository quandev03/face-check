# Troubleshooting Guide

## Lỗi thường gặp và cách khắc phục

### 1. "API: Lỗi" hoặc "API: Lỗi kết nối"

**Nguyên nhân:**
- API server chưa chạy
- URL API không đúng
- Firewall chặn kết nối

**Cách khắc phục:**

1. **Kiểm tra API server đang chạy:**
   ```bash
   # Kiểm tra API có đang chạy không
   curl http://localhost:5555/health
   ```

2. **Khởi động API server:**
   ```bash
   cd /Users/quandev03/Code/QLNS/Face_check
   source venv/bin/activate
   python app.py
   ```

   Hoặc dùng Docker:
   ```bash
   docker-compose up -d face-recognition-app
   ```

3. **Cập nhật API URL trong ứng dụng:**
   - Nhấn nút "⚙️ Cài Đặt" trong ứng dụng
   - Nhập đúng API Base URL (ví dụ: `http://localhost:5555`)
   - Nhấn "Lưu"
   - Khởi động lại ứng dụng

4. **Kiểm tra firewall:**
   - Đảm bảo port 5555 không bị chặn
   - Trên macOS: System Settings > Network > Firewall

### 2. "Lỗi: The path does not exist"

**Nguyên nhân:**
- Lỗi khi tạo log file
- Lỗi khi load .env file
- Lỗi từ API response

**Cách khắc phục:**

1. **Kiểm tra quyền ghi file:**
   - Ứng dụng cần quyền ghi vào thư mục temp để tạo log
   - Trên macOS: System Settings > Privacy & Security > Files and Folders

2. **Kiểm tra API response:**
   - Lỗi này có thể đến từ API server
   - Kiểm tra logs của API server để xem chi tiết

3. **Tạo file .env (tùy chọn):**
   ```bash
   cd /Users/quandev03/Code/QLNS/Face_check
   cp config.env.example .env
   # Chỉnh sửa .env với API URL đúng
   ```

### 3. Camera không hoạt động

**Nguyên nhân:**
- Camera chưa được cấp quyền
- Camera đang được sử dụng bởi ứng dụng khác
- Camera index không đúng

**Cách khắc phục:**

1. **Cấp quyền camera trên macOS:**
   - System Settings > Privacy & Security > Camera
   - Đảm bảo ứng dụng có quyền truy cập camera

2. **Kiểm tra camera index:**
   - Mặc định sử dụng camera index 0
   - Nếu có nhiều camera, thử thay đổi trong Settings

3. **Đóng ứng dụng khác đang dùng camera:**
   - Zoom, Teams, FaceTime, etc.

### 4. Không phát hiện khuôn mặt

**Nguyên nhân:**
- Ánh sáng không đủ
- Khuôn mặt quá xa camera
- Khuôn mặt bị che khuất

**Cách khắc phục:**

1. **Cải thiện điều kiện:**
   - Đảm bảo đủ ánh sáng
   - Đứng cách camera 50-100cm
   - Khuôn mặt rõ ràng, không đeo khẩu trang, kính râm

2. **Điều chỉnh settings:**
   - Giảm `FACE_DETECTION_CONFIDENCE` nếu quá strict
   - Tăng `FACE_QUALITY_THRESHOLD` để yêu cầu chất lượng cao hơn

### 5. Executable không chạy được

**Nguyên nhân:**
- Thiếu dependencies
- Lỗi code signing (macOS)
- File bị corrupt

**Cách khắc phục:**

1. **Rebuild lại:**
   ```bash
   cd /Users/quandev03/Code/QLNS/Face_check/gui_app
   rm -rf build dist
   ./build_mac.sh
   ```

2. **Kiểm tra console output:**
   - Chạy với console mode để xem lỗi chi tiết
   - Sửa `console=True` trong `build.spec`

3. **macOS Security:**
   - Nếu macOS chặn, vào System Settings > Privacy & Security
   - Cho phép ứng dụng chạy

## Kiểm tra Logs

### Khi chạy từ source:
- Log file: `gui_app/gui_app.log`

### Khi chạy từ executable:
- Log file: `/tmp/face_recognition_gui.log` (hoặc temp directory)

Xem logs:
```bash
# macOS
tail -f /tmp/face_recognition_gui.log

# Hoặc tìm trong temp directory
ls -la /var/folders/*/T/face_recognition_gui.log
```

## Test API Connection

Test API từ terminal:
```bash
# Health check
curl http://localhost:5555/health

# Test recognize (cần file ảnh)
curl -X POST -F "image=@test_face.jpg" http://localhost:5555/api/face/recognize
```

## Liên hệ hỗ trợ

Nếu vẫn gặp vấn đề:
1. Kiểm tra logs chi tiết
2. Chụp screenshot lỗi
3. Ghi lại các bước đã thử





