# GenPass - Secure Password Manager

## Overview
GenPass is a secure, feature-rich password manager built with Python, offering both command-line and graphical user interfaces. It provides robust password generation, encrypted storage, and two-factor authentication capabilities.


## Features
- 🔐 Secure password generation with customizable complexity
- 📱 Two-factor authentication (2FA) support
- 🎨 Dark/Light theme support
- 🔒 AES-256 encryption for stored passwords
- 📧 Email-based verification
- 👥 Multi-user support
- 🖥️ Cross-platform compatibility
- 🔄 Automatic password strength assessment
- 📋 Clipboard integration for easy copying

## Installation

### Prerequisites
- Python 3.7 or higher
- pip (Python package installer)
- Operating System: Windows/macOS/Linux

### Step 1: Clone the Repository
```bash
git clone https://github.com/akshat0824/GenPass.git
cd GenPass
```

### Step 2: Create Virtual Environment (Recommended)
```bash
# Windows
python -m venv venv
.\venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Configure Email Settings
Create `config/email_config.json`:
```json
{
    "smtp_server": "smtp.gmail.com",
    "smtp_port": 587,
    "sender_email": "your-email@gmail.com",
    "sender_password": "your-app-specific-password"
}
```
Note: For Gmail, you'll need to use an App Password, not your regular password.

## Usage

### Starting the Application
```bash
python run.py
```

### First-Time Setup
1. Launch the application
2. Click "Register" to create a new account
3. Enter your details:
   - Username (3-30 characters, alphanumeric)
   - Email (valid email address)
   - Password
4. Verify your email using the OTP sent
5. Log in with your credentials

### Password Generation
1. Select desired password length (1-128 characters)
2. Choose password strength:
   - Basic (lowercase only)
   - Medium (lowercase + uppercase)
   - Strong (lowercase + uppercase + numbers)
   - Very Strong (all characters + symbols)
3. Click "Generate Password"
4. Use "Copy to Clipboard" to copy the password

### Password Storage
- Save passwords with associated website/service names
- View stored passwords in the password list
- Delete passwords when no longer needed
- All passwords are encrypted using AES-256 encryption

### Theme Customization
- Toggle between Light/Dark themes using the theme button
- Theme preference is saved between sessions

## Security Features

### Password Security
- Passwords are hashed using SHA-256
- Salt and pepper are used for additional security
- Encrypted storage using Fernet (AES-256)
- Automatic password strength assessment

### Two-Factor Authentication
- Email-based 2FA
- Time-based one-time passwords (TOTP)
- 5-minute validity window
- Rate limiting for OTP requests

### Data Protection
- All stored passwords are encrypted
- Secure key storage
- Protection against brute force attacks
- Account lockout after failed attempts


### Common Issues and Solutions

1. **Email Configuration**
   - Error: "Failed to send email"
   - Solution: Check email credentials and app password

2. **Database Access**
   - Error: "Permission denied"
   - Solution: Check file permissions in data directory

3. **Dependency Issues**
   - Error: "Module not found"
   - Solution: Verify virtual environment activation and dependencies

## Contributing
1. Fork the repository
2. Create a feature branch
3. Commit changes
4. Push to the branch
5. Create a Pull Request


## Authors
- Akshat Tiwari - Initial work - [akshat0824](https://github.com/akshat0824)

## Acknowledgments
- [Cryptography](https://cryptography.io/) for encryption
- [PyOTP](https://pyauth.github.io/pyotp/) for 2FA
- [Tkinter](https://docs.python.org/3/library/tkinter.html) for GUI

## Version History
- v2.0.0 - Added 2FA and better GUI
- v1.0.0 - Initial

## Support
For support, please open an issue in the GitHub repository or contact the maintainers.

## Roadmap
- [ ] Browser extension integration
- [ ] Cloud backup support
- [ ] Password sharing functionality
- [ ] Mobile application
- [ ] Hardware key support
