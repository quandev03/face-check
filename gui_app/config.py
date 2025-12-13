"""
Configuration for GUI Application
"""
import os
import sys
from pathlib import Path

# Try to load .env file, but don't fail if it doesn't exist
try:
    from dotenv import load_dotenv
    # Try to find .env file in multiple locations
    if getattr(sys, 'frozen', False):
        # Running from PyInstaller bundle
        # Try current directory and parent directories
        env_paths = [
            Path.cwd() / '.env',
            Path(sys.executable).parent / '.env',
        ]
    else:
        # Running from source
        env_paths = [
            Path(__file__).parent.parent / '.env',
            Path(__file__).parent / '.env',
            Path.cwd() / '.env',
        ]
    
    loaded = False
    for env_path in env_paths:
        if env_path.exists():
            load_dotenv(env_path)
            loaded = True
            break
    
    # If no .env found, try default load_dotenv() which searches current dir
    if not loaded:
        load_dotenv()
except Exception as e:
    # If dotenv fails, just continue without it
    print(f"Warning: Could not load .env file: {e}")

class AppConfig:
    """Application configuration"""
    
    # API Configuration
    API_BASE_URL = os.environ.get('API_BASE_URL', 'http://localhost:5555')
    API_TIMEOUT = int(os.environ.get('API_TIMEOUT', 30))
    
    # Camera Configuration
    CAMERA_INDEX = int(os.environ.get('CAMERA_INDEX', 0))
    CAMERA_WIDTH = int(os.environ.get('CAMERA_WIDTH', 640))
    CAMERA_HEIGHT = int(os.environ.get('CAMERA_HEIGHT', 480))
    
    # Face Detection Configuration
    FACE_DETECTION_CONFIDENCE = float(os.environ.get('FACE_DETECTION_CONFIDENCE', 0.5))
    FACE_QUALITY_THRESHOLD = float(os.environ.get('FACE_QUALITY_THRESHOLD', 0.5))
    AUTO_CAPTURE_DELAY = float(os.environ.get('AUTO_CAPTURE_DELAY', 2.0))  # seconds
    
    # UI Configuration
    THEME = os.environ.get('THEME', 'dark')  # 'light' or 'dark'
    COLOR_THEME = os.environ.get('COLOR_THEME', 'blue')  # 'blue', 'green', 'dark-blue'
    
    # Device Configuration
    DEVICE_CODE = os.environ.get('DEVICE_CODE', 'GUI_APP_001')

