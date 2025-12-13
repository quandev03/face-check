# Quick Start Guide - Build GUI App

## ⚠️ QUAN TRỌNG: Khởi động Database và API Server trước

GUI app cần API server và database chạy để hoạt động.

### Cách 1: Sử dụng script tự động (Khuyến nghị)

```bash
cd /Users/quandev03/Code/QLNS/Face_check
./start_local_dev.sh
```

Script này sẽ:
1. Khởi động PostgreSQL và MinIO trong Docker
2. Đợi services sẵn sàng
3. Khởi động API server

### Cách 2: Khởi động thủ công

**Bước 1: Khởi động Database services (PostgreSQL + MinIO)**

```bash
cd /Users/quandev03/Code/QLNS/Face_check
docker-compose -f docker-compose.database.yml up -d
```

**Bước 2: Kiểm tra services đã sẵn sàng**

```bash
# Kiểm tra PostgreSQL
docker exec face_attendance_postgres pg_isready -U postgres

# Kiểm tra MinIO
curl http://localhost:9000/minio/health/live
```

**Bước 3: Khởi động API server**

```bash
cd /Users/quandev03/Code/QLNS/Face_check
source venv/bin/activate

# Cài đặt API dependencies (nếu chưa có)
./venv/bin/python3 -m pip install -r requirements-mediapipe.txt

# Khởi động API server
python app.py
```

API server sẽ chạy tại `http://localhost:5555`

**Kiểm tra API đang chạy:**
```bash
curl http://localhost:5555/health
```

**Lưu ý:** File `.env` đã được tạo để kết nối đến local database. Nếu muốn dùng remote database, sửa file `.env`.

## Vấn đề thường gặp

Nếu bạn gặp lỗi "command not found: python" hoặc "command not found: pip", hãy làm theo các bước sau:

## Bước 1: Đảm bảo đang trong đúng venv

```bash
cd /Users/quandev03/Code/QLNS/Face_check
source venv/bin/activate
```

Kiểm tra venv đã được activate:
```bash
which python3
# Nên hiển thị: /Users/quandev03/Code/QLNS/Face_check/venv/bin/python3
```

## Bước 2: Cài đặt dependencies (nếu chưa có)

**Cài đặt API server dependencies:**
```bash
cd /Users/quandev03/Code/QLNS/Face_check
./venv/bin/python3 -m pip install -r requirements-mediapipe.txt
```

**Cài đặt GUI app dependencies:**
Từ thư mục gốc (`Face_check`):
```bash
./venv/bin/python3 -m pip install -r gui_app/requirements-gui.txt
./venv/bin/python3 -m pip install pyinstaller
```

Hoặc từ thư mục `gui_app`:
```bash
../venv/bin/python3 -m pip install -r requirements-gui.txt
../venv/bin/python3 -m pip install pyinstaller
```

## Bước 3: Kiểm tra dependencies

Từ thư mục `gui_app`:
```bash
../venv/bin/python3 check_dependencies.py
```

Tất cả dependencies phải hiển thị ✓

## Bước 4: Build ứng dụng

```bash
cd gui_app
./build_mac.sh
```

Hoặc:

```bash
cd gui_app
./rebuild.sh
```

## Lưu ý

- Scripts đã được cập nhật để tự động sử dụng `python3` và `pip3` từ venv
- Nếu vẫn gặp lỗi, hãy chạy trực tiếp với đường dẫn đầy đủ:
  ```bash
  /Users/quandev03/Code/QLNS/Face_check/venv/bin/python3 -m PyInstaller --clean build.spec
  ```

## Nếu venv bị lỗi

Tạo lại venv:

```bash
cd /Users/quandev03/Code/QLNS/Face_check
rm -rf venv
python3.11 -m venv venv
source venv/bin/activate
pip install -r gui_app/requirements-gui.txt
pip install pyinstaller
```

## Sơ đồ quy trình thu và nhận diện khuôn mặt

### Sơ đồ luồng (Flowchart)

Sử dụng mã PlantUML bên dưới để dựng sơ đồ luồng tổng quan:

```
@startuml
start
:Chuẩn bị camera & phần mềm;
:Phát hiện khuôn mặt từ luồng video;
:Thu nhiều khung hình (đa góc, đa biểu cảm);
if (Chất lượng đạt yêu cầu?) then (Có)
  :Tiền xử lý (cân bằng sáng, căn chỉnh mắt);
  :Trích xuất embedding;
  :Lưu embedding + metadata vào CSDL;
  :Sẵn sàng cho bước nhận diện;
  stop
else (Không)
  :Thông báo người dùng chụp lại;
  -> :Thu nhiều khung hình (đa góc, đa biểu cảm);
endif
@enduml
```

### Sơ đồ hoạt động (Activity Diagram)

Nhấn mạnh ba phân đoạn Thu mẫu → Xử lý/Lưu trữ → Nhận diện:

```
@startuml
start
partition "Thu mẫu" {
  :Phát hiện khuôn mặt;
  :Ghi nhận nhiều ảnh;
  if (Ảnh đạt chuẩn?) then (Có)
    :Chuẩn hóa & cân chỉnh;
  else (Không)
    :Thông báo chụp lại;
    back to :Ghi nhận nhiều ảnh;
  endif
}
partition "Xử lý & Lưu trữ" {
  :Trích xuất embedding;
  :Lưu embedding + metadata;
}
partition "Nhận diện" {
  :Nhận ảnh mới;
  :Trích xuất embedding mới;
  :So khớp với cơ sở dữ liệu;
  if (Điểm tương đồng >= ngưỡng?) then (Có)
    :Trả về danh tính;
  else (Không)
    :Thông báo không nhận diện được;
  endif
}
stop
@enduml
```


