"""
Authentication and security related functionality.
"""

from .user_auth import UserAuth
from .two_factor import TwoFactorAuth

# Create singleton instances
auth = UserAuth()
two_factor = TwoFactorAuth()

# Authentication constants
TOKEN_EXPIRY = 3600  # seconds
MAX_LOGIN_ATTEMPTS = 3
LOCKOUT_DURATION = 900  # seconds

__all__ = [
    'UserAuth',
    'TwoFactorAuth',
    'auth',
    'two_factor',
    'TOKEN_EXPIRY',
    'MAX_LOGIN_ATTEMPTS',
    'LOCKOUT_DURATION'
]