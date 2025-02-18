import sys
import logging
import tkinter as tk
from tkinter import messagebox
from src.ui.login_window import LoginWindow
from src.utils.config import config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('genpass.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

def setup_exception_handler():
    def handle_exception(exc_type, exc_value, exc_traceback):
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return

        logger.error("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))
        
        # Show error message to user if GUI is running
        try:
            messagebox.showerror("Error", f"An unexpected error occurred: {str(exc_value)}")
        except:
            pass

    sys.excepthook = handle_exception

def check_dependencies():
    try:
        import cryptography
        import pyotp
        import pyperclip
    except ImportError as e:
        logger.error(f"Missing dependency: {str(e)}")
        messagebox.showerror(
            "Error", 
            "Missing required dependencies. Please run: pip install -r requirements.txt"
        )
        sys.exit(1)

def initialize_app():
    try:
        # Ensure all necessary directories and configurations exist
        config.ensure_directories()
        
        # Create the root window
        root = tk.Tk()
        root.withdraw()  # Hide the root window
        
        # Set application icon (if available)
        try:
            root.iconbitmap('assets/icon.ico')
        except:
            pass
        
        # Set window attributes
        root.title("GenPass")
        
        # Create and show login window
        app = LoginWindow()
        return root, app
    
    except Exception as e:
        logger.error(f"Failed to initialize application: {str(e)}")
        messagebox.showerror("Error", f"Failed to initialize application: {str(e)}")
        sys.exit(1)

def main():
    try:
        # Setup exception handler
        setup_exception_handler()
        
        # Check required dependencies
        check_dependencies()
        
        # Initialize application
        root, app = initialize_app()
        
        # Start the application
        logger.info("Starting GenPass application")
        app.run()
        
    except Exception as e:
        logger.error(f"Application failed to start: {str(e)}")
        messagebox.showerror("Error", f"Application failed to start: {str(e)}")
        sys.exit(1)
    
    finally:
        # Cleanup
        try:
            root.destroy()
        except:
            pass
        
        logger.info("Application shutdown complete")

if __name__ == "__main__":
    main()