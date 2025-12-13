# Build Guide - Executable Applications

Hướng dẫn build ứng dụng GUI thành file executable cho Windows và macOS.

## Yêu Cầu

- Python 3.8+
- PyInstaller
- Tất cả dependencies đã được cài đặt

## Cài Đặt PyInstaller

```bash
pip install pyinstaller
```

## Build Process

### Windows

1. Mở Command Prompt hoặc PowerShell
2. Di chuyển đến thư mục `gui_app`:
   ```bash
   cd gui_app
   ```
3. Chạy build script:
   ```bash
   build_windows.bat
   ```
4. Executable sẽ được tạo trong `dist/FaceRecognitionApp.exe`

### macOS

1. Mở Terminal
2. Di chuyển đến thư mục `gui_app`:
   ```bash
   cd gui_app
   ```
3. Chạy build script:
   ```bash
   ./build_mac.sh
   ```
4. Executable sẽ được tạo trong `dist/FaceRecognitionApp`

### Build Manual

Nếu build scripts không hoạt động, bạn có thể build thủ công:

```bash
cd gui_app
pyinstaller --clean build.spec
```

## Cấu Hình Build

File `build.spec` chứa cấu hình PyInstaller. Bạn có thể tùy chỉnh:

- **name**: Tên của executable
- **console**: `False` để ẩn console window (Windows)
- **icon**: Đường dẫn đến file icon (nếu có)
- **hiddenimports**: Các modules cần import thêm

## Troubleshooting

### Build Fails với Import Errors

Nếu gặp lỗi import, thêm module vào `hiddenimports` trong `build.spec`:

```python
hiddenimports=[
    'customtkinter',
    'PIL._tkinter_finder',
    'cv2',
    'mediapipe',
    'numpy',
    'requests',
    'dotenv',
    'your_missing_module',  # Thêm module bị thiếu
],
```

### Executable Quá Lớn

File executable có thể lớn (~200-300MB) do bao gồm:
- OpenCV
- MediaPipe
- NumPy
- CustomTkinter
- Python runtime

Để giảm kích thước:
- Sử dụng `--onefile` với compression
- Loại bỏ các dependencies không cần thiết
- Sử dụng UPX compression (đã bật trong spec)

### Executable Không Chạy

1. **Kiểm tra dependencies**:
   - Đảm bảo tất cả DLLs/SOs được bundle
   - Kiểm tra logs trong console (nếu `console=True`)

2. **Test trên máy khác**:
   - Copy executable sang máy khác không có Python
   - Kiểm tra xem có thiếu dependencies không

3. **Check paths**:
   - Đảm bảo các file resources được include đúng
   - Kiểm tra `datas` trong spec file

### macOS Code Signing

Trên macOS, bạn có thể cần code sign executable:

```bash
codesign --deep --force --verify --verbose --sign "Developer ID Application: Your Name" dist/FaceRecognitionApp
```

Hoặc khôngarize (nếu không có developer certificate):

```bash
xattr -cr dist/FaceRecognitionApp
```

### Windows Antivirus False Positives

Một số antivirus có thể flag PyInstaller executables. Giải pháp:
- Thêm exception trong antivirus
- Sử dụng code signing certificate
- Submit file để whitelist

## Tạo .app Bundle (macOS)

Để tạo .app bundle cho macOS:

1. Tạo cấu trúc thư mục:
   ```bash
   mkdir -p FaceRecognitionApp.app/Contents/MacOS
   mkdir -p FaceRecognitionApp.app/Contents/Resources
   ```

2. Copy executable:
   ```bash
   cp dist/FaceRecognitionApp FaceRecognitionApp.app/Contents/MacOS/
   ```

3. Tạo Info.plist (tùy chọn):
   ```xml
   <?xml version="1.0" encoding="UTF-8"?>
   <!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
   <plist version="1.0">
   <dict>
       <key>CFBundleExecutable</key>
       <string>FaceRecognitionApp</string>
       <key>CFBundleIdentifier</key>
       <string>com.yourcompany.facerecognition</string>
       <key>CFBundleName</key>
       <string>Face Recognition App</string>
       <key>CFBundleVersion</key>
       <string>1.0.0</string>
   </dict>
   </plist>
   ```

## Distribution

### Windows

- Distribute `FaceRecognitionApp.exe`
- Có thể tạo installer với Inno Setup hoặc NSIS

### macOS

- Distribute `.app` bundle hoặc `.dmg` file
- Có thể tạo `.dmg` với:
  ```bash
   hdiutil create -volname "Face Recognition App" -srcfolder FaceRecognitionApp.app -ov -format UDZO FaceRecognitionApp.dmg
   ```

## Testing

Sau khi build, test executable:

1. **Chạy trên máy build**:
   ```bash
   # Windows
   dist\FaceRecognitionApp.exe
   
   # macOS
   ./dist/FaceRecognitionApp
   ```

2. **Test trên máy sạch**:
   - Copy executable sang máy không có Python
   - Chạy và kiểm tra tất cả tính năng

3. **Test camera**:
   - Đảm bảo camera hoạt động
   - Test face detection
   - Test API connection

## Advanced Configuration

### One-file vs One-folder

- **One-file**: Tất cả trong một file, chậm hơn khi start
- **One-folder**: Nhiều files, nhanh hơn

Hiện tại spec sử dụng one-file. Để chuyển sang one-folder, sử dụng `COLLECT` thay vì `EXE`.

### UPX Compression

UPX đã được bật trong spec. Để tắt:

```python
upx=False,
```

### Icon

Thêm icon vào spec:

```python
icon='path/to/icon.ico',  # Windows
icon='path/to/icon.icns',  # macOS
```

## Best Practices

1. **Test trước khi build**: Đảm bảo app chạy tốt với `python main.py`
2. **Clean build**: Xóa `build/` và `dist/` trước khi build mới
3. **Version control**: Không commit `build/` và `dist/`
4. **Documentation**: Ghi lại các thay đổi trong spec file
5. **CI/CD**: Tự động hóa build process nếu có thể





