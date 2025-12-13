# GUI Application - Hệ Thống Nhận Diện Khuôn Mặt

Ứng dụng GUI để quản lý nhận diện khuôn mặt và chấm công nhân viên.

## Tính Năng

- **Thêm Khuôn Mặt Nhân Viên**: Đăng ký khuôn mặt mới với thông tin nhân viên
- **Nhận Diện Khuôn Mặt**: Nhận diện khuôn mặt tự động và chấm công
- **Tự Động Chụp**: Tự động chụp ảnh khi phát hiện khuôn mặt với chất lượng tốt
- **Lịch Sử Nhận Diện**: Xem lịch sử các lần nhận diện gần đây
- **Cài Đặt Linh Hoạt**: Tùy chỉnh thời gian chờ, ngưỡng chất lượng, v.v.

## Yêu Cầu Hệ Thống

- Python 3.8+
- Camera (webcam hoặc USB camera)
- Kết nối mạng để giao tiếp với API server

## Cài Đặt

### 1. Cài đặt Dependencies

```bash
cd gui_app
pip install -r requirements-gui.txt
```

Hoặc từ thư mục gốc:

```bash
pip install -r gui_app/requirements-gui.txt
```

### 2. Cấu Hình

Tạo file `.env` trong thư mục gốc (hoặc sử dụng `config.env.example`):

```bash
# API Configuration
API_BASE_URL=http://localhost:5555

# Camera Configuration
CAMERA_INDEX=0
CAMERA_WIDTH=640
CAMERA_HEIGHT=480

# Face Detection
FACE_DETECTION_CONFIDENCE=0.5
FACE_QUALITY_THRESHOLD=0.5
AUTO_CAPTURE_DELAY=2.0

# UI Configuration
THEME=dark
COLOR_THEME=blue

# Device Configuration
DEVICE_CODE=GUI_APP_001
```

### 3. Chạy Ứng Dụng

Từ thư mục gốc:

```bash
python run_gui.py
```

Hoặc từ thư mục `gui_app`:

```bash
cd gui_app
python main.py
```

## Sử Dụng

### Màn Hình Nhận Diện

1. Nhấn "Start Camera" để khởi động camera
2. Đứng trước camera để phát hiện khuôn mặt
3. Chọn một trong các tùy chọn:
   - **Tự động chụp**: Bật công tắc "Tự động chụp" - hệ thống sẽ tự động chụp khi phát hiện khuôn mặt
   - **Chụp thủ công**: Nhấn nút "Chụp Ảnh" khi sẵn sàng
4. Hệ thống sẽ nhận diện và tự động chấm công
5. Kết quả sẽ hiển thị ở panel bên phải

### Màn Hình Thêm Khuôn Mặt

1. Nhấn "Start Camera" để khởi động camera
2. Điền thông tin nhân viên:
   - Mã nhân viên (bắt buộc)
   - Họ và tên (bắt buộc)
   - Email, Phòng ban, Chức vụ (tùy chọn)
3. Đứng trước camera và nhấn "Capture" khi thấy khuôn mặt được phát hiện
4. Kiểm tra ảnh đã chụp ở preview
5. Nhấn "Đăng Ký Khuôn Mặt" để gửi dữ liệu

## Build Executable

### Windows

```bash
cd gui_app
build_windows.bat
```

Executable sẽ được tạo trong thư mục `dist/FaceRecognitionApp.exe`

### macOS

```bash
cd gui_app
./build_mac.sh
```

Executable sẽ được tạo trong thư mục `dist/FaceRecognitionApp`

### Lưu Ý Khi Build

- Đảm bảo đã cài đặt tất cả dependencies
- PyInstaller sẽ tự động bundle các dependencies
- File executable có thể khá lớn (~200-300MB) do bao gồm OpenCV và MediaPipe
- Trên macOS, bạn có thể cần cấu hình code signing để chạy ứng dụng

## Troubleshooting

### Camera không hoạt động

- Kiểm tra camera có được kết nối và hoạt động
- Thử thay đổi `CAMERA_INDEX` trong file `.env` (0, 1, 2, ...)
- Trên macOS, có thể cần cấp quyền truy cập camera trong System Preferences

### Không kết nối được API

- Kiểm tra API server đang chạy tại địa chỉ trong `API_BASE_URL`
- Kiểm tra kết nối mạng
- Xem log trong file `gui_app.log`

### Lỗi Import

- Đảm bảo đã cài đặt tất cả dependencies từ `requirements-gui.txt`
- Chạy từ thư mục gốc với `python run_gui.py`

### Face Detection không hoạt động

- Đảm bảo có đủ ánh sáng
- Khuôn mặt phải rõ ràng và chiếm đủ diện tích trong khung hình
- Kiểm tra ngưỡng `FACE_DETECTION_CONFIDENCE` trong cài đặt

## Cấu Trúc Thư Mục

```
gui_app/
├── main.py                 # Entry point
├── config.py              # Configuration
├── api_client.py          # API client
├── camera_service.py      # Camera service
├── screens/               # UI screens
│   ├── base_screen.py
│   ├── enroll_screen.py
│   └── recognize_screen.py
├── utils/                 # Utilities
│   ├── face_detector.py
│   └── image_utils.py
├── requirements-gui.txt   # Dependencies
├── build.spec            # PyInstaller spec
├── build_windows.bat     # Windows build script
└── build_mac.sh          # macOS build script
```

## API Endpoints Sử Dụng

- `GET /health` - Health check
- `POST /api/face/enroll` - Đăng ký khuôn mặt
- `POST /api/face/recognize` - Nhận diện khuôn mặt
- `GET /api/employees` - Lấy danh sách nhân viên
- `GET /api/attendance/logs` - Lấy lịch sử chấm công

## License

MIT License





