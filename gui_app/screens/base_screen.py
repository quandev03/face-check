"""
Base screen class for GUI screens
"""
import customtkinter as ctk
from typing import Optional


class BaseScreen(ctk.CTkFrame):
    """Base class for all screens"""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.parent = parent
    
    def show(self):
        """Show this screen"""
        self.pack(fill="both", expand=True, padx=10, pady=10)
    
    def hide(self):
        """Hide this screen"""
        self.pack_forget()
    
    def cleanup(self):
        """Cleanup resources when screen is closed"""
        pass





