"""
Recognize Screen - Face recognition and attendance logging
"""
import customtkinter as ctk
import cv2
import numpy as np
import threading
import logging
from datetime import datetime
from typing import Optional, List
from PIL import Image, ImageTk

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


class RecognizeScreen(BaseScreen):
    """Screen for face recognition and attendance"""
    
    def __init__(self, parent, api_client: APIClient, **kwargs):
        super().__init__(parent, **kwargs)
        
        self.api_client = api_client
        self.camera_service: Optional[CameraService] = None
        self.recognition_history: List[dict] = []
        self.auto_capture_enabled = False
        
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup UI components"""
        # Main container
        self.grid_columnconfigure(0, weight=2)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # Left side - Camera and recognition
        left_frame = ctk.CTkFrame(self)
        left_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        left_frame.grid_columnconfigure(0, weight=1)
        left_frame.grid_rowconfigure(0, weight=1)
        left_frame.grid_rowconfigure(1, weight=0)
        
        # Camera preview
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
        camera_controls.grid_columnconfigure(3, weight=1)
        
        self.start_camera_btn = ctk.CTkButton(
            camera_controls,
            text="Start Camera",
            command=self._start_camera,
            width=120
        )
        self.start_camera_btn.grid(row=0, column=0, padx=5, pady=5)
        
        self.manual_capture_btn = ctk.CTkButton(
            camera_controls,
            text="Chụp Ảnh",
            command=self._manual_capture,
            width=120,
            state="disabled"
        )
        self.manual_capture_btn.grid(row=0, column=1, padx=5, pady=5)
        
        self.auto_capture_switch = ctk.CTkSwitch(
            camera_controls,
            text="Tự động chụp",
            command=self._toggle_auto_capture,
            state="disabled"
        )
        self.auto_capture_switch.grid(row=0, column=2, padx=5, pady=5)
        
        self.stop_camera_btn = ctk.CTkButton(
            camera_controls,
            text="Stop Camera",
            command=self._stop_camera,
            width=120,
            state="disabled"
        )
        self.stop_camera_btn.grid(row=0, column=3, padx=5, pady=5)
        
        # Auto-capture timer
        self.timer_label = ctk.CTkLabel(
            left_frame,
            text="",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        self.timer_label.grid(row=2, column=0, padx=10, pady=5)
        
        # Right side - Recognition results
        right_frame = ctk.CTkFrame(self)
        right_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        right_frame.grid_columnconfigure(0, weight=1)
        right_frame.grid_rowconfigure(1, weight=1)
        
        # Title
        title_label = ctk.CTkLabel(
            right_frame,
            text="Kết Quả Nhận Diện",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        title_label.grid(row=0, column=0, padx=20, pady=15)
        
        # Recognition result panel
        result_frame = ctk.CTkFrame(right_frame)
        result_frame.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")
        result_frame.grid_columnconfigure(0, weight=1)
        
        # Employee info
        self.employee_info_label = ctk.CTkLabel(
            result_frame,
            text="Chưa có kết quả",
            font=ctk.CTkFont(size=14),
            justify="left"
        )
        self.employee_info_label.grid(row=0, column=0, padx=10, pady=10, sticky="w")
        
        # Confidence/Quality
        self.confidence_label = ctk.CTkLabel(
            result_frame,
            text="",
            font=ctk.CTkFont(size=12)
        )
        self.confidence_label.grid(row=1, column=0, padx=10, pady=5, sticky="w")
        
        # Status
        self.status_label = ctk.CTkLabel(
            result_frame,
            text="",
            font=ctk.CTkFont(size=12)
        )
        self.status_label.grid(row=2, column=0, padx=10, pady=5, sticky="w")
        
        # Progress bar
        self.progress_bar = ctk.CTkProgressBar(result_frame, width=250)
        self.progress_bar.grid(row=3, column=0, padx=10, pady=10)
        self.progress_bar.set(0)
        self.progress_bar.grid_remove()
        
        # History section
        history_label = ctk.CTkLabel(
            right_frame,
            text="Lịch Sử Nhận Diện",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        history_label.grid(row=2, column=0, padx=20, pady=(20, 10))
        
        # History scrollable frame
        self.history_frame = ctk.CTkScrollableFrame(right_frame, height=200)
        self.history_frame.grid(row=3, column=0, padx=20, pady=10, sticky="nsew")
        right_frame.grid_rowconfigure(3, weight=1)
        
        # Settings button
        settings_btn = ctk.CTkButton(
            right_frame,
            text="⚙️ Cài Đặt",
            command=self._show_settings,
            width=100,
            height=30
        )
        settings_btn.grid(row=4, column=0, padx=20, pady=10)
    
    def _start_camera(self):
        """Start camera"""
        try:
            self.camera_service = CameraService()
            
            # Set callbacks
            self.camera_service.set_frame_callback(self._on_frame_update)
            self.camera_service.set_auto_capture_callback(self._on_auto_capture)
            self.camera_service.set_auto_capture_timer_callback(self._on_timer_update)
            
            if self.camera_service.start():
                self.start_camera_btn.configure(state="disabled")
                self.stop_camera_btn.configure(state="normal")
                self.manual_capture_btn.configure(state="normal")
                self.auto_capture_switch.configure(state="normal")
                self._update_status("Camera đã khởi động", "green")
            else:
                self._update_status("Lỗi: Không thể khởi động camera", "red")
        except Exception as e:
            logger.error(f"Error starting camera: {str(e)}")
            self._update_status(f"Lỗi: {str(e)}", "red")
    
    def _stop_camera(self):
        """Stop camera"""
        if self.camera_service:
            self.camera_service.stop()
            self.camera_service = None
        
        self.start_camera_btn.configure(state="normal")
        self.stop_camera_btn.configure(state="disabled")
        self.manual_capture_btn.configure(state="disabled")
        self.auto_capture_switch.configure(state="disabled")
        self.auto_capture_switch.deselect()
        self.auto_capture_enabled = False
        self.preview_label.configure(image=None, text="Camera Preview\n\nClick 'Start Camera' to begin")
        self.timer_label.configure(text="")
        self._update_status("Camera đã dừng", "gray")
    
    def _toggle_auto_capture(self):
        """Toggle auto-capture"""
        if not self.camera_service:
            return
        
        self.auto_capture_enabled = self.auto_capture_switch.get()
        self.camera_service.enable_auto_capture(self.auto_capture_enabled)
        
        if self.auto_capture_enabled:
            self._update_status("Tự động chụp đã bật", "blue")
        else:
            self.timer_label.configure(text="")
            self._update_status("Tự động chụp đã tắt", "gray")
    
    def _on_frame_update(self, frame: np.ndarray, detection: Optional[dict]):
        """Update preview with new frame"""
        try:
            # Draw detection if available
            if detection:
                frame = self.camera_service.face_detector.draw_detection(frame, detection)
            
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
    
    def _on_timer_update(self, remaining: float):
        """Update auto-capture timer display"""
        self.after(0, lambda: self.timer_label.configure(
            text=f"Tự động chụp sau: {remaining:.1f}s",
            text_color="orange"
        ))
    
    def _on_auto_capture(self, frame: np.ndarray, detection: dict, quality_score: float):
        """Handle auto-capture trigger"""
        self.after(0, lambda: self.timer_label.configure(text="Đang nhận diện...", text_color="blue"))
        self._recognize_face(frame, detection)
    
    def _manual_capture(self):
        """Manually capture and recognize"""
        if not self.camera_service:
            return
        
        frame = self.camera_service.get_current_frame()
        detection = self.camera_service.get_current_detection()
        
        if frame is None or detection is None:
            self._update_status("Không phát hiện khuôn mặt", "red")
            return
        
        self._recognize_face(frame, detection)
    
    def _recognize_face(self, frame: np.ndarray, detection: dict):
        """Recognize face from frame"""
        # Disable buttons
        self.manual_capture_btn.configure(state="disabled")
        self.progress_bar.grid()
        self.progress_bar.set(0.3)
        self._update_status("Đang nhận diện...", "blue")
        
        # Run in separate thread
        threading.Thread(target=self._do_recognize_face, args=(frame, detection), daemon=True).start()
    
    def _do_recognize_face(self, frame: np.ndarray, detection: dict):
        """Actually recognize face (runs in thread)"""
        try:
            # Extract face region
            x, y, w, h = detection['bbox']
            face_region = self.camera_service.face_detector.extract_face_region(frame, (x, y, w, h))
            
            if face_region is None:
                self._update_status("Lỗi: Không thể trích xuất khuôn mặt", "red")
                self.after(0, lambda: self.manual_capture_btn.configure(state="normal"))
                return
            
            # Convert to bytes
            image_bytes = image_to_bytes(face_region, format='JPEG', quality=95)
            
            # Update progress
            self.after(0, lambda: self.progress_bar.set(0.6))
            
            # Call API
            result = self.api_client.recognize_face(
                image_data=image_bytes,
                device_code=AppConfig.DEVICE_CODE
            )
            
            self.after(0, lambda: self.progress_bar.set(0.9))
            
            # Update UI with result
            if result.get('success'):
                employee_code = result.get('employee_code', 'N/A')
                full_name = result.get('full_name', 'N/A')
                confidence = result.get('confidence', 0.0)
                distance = result.get('distance', 0.0)
                
                # Update employee info
                info_text = f"Mã NV: {employee_code}\n"
                info_text += f"Họ tên: {full_name}\n"
                if result.get('department'):
                    info_text += f"Phòng ban: {result.get('department')}\n"
                if result.get('position'):
                    info_text += f"Chức vụ: {result.get('position')}"
                
                self.after(0, lambda: self.employee_info_label.configure(text=info_text))
                self.after(0, lambda: self.confidence_label.configure(
                    text=f"Độ tin cậy: {confidence:.2%} | Khoảng cách: {distance:.3f}",
                    text_color="green"
                ))
                
                # The API already logs attendance, so we just show success
                self._update_status("Nhận diện thành công! Đã chấm công.", "green")
                self.after(0, lambda: self.progress_bar.set(1.0))
                
                # Add to history
                history_item = {
                    'employee_code': employee_code,
                    'full_name': full_name,
                    'confidence': confidence,
                    'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                self._add_to_history(history_item)
                
            else:
                error_msg = result.get('error', 'Không nhận diện được')
                # Clean up error message - remove path details if present
                if 'path' in error_msg.lower() and 'not exist' in error_msg.lower():
                    error_msg = "Lỗi kết nối API. Vui lòng kiểm tra API server."
                
                self.after(0, lambda: self.employee_info_label.configure(text="Không nhận diện được"))
                self.after(0, lambda: self.confidence_label.configure(
                    text=error_msg[:100] if len(error_msg) > 100 else error_msg,  # Truncate long messages
                    text_color="red"
                ))
                self._update_status(f"Lỗi: {error_msg[:50]}", "red")
                self.after(0, lambda: self.progress_bar.set(0))
            
            # Re-enable button
            self.after(0, lambda: self.manual_capture_btn.configure(state="normal"))
            self.after(2000, lambda: self.progress_bar.grid_remove())
            
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Error recognizing face: {error_msg}")
            
            # Clean up error message
            if 'path' in error_msg.lower() and 'not exist' in error_msg.lower():
                error_msg = "Lỗi kết nối API. Vui lòng kiểm tra API server."
            elif 'connection' in error_msg.lower() or 'timeout' in error_msg.lower():
                error_msg = "Không thể kết nối đến API server. Vui lòng kiểm tra kết nối."
            
            self._update_status(f"Lỗi: {error_msg[:50]}", "red")
            self.after(0, lambda: self.employee_info_label.configure(text="Lỗi kết nối"))
            self.after(0, lambda: self.confidence_label.configure(
                text=error_msg[:100] if len(error_msg) > 100 else error_msg,
                text_color="red"
            ))
            self.after(0, lambda: self.manual_capture_btn.configure(state="normal"))
            self.after(0, lambda: self.progress_bar.set(0))
            self.after(0, lambda: self.progress_bar.grid_remove())
    
    def _add_to_history(self, item: dict):
        """Add recognition result to history"""
        self.recognition_history.insert(0, item)
        
        # Limit history size
        if len(self.recognition_history) > 20:
            self.recognition_history = self.recognition_history[:20]
        
        # Update UI
        self.after(0, self._update_history_display)
    
    def _update_history_display(self):
        """Update history display"""
        # Clear existing items
        for widget in self.history_frame.winfo_children():
            widget.destroy()
        
        # Add history items
        for i, item in enumerate(self.recognition_history[:10]):  # Show last 10
            history_item_frame = ctk.CTkFrame(self.history_frame)
            history_item_frame.grid(row=i, column=0, padx=5, pady=2, sticky="ew")
            history_item_frame.grid_columnconfigure(0, weight=1)
            
            text = f"{item['timestamp']} - {item['full_name']} ({item['employee_code']})"
            if item.get('confidence'):
                text += f" - {item['confidence']:.1%}"
            
            label = ctk.CTkLabel(
                history_item_frame,
                text=text,
                font=ctk.CTkFont(size=11),
                anchor="w"
            )
            label.grid(row=0, column=0, padx=10, pady=5, sticky="ew")
    
    def _update_status(self, message: str, color: str):
        """Update status label (thread-safe)"""
        self.after(0, lambda: self.status_label.configure(text=message, text_color=color))
    
    def _show_settings(self):
        """Show settings dialog"""
        # Simple settings dialog
        settings_window = ctk.CTkToplevel(self)
        settings_window.title("Cài Đặt")
        settings_window.geometry("400x300")
        
        # Auto-capture delay
        ctk.CTkLabel(settings_window, text="Thời gian chờ tự động chụp (giây):").pack(pady=10)
        delay_var = ctk.StringVar(value=str(AppConfig.AUTO_CAPTURE_DELAY))
        delay_entry = ctk.CTkEntry(settings_window, textvariable=delay_var, width=200)
        delay_entry.pack(pady=5)
        
        # Quality threshold
        ctk.CTkLabel(settings_window, text="Ngưỡng chất lượng (0.0-1.0):").pack(pady=10)
        quality_var = ctk.StringVar(value=str(AppConfig.FACE_QUALITY_THRESHOLD))
        quality_entry = ctk.CTkEntry(settings_window, textvariable=quality_var, width=200)
        quality_entry.pack(pady=5)
        
        def save_settings():
            try:
                delay = float(delay_var.get())
                quality = float(quality_var.get())
                
                if 0.1 <= delay <= 10.0 and 0.0 <= quality <= 1.0:
                    if self.camera_service:
                        self.camera_service.set_auto_capture_delay(delay)
                        self.camera_service.set_auto_capture_quality_threshold(quality)
                    settings_window.destroy()
                else:
                    ctk.CTkMessageBox.showwarning("Cảnh báo", "Giá trị không hợp lệ")
            except ValueError:
                ctk.CTkMessageBox.showerror("Lỗi", "Vui lòng nhập số hợp lệ")
        
        save_btn = ctk.CTkButton(settings_window, text="Lưu", command=save_settings)
        save_btn.pack(pady=20)
    
    def cleanup(self):
        """Cleanup resources"""
        self._stop_camera()

