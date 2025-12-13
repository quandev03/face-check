"""
Main Application Entry Point
Face Recognition Attendance System - GUI Application
"""
import customtkinter as ctk
import logging
import sys
import os
from pathlib import Path

# Add parent directory to path for imports
parent_dir = str(Path(__file__).parent.parent)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Import with explicit gui_app prefix to avoid conflicts
# PyInstaller will bundle all gui_app modules correctly
from gui_app.config import AppConfig
from gui_app.api_client import APIClient
from gui_app.screens.enroll_screen import EnrollScreen
from gui_app.screens.recognize_screen import RecognizeScreen

# Setup logging
# Determine log file path - use temp directory if running from executable
if getattr(sys, 'frozen', False):
    # Running from PyInstaller bundle
    import tempfile
    log_dir = tempfile.gettempdir()
    log_file = os.path.join(log_dir, 'face_recognition_gui.log')
else:
    # Running from source
    log_file = os.path.join(os.path.dirname(__file__), 'gui_app.log')

try:
    handlers = [
        logging.FileHandler(log_file),
        logging.StreamHandler(sys.stdout)
    ]
except Exception as e:
    # If file logging fails, just use console
    handlers = [logging.StreamHandler(sys.stdout)]
    print(f"Warning: Could not create log file: {e}")

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=handlers
)
logger = logging.getLogger(__name__)


