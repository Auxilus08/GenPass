"""
User interface components and window management.
"""
from src.ui.theme_manager import ThemeManager
from src.ui.login_window import LoginWindow
from src.ui.main_window import MainWindow

# Default theme settings
DEFAULT_THEME = 'light'
WINDOW_SIZES = {
    'login': '400x500',
    'main': '800x600'
}

__all__ = [
    'ThemeManager',
    'LoginWindow',
    'MainWindow',
    'DEFAULT_THEME',
    'WINDOW_SIZES'
]