"""
Utility functions and configuration management.
"""

from .config import Config

# Create singleton instance
config = Config()

# Constants
DEFAULT_CONFIG_PATH = 'config/default.json'
DATA_DIR = 'data'
CONFIG_DIR = 'config'

__all__ = [
    'Config',
    'config',
    'DEFAULT_CONFIG_PATH',
    'DATA_DIR',
    'CONFIG_DIR'
]