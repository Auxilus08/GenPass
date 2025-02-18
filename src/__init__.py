"""
GenPass - A Secure Password Manager
Version: 2.0.0
"""

__version__ = '2.0.0'
__author__ = 'Akshat Tiwari'

import logging

# Configure package-level logging
logging.getLogger(__name__).addHandler(logging.NullHandler())

# Package metadata
APP_NAME = 'GenPass'
DEBUG = False