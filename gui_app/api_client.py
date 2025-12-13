"""
API Client for communicating with Flask Face Recognition API
"""
import requests
import logging
from typing import Optional, Dict, Any, List
from io import BytesIO
from PIL import Image
import json

# Import gui_app.config - PyInstaller will bundle it correctly
try:
    from gui_app.config import AppConfig
except ImportError:
    # Fallback if running from gui_app directory
    from config import AppConfig

logger = logging.getLogger(__name__)


class APIClient:
    """Client for Face Recognition API"""
    
    def __init__(self, base_url: str = None, timeout: int = None):
        self.base_url = base_url or AppConfig.API_BASE_URL
        self.timeout = timeout or AppConfig.API_TIMEOUT
        self.session = requests.Session()
        
    def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make HTTP request with error handling"""
        url = f"{self.base_url.rstrip('/')}/{endpoint.lstrip('/')}"
        
        try:
            response = self.session.request(
                method=method,
                url=url,
                timeout=self.timeout,
                **kwargs
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.Timeout:
            logger.error(f"Request timeout: {url}")
            raise Exception("Request timeout. Please check your connection.")
        except requests.exceptions.ConnectionError:
            logger.error(f"Connection error: {url}")
            raise Exception("Cannot connect to server. Please check if the API is running.")
        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP error: {e.response.status_code} - {e.response.text}")
            try:
                error_data = e.response.json()
                error_msg = error_data.get('error', f'HTTP {e.response.status_code}')
            except:
                error_msg = f'HTTP {e.response.status_code}: {e.response.text}'
            raise Exception(error_msg)
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error: {str(e)}")
            raise Exception(f"Request failed: {str(e)}")
    
    def health_check(self) -> bool:
        """Check if API is healthy"""
        try:
            result = self._make_request('GET', '/health')
            return result.get('success', False)
        except Exception as e:
            logger.error(f"Health check failed: {str(e)}")
            return False
    
    def enroll_face(
        self,
        image_data: bytes,
        employee_code: str,
        full_name: str = None,
        email: str = None,
        department: str = None,
        position: str = None,
        created_by: str = None,
        source: str = 'ENROLL'
    ) -> Dict[str, Any]:
        """
        Enroll a face for an employee
        
        Args:
            image_data: Image bytes
            employee_code: Employee code
            full_name: Full name (optional, for creating employee if not exists)
            email: Email (optional)
            department: Department (optional)
            position: Position (optional)
            created_by: Created by (optional)
            source: Source type (ENROLL/VERIFY/IMPORT)
        
        Returns:
            Response dictionary with success status and data
        """
        # Prepare form data
        files = {
            'image': ('face.jpg', image_data, 'image/jpeg')
        }
        
        data = {
            'employee_code': employee_code,
            'source': source
        }
        
        if full_name:
            data['full_name'] = full_name
        if email:
            data['email'] = email
        if department:
            data['department'] = department
        if position:
            data['position'] = position
        if created_by:
            data['created_by'] = created_by
        
        result = self._make_request('POST', '/api/face/enroll', files=files, data=data)
        return result
    
    def recognize_face(
        self,
        image_data: bytes,
        device_code: str = None
    ) -> Dict[str, Any]:
        """
        Recognize a face from image
        
        Args:
            image_data: Image bytes
            device_code: Device code (optional)
        
        Returns:
            Response dictionary with recognition result
        """
        files = {
            'image': ('face.jpg', image_data, 'image/jpeg')
        }
        
        data = {}
        if device_code:
            data['device_code'] = device_code
        
        result = self._make_request('POST', '/api/face/recognize', files=files, data=data)
        return result
    
    def get_employees(self) -> List[Dict[str, Any]]:
        """
        Get list of all employees
        
        Returns:
            List of employee dictionaries
        """
        result = self._make_request('GET', '/api/employees')
        return result.get('data', [])
    
    def get_employee_by_code(self, employee_code: str) -> Optional[Dict[str, Any]]:
        """
        Get employee by code
        
        Args:
            employee_code: Employee code
        
        Returns:
            Employee dictionary or None
        """
        employees = self.get_employees()
        for emp in employees:
            if emp.get('employee_code') == employee_code:
                return emp
        return None
    
    def create_employee(
        self,
        employee_code: str,
        full_name: str,
        email: str = None,
        department: str = None,
        position: str = None
    ) -> Dict[str, Any]:
        """
        Create a new employee
        
        Args:
            employee_code: Employee code
            full_name: Full name
            email: Email (optional)
            department: Department (optional)
            position: Position (optional)
        
        Returns:
            Response dictionary with created employee data
        """
        data = {
            'employee_code': employee_code,
            'full_name': full_name
        }
        
        if email:
            data['email'] = email
        if department:
            data['department'] = department
        if position:
            data['position'] = position
        
        result = self._make_request('POST', '/api/employees', json=data)
        return result
    
    def get_attendance_logs(
        self,
        employee_code: str = None,
        device_code: str = None,
        date_from: str = None,
        date_to: str = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Get attendance logs
        
        Args:
            employee_code: Filter by employee code (optional)
            device_code: Filter by device code (optional)
            date_from: Start date (ISO format, optional)
            date_to: End date (ISO format, optional)
            limit: Maximum number of records (default: 100)
        
        Returns:
            List of attendance log dictionaries
        """
        params = {'limit': limit}
        
        if employee_code:
            params['employee_code'] = employee_code
        if device_code:
            params['device_code'] = device_code
        if date_from:
            params['date_from'] = date_from
        if date_to:
            params['date_to'] = date_to
        
        result = self._make_request('GET', '/api/attendance/logs', params=params)
        return result.get('data', [])
    
    def get_face_embeddings(self, employee_code: str = None) -> List[Dict[str, Any]]:
        """
        Get face embeddings
        
        Args:
            employee_code: Filter by employee code (optional)
        
        Returns:
            List of face embedding dictionaries
        """
        params = {}
        if employee_code:
            params['employee_code'] = employee_code
        
        result = self._make_request('GET', '/api/face/embeddings', params=params)
        return result.get('data', [])

