# 🔧 Fix Docker Build Error - CMake Version Conflict

## Vấn đề
```
CMake Error: Compatibility with CMake < 3.5 has been removed from CMake
```

Lỗi này xảy ra vì:
- dlib 19.24.2 không tương thích với CMake version mới
- ARM64 architecture (Apple Silicon) có vấn đề với pybind11 trong dlib
- Python 3.11 + dlib + CMake version conflict

## Giải pháp

### 🚀 Giải pháp nhanh nhất
```bash
./build-fixed.sh
```

### 📋 Các phương pháp thủ công

#### Phương pháp 1: Pre-built wheel (Khuyến nghị)
```bash
docker build -f Dockerfile.prebuilt-fixed -t face_check-app .
```

#### Phương pháp 2: Fixed CMake version
```bash
docker build -f Dockerfile.fixed -t face_check-app .
```

#### Phương pháp 3: Alternative library (MediaPipe)
```bash
docker build -f Dockerfile.mediapipe -t face_check-app .
```

## So sánh các phương pháp

| Method | Speed | Compatibility | Pros | Cons |
|--------|-------|---------------|------|------|
| Pre-built wheel | ⚡⚡⚡ | ✅ High | Fastest, no compilation | May not work on all platforms |
| Fixed CMake | ⚡⚡ | ⚠️ Medium | Uses original dlib | Still slow, may fail |
| MediaPipe | ⚡⚡⚡ | ✅ High | Fast, modern, Google-backed | Need to update code |

## Troubleshooting

### Nếu vẫn gặp lỗi CMake:
```bash
# Check CMake version
docker run --rm python:3.11-slim cmake --version

# Force specific CMake version
docker build --build-arg CMAKE_VERSION=3.25.1 -f Dockerfile.fixed -t face_check-app .
```

### Nếu gặp lỗi ARM64:
```bash
# Build for specific platform
docker build --platform linux/amd64 -f Dockerfile.prebuilt-fixed -t face_check-app .
```

### Nếu gặp lỗi memory:
```bash
# Increase Docker memory limit
# Docker Desktop > Settings > Resources > Memory: 8GB
```

## Alternative: Use different base image

### Option A: Use Ubuntu base
```dockerfile
FROM ubuntu:22.04
RUN apt-get update && apt-get install -y python3.11 python3.11-pip
# ... rest of setup
```

### Option B: Use conda base
```dockerfile
FROM continuumio/miniconda3:latest
RUN conda install -c conda-forge dlib
# ... rest of setup
```

## Code Changes for MediaPipe

Nếu sử dụng MediaPipe, cần update face recognition code:

```python
# Replace dlib with MediaPipe
import mediapipe as mp
import cv2
import numpy as np

class FaceRecognition:
    def __init__(self):
        self.mp_face_detection = mp.solutions.face_detection
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_detection = self.mp_face_detection.FaceDetection()
        self.face_mesh = self.mp_face_mesh.FaceMesh()
    
    def get_face_embeddings(self, image):
        # MediaPipe face detection and embedding extraction
        results = self.face_detection.process(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
        # ... implementation
```

## Quick Test

```bash
# Test if dlib works
docker run --rm -it face_check-app python -c "import dlib; print('dlib works!')"

# Test if face_recognition works  
docker run --rm -it face_check-app python -c "import face_recognition; print('face_recognition works!')"
```
