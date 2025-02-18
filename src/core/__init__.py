"""
Core functionality for password generation and storage.
"""

from .password_generator import PasswordGenerator
from .storage_manager import StorageManager

# Create singleton instance for storage
storage = StorageManager()

__all__ = [
    'PasswordGenerator',
    'StorageManager',
    'storage'
]