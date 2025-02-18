import os
import json
from typing import Dict, Any

class Config:
    def __init__(self):
        self.config_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'config')
        self.data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data')
        self.ensure_directories()

    def ensure_directories(self):
        """Ensure necessary directories exist"""
        os.makedirs(self.config_dir, exist_ok=True)
        os.makedirs(self.data_dir, exist_ok=True)

    def load_email_config(self) -> Dict[str, Any]:
        """Load email configuration"""
        config_path = os.path.join(self.config_dir, 'email_config.json')
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
                self._validate_email_config(config)
                return config
        except FileNotFoundError:
            default_config = self._get_default_email_config()
            self.save_email_config(default_config)
            return default_config
        except json.JSONDecodeError:
            raise ValueError("Invalid email configuration format")

    def save_email_config(self, config: Dict[str, Any]):
        """Save email configuration"""
        self._validate_email_config(config)
        config_path = os.path.join(self.config_dir, 'email_config.json')
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=4)

    def _validate_email_config(self, config: Dict[str, Any]):
        """Validate email configuration"""
        required_fields = ['smtp_server', 'smtp_port', 'sender_email', 'sender_password']
        if not all(field in config for field in required_fields):
            raise ValueError("Missing required fields in email config")
        
        if not isinstance(config['smtp_port'], int):
            raise ValueError("SMTP port must be an integer")
        
        if not isinstance(config['smtp_server'], str):
            raise ValueError("SMTP server must be a string")
        
        if not isinstance(config['sender_email'], str):
            raise ValueError("Sender email must be a string")
        
        if not isinstance(config['sender_password'], str):
            raise ValueError("Sender password must be a string")

    def _get_default_email_config(self) -> Dict[str, Any]:
        """Get default email configuration"""
        return {
            "smtp_server": "smtp.gmail.com",
            "smtp_port": 587,
            "sender_email": "",
            "sender_password": ""
        }

    def get_data_file_path(self, filename: str) -> str:
        """Get full path for a data file"""
        return os.path.join(self.data_dir, filename)

    def get_config_file_path(self, filename: str) -> str:
        """Get full path for a config file"""
        return os.path.join(self.config_dir, filename)

# Create global instance
config = Config()