class FaceRecognitionApp(ctk.CTk):
    """Main application window"""
    
    def __init__(self):
        super().__init__()
        
        # Configure window
        self.title("Hệ Thống Nhận Diện Khuôn Mặt - Chấm Công")
        self.geometry("1200x700")
        self.minsize(1000, 600)
        
        # Set theme
        ctk.set_appearance_mode(AppConfig.THEME)
        ctk.set_default_color_theme(AppConfig.COLOR_THEME)
        
        # Initialize API client
        try:
            self.api_client = APIClient()
            # Test connection
            if not self.api_client.health_check():
                logger.warning("API health check failed, but continuing...")
        except Exception as e:
            logger.error(f"Failed to initialize API client: {str(e)}")
            self.api_client = None
            self._show_error_dialog(
                "Lỗi Kết Nối",
                f"Không thể kết nối đến API server.\n\nLỗi: {str(e)}\n\nVui lòng kiểm tra:\n"
                f"1. API server đang chạy tại {AppConfig.API_BASE_URL}\n"
                f"2. Kết nối mạng\n\nỨng dụng vẫn có thể chạy nhưng một số tính năng sẽ không hoạt động."
            )
        
        # Current screen
        self.current_screen = None
        self.screens = {}
        
        # Setup UI
        self._setup_ui()
        
        # Load default screen
        self._switch_screen('recognize')
        
        # Handle window close
        self.protocol("WM_DELETE_WINDOW", self._on_closing)
    
    def _setup_ui(self):
        """Setup main UI"""
        # Configure grid
        self.grid_columnconfigure(0, weight=0)  # Sidebar
        self.grid_columnconfigure(1, weight=1)  # Content
        self.grid_rowconfigure(0, weight=1)
        
        # Sidebar
        sidebar = ctk.CTkFrame(self, width=200, corner_radius=0)
        sidebar.grid(row=0, column=0, sticky="nsew")
        sidebar.grid_rowconfigure(4, weight=1)
        sidebar.grid_propagate(False)
        
        # Logo/Title
        title_label = ctk.CTkLabel(
            sidebar,
            text="Face Recognition\nAttendance",
            font=ctk.CTkFont(size=20, weight="bold"),
            anchor="center"
        )
        title_label.grid(row=0, column=0, padx=20, pady=30)
        
        # Navigation buttons
        self.recognize_btn = ctk.CTkButton(
            sidebar,
            text="📷 Nhận Diện",
            command=lambda: self._switch_screen('recognize'),
            width=180,
            height=50,
            font=ctk.CTkFont(size=16),
            corner_radius=10
        )
        self.recognize_btn.grid(row=1, column=0, padx=10, pady=10)
        
        self.enroll_btn = ctk.CTkButton(
            sidebar,
            text="➕ Thêm Khuôn Mặt",
            command=lambda: self._switch_screen('enroll'),
            width=180,
            height=50,
            font=ctk.CTkFont(size=16),
            corner_radius=10
        )
        self.enroll_btn.grid(row=2, column=0, padx=10, pady=10)
        
        # API Status
        self.api_status_label = ctk.CTkLabel(
            sidebar,
            text="API: Đang kiểm tra...",
            font=ctk.CTkFont(size=12)
        )
        self.api_status_label.grid(row=3, column=0, padx=10, pady=10)
        
        # Check API status
        self._check_api_status()
        
        # Settings button
        settings_btn = ctk.CTkButton(
            sidebar,
            text="⚙️ Cài Đặt",
            command=self._show_settings,
            width=180,
            height=40,
            font=ctk.CTkFont(size=14)
        )
        settings_btn.grid(row=5, column=0, padx=10, pady=10)
        
        # About button
        about_btn = ctk.CTkButton(
            sidebar,
            text="ℹ️ Giới Thiệu",
            command=self._show_about,
            width=180,
            height=40,
            font=ctk.CTkFont(size=14)
        )
        about_btn.grid(row=6, column=0, padx=10, pady=10)
        
        # Content area
        self.content_frame = ctk.CTkFrame(self)
        self.content_frame.grid(row=0, column=1, sticky="nsew", padx=0, pady=0)
        self.content_frame.grid_columnconfigure(0, weight=1)
        self.content_frame.grid_rowconfigure(0, weight=1)
        
        # Initialize screens
        if self.api_client:
            self.screens['enroll'] = EnrollScreen(self.content_frame, self.api_client)
            self.screens['recognize'] = RecognizeScreen(self.content_frame, self.api_client)
        else:
            # Create placeholder screens if API is not available
            error_screen = ctk.CTkFrame(self.content_frame)
            error_label = ctk.CTkLabel(
                error_screen,
                text="Không thể kết nối đến API server.\nVui lòng kiểm tra kết nối và thử lại.",
                font=ctk.CTkFont(size=16),
                justify="center"
            )
            error_label.pack(expand=True)
            self.screens['enroll'] = error_screen
            self.screens['recognize'] = error_screen
    
    def _switch_screen(self, screen_name: str):
        """Switch to a different screen"""
        # Hide current screen
        if self.current_screen:
            if hasattr(self.current_screen, 'hide'):
                self.current_screen.hide()
            else:
                self.current_screen.pack_forget()
        
        # Show new screen
        if screen_name in self.screens:
            self.current_screen = self.screens[screen_name]
            if hasattr(self.current_screen, 'show'):
                self.current_screen.show()
            else:
                self.current_screen.pack(fill="both", expand=True)
            
            # Update button states
            if screen_name == 'recognize':
                self.recognize_btn.configure(fg_color=("gray75", "gray25"))
                self.enroll_btn.configure(fg_color=("gray70", "gray30"))
            else:
                self.enroll_btn.configure(fg_color=("gray75", "gray25"))
                self.recognize_btn.configure(fg_color=("gray70", "gray30"))
        else:
            logger.error(f"Screen '{screen_name}' not found")
    
    def _check_api_status(self):
        """Check API connection status"""
        def check():
            if self.api_client:
                try:
                    is_healthy = self.api_client.health_check()
                    status_text = "API: Kết nối" if is_healthy else "API: Lỗi"
                    status_color = "green" if is_healthy else "red"
                    self.after(0, lambda: self.api_status_label.configure(
                        text=status_text,
                        text_color=status_color
                    ))
                except Exception as e:
                    self.after(0, lambda: self.api_status_label.configure(
                        text="API: Lỗi kết nối",
                        text_color="red"
                    ))
            else:
                self.after(0, lambda: self.api_status_label.configure(
                    text="API: Chưa kết nối",
                    text_color="orange"
                ))
        
        # Run in separate thread
        import threading
        threading.Thread(target=check, daemon=True).start()
        
        # Schedule next check
        self.after(30000, self._check_api_status)  # Check every 30 seconds
    
    def _show_settings(self):
        """Show settings dialog"""
        settings_window = ctk.CTkToplevel(self)
        settings_window.title("Cài Đặt")
        settings_window.geometry("500x400")
        
        # API URL
        ctk.CTkLabel(settings_window, text="API Base URL:", font=ctk.CTkFont(size=14)).pack(pady=10)
        api_url_var = ctk.StringVar(value=AppConfig.API_BASE_URL)
        api_url_entry = ctk.CTkEntry(settings_window, textvariable=api_url_var, width=400)
        api_url_entry.pack(pady=5)
        
        # Theme
        ctk.CTkLabel(settings_window, text="Giao diện:", font=ctk.CTkFont(size=14)).pack(pady=10)
        theme_var = ctk.StringVar(value=AppConfig.THEME)
        theme_menu = ctk.CTkOptionMenu(
            settings_window,
            values=["light", "dark"],
            variable=theme_var,
            width=400
        )
        theme_menu.pack(pady=5)
        
        # Color theme
        ctk.CTkLabel(settings_window, text="Màu sắc:", font=ctk.CTkFont(size=14)).pack(pady=10)
        color_var = ctk.StringVar(value=AppConfig.COLOR_THEME)
        color_menu = ctk.CTkOptionMenu(
            settings_window,
            values=["blue", "green", "dark-blue"],
            variable=color_var,
            width=400
        )
        color_menu.pack(pady=5)
        
        def save_settings():
            # Update config (in-memory only, would need to save to file for persistence)
            AppConfig.API_BASE_URL = api_url_var.get()
            AppConfig.THEME = theme_var.get()
            AppConfig.COLOR_THEME = color_var.get()
            
            # Apply theme
            ctk.set_appearance_mode(AppConfig.THEME)
            ctk.set_default_color_theme(AppConfig.COLOR_THEME)
            
            # Reinitialize API client
            try:
                self.api_client = APIClient()
            except Exception as e:
                logger.error(f"Error reinitializing API client: {str(e)}")
            
            settings_window.destroy()
            self._show_info_dialog("Thành công", "Cài đặt đã được lưu. Vui lòng khởi động lại ứng dụng để áp dụng thay đổi.")
        
        save_btn = ctk.CTkButton(settings_window, text="Lưu", command=save_settings, width=200)
        save_btn.pack(pady=20)
    
    def _show_about(self):
        """Show about dialog"""
        about_text = """
Hệ Thống Nhận Diện Khuôn Mặt - Chấm Công

Phiên bản: 1.0.0

Ứng dụng GUI để quản lý nhận diện khuôn mặt và chấm công nhân viên.

Tính năng:
• Thêm khuôn mặt nhân viên
• Nhận diện khuôn mặt tự động
• Chấm công tự động
• Lịch sử nhận diện

Công nghệ:
• CustomTkinter
• MediaPipe
• OpenCV
• Flask API
        """
        
        about_window = ctk.CTkToplevel(self)
        about_window.title("Giới Thiệu")
        about_window.geometry("400x500")
        
        about_label = ctk.CTkLabel(
            about_window,
            text=about_text,
            font=ctk.CTkFont(size=12),
            justify="left"
        )
        about_label.pack(padx=20, pady=20)
    
    def _show_error_dialog(self, title: str, message: str):
        """Show error dialog"""
        # Use messagebox for now (CustomTkinter doesn't have built-in messagebox)
        import tkinter.messagebox as messagebox
        messagebox.showerror(title, message)
    
    def _show_info_dialog(self, title: str, message: str):
        """Show info dialog"""
        import tkinter.messagebox as messagebox
        messagebox.showinfo(title, message)
    
    def _on_closing(self):
        """Handle window closing"""
        # Cleanup screens
        for screen in self.screens.values():
            if hasattr(screen, 'cleanup'):
                try:
                    screen.cleanup()
                except Exception as e:
                    logger.error(f"Error cleaning up screen: {str(e)}")
        
        # Destroy window
        self.destroy()
        sys.exit(0)


def main():
    """Main entry point"""
    try:
        app = FaceRecognitionApp()
        app.mainloop()
    except KeyboardInterrupt:
        logger.info("Application interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()

