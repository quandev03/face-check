"""
Enroll Screen - Add employee face
"""
import customtkinter as ctk
import cv2
import numpy as np
import threading
import logging
from typing import Optional
from PIL import Image, ImageTk
import os
import requests
from tkinter import messagebox


from gui_app.screens.base_screen import BaseScreen
from gui_app.camera_service import CameraService
from gui_app.api_client import APIClient
from gui_app.utils.image_utils import cv2_to_pil, image_to_bytes
# Import gui_app.config - PyInstaller will bundle it correctly
try:
    from gui_app.config import AppConfig
except ImportError:
    # Fallback if running from gui_app directory
    from config import AppConfig

logger = logging.getLogger(__name__)

domain = os.environ.get("DOMAIN_API", "localhost:8080")


class EnrollScreen(BaseScreen):
    """Screen for enrolling employee faces"""
    
    def __init__(self, parent, api_client: APIClient, **kwargs):
        super().__init__(parent, **kwargs)
        
        self.api_client = api_client
        self.camera_service: Optional[CameraService] = None
        self.captured_image: Optional[np.ndarray] = None
        self.captured_detection: Optional[dict] = None
        
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup UI components"""
        # Main container
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # Left side - Camera preview
        left_frame = ctk.CTkFrame(self)
        left_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        left_frame.grid_columnconfigure(0, weight=1)
        left_frame.grid_rowconfigure(0, weight=1)
        left_frame.grid_rowconfigure(1, weight=0)
        
        # Camera preview label
        self.preview_label = ctk.CTkLabel(
            left_frame,
            text="Camera Preview\n\nClick 'Start Camera' to begin",
            width=640,
            height=480
        )
        self.preview_label.grid(row=0, column=0, padx=10, pady=10)
        
        # Camera controls
        camera_controls = ctk.CTkFrame(left_frame)
        camera_controls.grid(row=1, column=0, padx=10, pady=10, sticky="ew")
        camera_controls.grid_columnconfigure(0, weight=1)
        camera_controls.grid_columnconfigure(1, weight=1)
        camera_controls.grid_columnconfigure(2, weight=1)
        
        self.start_camera_btn = ctk.CTkButton(
            camera_controls,
            text="Start Camera",
            command=self._start_camera,
            width=150
        )
        self.start_camera_btn.grid(row=0, column=0, padx=5, pady=5)
        
        self.capture_btn = ctk.CTkButton(
            camera_controls,
            text="Capture",
            command=self._capture_face,
            width=150,
            state="disabled"
        )
        self.capture_btn.grid(row=0, column=1, padx=5, pady=5)
        
        self.stop_camera_btn = ctk.CTkButton(
            camera_controls,
            text="Stop Camera",
            command=self._stop_camera,
            width=150,
            state="disabled"
        )
        self.stop_camera_btn.grid(row=0, column=2, padx=5, pady=5)
        
        # Quality indicator
        self.quality_label = ctk.CTkLabel(
            left_frame,
            text="Quality: --",
            font=ctk.CTkFont(size=14)
        )
        self.quality_label.grid(row=2, column=0, padx=10, pady=5)
        
        # Right side - Form
        right_frame = ctk.CTkFrame(self)
        right_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        right_frame.grid_columnconfigure(0, weight=1)
        
        # Title
        title_label = ctk.CTkLabel(
            right_frame,
            text="Thêm Khuôn Mặt Nhân Viên",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        title_label.grid(row=0, column=0, padx=20, pady=20)
        
        # Form fields
        form_frame = ctk.CTkFrame(right_frame)
        form_frame.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
        form_frame.grid_columnconfigure(1, weight=1)
        
        # Employee Code
        ctk.CTkLabel(form_frame, text="Mã Nhân Viên *:").grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.employee_code_entry = ctk.CTkEntry(form_frame, width=220)
        self.employee_code_entry.grid(row=0, column=1, padx=(10,0), pady=10, sticky="ew")
        self.check_info_btn = ctk.CTkButton(form_frame, text="Kiểm tra thông tin", width=80, command=self._check_employee_info)
        self.check_info_btn.grid(row=0, column=2, padx=(6,10), pady=10, sticky="ew")
        
        # Full Name
        ctk.CTkLabel(form_frame, text="Họ và Tên *:").grid(row=1, column=0, padx=10, pady=10, sticky="w")
        self.full_name_entry = ctk.CTkEntry(form_frame, width=300)
        self.full_name_entry.configure(state="disabled")
        self.full_name_entry.grid(row=1, column=1, padx=10, pady=10, sticky="ew")
        
        # Email
        ctk.CTkLabel(form_frame, text="Email:").grid(row=2, column=0, padx=10, pady=10, sticky="w")
        self.email_entry = ctk.CTkEntry(form_frame, width=300)
        self.email_entry.configure(state="disabled")
        self.email_entry.grid(row=2, column=1, padx=10, pady=10, sticky="ew")
        
        # Department
        ctk.CTkLabel(form_frame, text="Phòng Ban:").grid(row=3, column=0, padx=10, pady=10, sticky="w")
        self.department_entry = ctk.CTkEntry(form_frame, width=300)
        self.department_entry.configure(state="disabled")
        self.department_entry.grid(row=3, column=1, padx=10, pady=10, sticky="ew")
        
        # Position
        ctk.CTkLabel(form_frame, text="Chức Vụ:").grid(row=4, column=0, padx=10, pady=10, sticky="w")
        self.position_entry = ctk.CTkEntry(form_frame, width=300)
        self.position_entry.configure(state="disabled")
        self.position_entry.grid(row=4, column=1, padx=10, pady=10, sticky="ew")
        
        # Captured image preview
        self.captured_preview_label = ctk.CTkLabel(
            right_frame,
            text="Chưa có ảnh",
            width=200,
            height=200
        )
        self.captured_preview_label.grid(row=2, column=0, padx=20, pady=10)


        # Submit button
        self.submit_btn = ctk.CTkButton(
            right_frame,
            text="Đăng Ký Khuôn Mặt",
            command=self._submit_enrollment,
            width=200,
            height=40,
            font=ctk.CTkFont(size=16),
            state="disabled"
        )
        self.submit_btn.grid(row=3, column=0, padx=20, pady=20)
        
        # Status label
        self.status_label = ctk.CTkLabel(
            right_frame,
            text="",
            font=ctk.CTkFont(size=12)
        )
        self.status_label.grid(row=4, column=0, padx=20, pady=10)
        
        # Progress bar
        self.progress_bar = ctk.CTkProgressBar(right_frame, width=300)
        self.progress_bar.grid(row=5, column=0, padx=20, pady=10)
        self.progress_bar.set(0)
        self.progress_bar.grid_remove()
    
    def _start_camera(self):
        """Start camera"""
        try:
            logger.info("Initializing CameraService...")
            self.camera_service = CameraService()
            logger.info("CameraService initialized, setting callbacks...")
            
            # Set frame callback
            self.camera_service.set_frame_callback(self._on_frame_update)
            
            logger.info("Starting camera...")
            if self.camera_service.start():
                self.start_camera_btn.configure(state="disabled")
                self.stop_camera_btn.configure(state="normal")
                self.status_label.configure(text="Camera đã khởi động", text_color="green")
                logger.info("Camera started successfully")
            else:
                error_msg = "Lỗi: Không thể khởi động camera. Vui lòng kiểm tra camera có được kết nối không."
                logger.error(error_msg)
                self.status_label.configure(text=error_msg, text_color="red")
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Error starting camera: {error_msg}", exc_info=True)
            
            # Clean up error message for user
            if "path does not exist" in error_msg.lower():
                error_msg = "Lỗi: Không tìm thấy MediaPipe model files. Vui lòng rebuild ứng dụng."
            elif "camera" in error_msg.lower():
                error_msg = f"Lỗi camera: {error_msg[:50]}"
            else:
                error_msg = f"Lỗi: {error_msg[:80]}"
            
            self.status_label.configure(text=error_msg, text_color="red")
    
    def _stop_camera(self):
        """Stop camera"""
        if self.camera_service:
            self.camera_service.stop()
            self.camera_service = None
        
        self.start_camera_btn.configure(state="normal")
        self.stop_camera_btn.configure(state="disabled")
        self.capture_btn.configure(state="disabled")
        self.preview_label.configure(image=None, text="Camera Preview\n\nClick 'Start Camera' to begin")
        self.status_label.configure(text="Camera đã dừng", text_color="gray")
    
    def _on_frame_update(self, frame: np.ndarray, detection: Optional[dict]):
        """Update preview with new frame"""
        try:
            # Draw detection if available
            if detection:
                frame = self.camera_service.face_detector.draw_detection(frame, detection)
                
                # Calculate quality
                x, y, w, h = detection['bbox']
                quality_score = self.camera_service.face_detector.calculate_quality_score(frame, (x, y, w, h))
                self.quality_label.configure(text=f"Quality: {quality_score:.2f}")
                
                # Enable capture button
                self.capture_btn.configure(state="normal")
            else:
                self.quality_label.configure(text="Quality: --")
                self.capture_btn.configure(state="disabled")
            
            # Resize for preview
            height, width = frame.shape[:2]
            max_width = 640
            max_height = 480
            
            if width > max_width or height > max_height:
                scale = min(max_width / width, max_height / height)
                new_width = int(width * scale)
                new_height = int(height * scale)
                frame = cv2.resize(frame, (new_width, new_height))
            
            # Convert to PIL and display
            pil_image = cv2_to_pil(frame)
            photo = ImageTk.PhotoImage(image=pil_image)
            
            self.preview_label.configure(image=photo, text="")
            self.preview_label.image = photo  # Keep a reference
            
        except Exception as e:
            logger.error(f"Error updating frame: {str(e)}")
    
    def _capture_face(self):
        """Capture face from camera"""
        if not self.camera_service:
            return
        
        frame = self.camera_service.get_current_frame()
        detection = self.camera_service.get_current_detection()
        
        if frame is None or detection is None:
            self.status_label.configure(text="Không phát hiện khuôn mặt", text_color="red")
            return
        
        # Store captured image and detection
        self.captured_image = frame.copy()
        self.captured_detection = detection.copy()
        
        # Extract face region
        x, y, w, h = detection['bbox']
        face_region = self.camera_service.face_detector.extract_face_region(frame, (x, y, w, h))
        
        if face_region is not None:
            # Display in preview
            pil_image = cv2_to_pil(face_region)
            photo = ImageTk.PhotoImage(image=pil_image.resize((200, 200)))
            self.captured_preview_label.configure(image=photo, text="")
            self.captured_preview_label.image = photo
            
            # Enable submit button
            self.submit_btn.configure(state="normal")
            self.status_label.configure(text="Ảnh đã được chụp. Vui lòng điền thông tin và nhấn Đăng Ký.", text_color="green")
        else:
            self.status_label.configure(text="Lỗi khi trích xuất khuôn mặt", text_color="red")
    
    def _check_employee_info(self):
        """Kiểm tra thông tin nhân viên theo mã, fill vào các trường form và disable lại các trường"""
        code = self.employee_code_entry.get().strip()
        if not code:
            self.status_label.configure(text="Vui lòng nhập mã nhân viên để kiểm tra!", text_color="red")
            return
        try:
            url = f"https://api-ns.quannh.click/api/v1/employee/get-detail-face-check?q={code}"
            resp = requests.get(url, timeout=7)
            if resp.status_code == 200:
                result = resp.json()
                # Cho phép chỉnh tạm các trường
                self.full_name_entry.configure(state="normal")
                self.email_entry.configure(state="normal")
                self.department_entry.configure(state="normal")
                self.position_entry.configure(state="normal")

                self.full_name_entry.delete(0, "end")
                self.email_entry.delete(0, "end")
                self.department_entry.delete(0, "end")
                self.position_entry.delete(0, "end")

                self.full_name_entry.insert(0, result.get("name", ""))
                self.email_entry.insert(0, result.get("email", ""))
                self.department_entry.insert(0, result.get("department", ""))
                self.position_entry.insert(0, result.get("title", ""))

                # Disable chỉnh sửa
                self.full_name_entry.configure(state="disabled")
                self.email_entry.configure(state="disabled")
                self.department_entry.configure(state="disabled")
                self.position_entry.configure(state="disabled")
                self.status_label.configure(text="Đã tự động điền thông tin nhân viên.", text_color="green")
            else:
                self.status_label.configure(text="Không tìm thấy nhân viên hoặc API lỗi!", text_color="red")
        except Exception as ex:
            self.status_label.configure(text=f"Lỗi kết nối API: {ex}", text_color="red")
    
    def _submit_enrollment(self):
        """Submit enrollment to API"""
        # Validate form
        employee_code = self.employee_code_entry.get().strip()
        full_name = self.full_name_entry.get().strip()
        
        if not employee_code:
            self.status_label.configure(text="Vui lòng nhập mã nhân viên", text_color="red")
            return
        
        if not full_name:
            self.status_label.configure(text="Vui lòng nhập họ và tên", text_color="red")
            return
        
        if self.captured_image is None or self.captured_detection is None:
            self.status_label.configure(text="Vui lòng chụp ảnh khuôn mặt", text_color="red")
            return
        
        # Disable submit button
        self.submit_btn.configure(state="disabled")
        self.progress_bar.grid()
        self.progress_bar.set(0.5)
        self.status_label.configure(text="Đang gửi dữ liệu...", text_color="blue")
        
        # Run in separate thread to avoid blocking UI
        threading.Thread(target=self._do_submit_enrollment, daemon=True).start()
    
    def _do_submit_enrollment(self):
        """Actually submit enrollment (runs in thread)"""
        try:
            # Extract face region with padding
            x, y, w, h = self.captured_detection['bbox']
            
            # Ensure minimum size for face region
            min_face_size = 100
            if w < min_face_size or h < min_face_size:
                # Use larger padding if face is too small
                padding = max(50, min_face_size - min(w, h))
            else:
                padding = 20
            
            face_region = self.camera_service.face_detector.extract_face_region(
                self.captured_image, (x, y, w, h), padding=padding
            )
            
            if face_region is None:
                self._update_status("Lỗi: Không thể trích xuất khuôn mặt", "red")
                return
            
            # Validate face region size
            # If face region is too small, send full frame (API will detect face)
            if face_region.size == 0 or face_region.shape[0] < 150 or face_region.shape[1] < 150:
                logger.warning(f"Face region too small: {face_region.shape}, using full frame")
                # Fallback: send full frame instead (API will detect face in full image)
                image_to_send = self.captured_image.copy()
                logger.info(f"Using full frame: {image_to_send.shape}")
            else:
                image_to_send = face_region
                logger.info(f"Using face region: {image_to_send.shape}")
            
            # Ensure image is in correct format (BGR for OpenCV)
            if len(image_to_send.shape) == 2:
                # Grayscale, convert to BGR
                image_to_send = cv2.cvtColor(image_to_send, cv2.COLOR_GRAY2BGR)
            elif len(image_to_send.shape) == 3 and image_to_send.shape[2] == 4:
                # RGBA, convert to BGR
                image_to_send = cv2.cvtColor(image_to_send, cv2.COLOR_RGBA2BGR)
            elif len(image_to_send.shape) == 3 and image_to_send.shape[2] == 1:
                # Single channel, convert to BGR
                image_to_send = cv2.cvtColor(image_to_send, cv2.COLOR_GRAY2BGR)
            
            # Ensure image has valid dimensions
            if image_to_send.shape[0] < 50 or image_to_send.shape[1] < 50:
                self._update_status("Lỗi: Ảnh quá nhỏ", "red")
                return
            
            # Convert to bytes
            image_bytes = image_to_bytes(image_to_send, format='JPEG', quality=95)
            
            # Validate image bytes
            if len(image_bytes) == 0:
                self._update_status("Lỗi: Không thể chuyển đổi ảnh", "red")
                return
            
            logger.info(f"Sending image: {len(image_bytes)} bytes, shape: {image_to_send.shape}")
            
            # Get form data
            employee_code = self.employee_code_entry.get().strip()
            full_name = self.full_name_entry.get().strip()
            email = self.email_entry.get().strip() or None
            department = self.department_entry.get().strip() or None
            position = self.position_entry.get().strip() or None
            
            # Call API
            result = self.api_client.enroll_face(
                image_data=image_bytes,
                employee_code=employee_code,
                full_name=full_name,
                email=email,
                department=department,
                position=position,
                source='ENROLL'
            )
            
            if result.get('success'):
                self._update_status("Đăng ký thành công!", "green")
                self.progress_bar.set(1.0)
                
                # Clear form after delay
                self.after(2000, self._clear_form)
            else:
                error_msg = result.get('error', 'Unknown error')
                self._update_status(f"Lỗi: {error_msg}", "red")
                self.progress_bar.set(0)
                self.submit_btn.configure(state="normal")
                
        except Exception as e:
            logger.error(f"Error submitting enrollment: {str(e)}")
            self._update_status(f"Lỗi: {str(e)}", "red")
            self.progress_bar.set(0)
            self.submit_btn.configure(state="normal")
    
    def _update_status(self, message: str, color: str):
        """Update status label (thread-safe)"""
        self.after(0, lambda: self.status_label.configure(text=message, text_color=color))
    
    def _clear_form(self):
        """Clear form after successful enrollment"""
        self.employee_code_entry.delete(0, "end")
        self.full_name_entry.delete(0, "end")
        self.email_entry.delete(0, "end")
        self.department_entry.delete(0, "end")
        self.position_entry.delete(0, "end")
        
        self.captured_image = None
        self.captured_detection = None
        self.captured_preview_label.configure(image=None, text="Chưa có ảnh")
        self.submit_btn.configure(state="disabled")
        self.progress_bar.set(0)
        self.progress_bar.grid_remove()
        self.status_label.configure(text="", text_color="gray")
    
    def cleanup(self):
        """Cleanup resources"""
        self._stop_camera()

    def message(self, code):
        CtkMessageMox
