import pyotp
import smtplib
from email.mime.text import MIMEText
import json
import os
from datetime import datetime, timedelta
import re
import random
from email.mime.multipart import MIMEMultipart
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class TwoFactorAuth:
    def __init__(self):
        # Create config directory if it doesn't exist
        self.config_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "config")
        os.makedirs(self.config_dir, exist_ok=True)
        
        # Initialize email config
        self.email_config = self._load_or_create_email_config()
        self.secret_key = pyotp.random_base32()
        self.totp = pyotp.TOTP(self.secret_key, interval=300)  # 5-minute window
        self.last_otp_time = None
        self.max_attempts = 3
        self.attempt_count = 0
        self.lockout_until = None
        self.verification_codes = {}
        logger.debug("TwoFactorAuth initialized")

    def _load_or_create_email_config(self):
        """Load or create email configuration"""
        config_file = os.path.join(self.config_dir, "email_config.json")
        default_config = {
            "smtp_server": "smtp.gmail.com",
            "smtp_port": 587,
            "sender_email": "your-email@gmail.com",
            "sender_password": "your-app-password"
        }
        
        if not os.path.exists(config_file):
            with open(config_file, 'w') as f:
                json.dump(default_config, f, indent=4)
            logger.info(f"Created default email config at {config_file}")
            
        with open(config_file, 'r') as f:
            config = json.load(f)
            logger.debug("Email configuration loaded successfully")
            return config

    def generate_otp(self):
        if self.last_otp_time and datetime.now() - self.last_otp_time < timedelta(minutes=1):
            raise Exception("Please wait 1 minute before requesting another OTP")
        
        self.last_otp_time = datetime.now()
        return self.totp.now()

    def verify_otp(self, otp):
        """Verify OTP with improved comparison"""
        if self.lockout_until and datetime.now() < self.lockout_until:
            raise Exception(f"Account locked. Try again after {self.lockout_until}")

        if self.attempt_count >= self.max_attempts:
            self.lockout_until = datetime.now() + timedelta(minutes=15)
            self.attempt_count = 0
            raise Exception("Too many failed attempts. Account locked for 15 minutes")

        try:
            # Convert OTP to string and strip whitespace
            entered_otp = str(otp).strip()
            
            # Get current valid OTP
            current_otp = str(self.totp.now()).zfill(6)  # Ensure 6 digits with leading zeros
            
            # Log for debugging
            logger.debug(f"Comparing OTP - Entered: {entered_otp}, Current: {current_otp}")
            
            # Compare exact strings
            if entered_otp == current_otp:
                self.attempt_count = 0
                return True
                
            # Also check the previous window to account for delay
            previous_otp = str(self.totp.at(datetime.now() - timedelta(seconds=30))).zfill(6)
            if entered_otp == previous_otp:
                self.attempt_count = 0
                return True
                
            self.attempt_count += 1
            return False
            
        except Exception as e:
            logger.error(f"OTP verification error: {str(e)}")
            self.attempt_count += 1
            return False

    def send_otp_email(self, user_email):
        if not self._validate_email(user_email):
            raise ValueError("Invalid email address")

        try:
            otp = self.generate_otp()
            
            html_content = f"""
            <html>
                <body>
                    <h2>GenPass Authentication Code</h2>
                    <p>Your one-time password is:</p>
                    <h1 style="color: #3f51b5;">{otp}</h1>
                    <p>This code will expire in 5 minutes.</p>
                    <p>If you didn't request this code, please ignore this email.</p>
                </body>
            </html>
            """
            
            msg = MIMEText(html_content, 'html')
            msg['Subject'] = 'GenPass Authentication Code'
            msg['From'] = self.email_config['sender_email']
            msg['To'] = user_email

            with smtplib.SMTP(self.email_config['smtp_server'], 
                            self.email_config['smtp_port']) as server:
                server.starttls()
                server.login(self.email_config['sender_email'], 
                           self.email_config['sender_password'])
                server.send_message(msg)
            return True

        except smtplib.SMTPException as e:
            raise Exception(f"SMTP error: {str(e)}")
        except Exception as e:
            raise Exception(f"Failed to send email: {str(e)}")

    def _validate_email(self, email):
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))

    def send_verification_code(self, email):
        """Send verification code to user's email"""
        try:
            # Generate a simple 6-digit code
            code = str(random.randint(100000, 999999))
            logger.debug(f"Generated code for {email}: {code}")
            
            # Store the code with email in lowercase
            self.verification_codes[email.lower()] = {
                'code': code,
                'timestamp': datetime.now()
            }
            logger.debug(f"Stored verification data: {self.verification_codes}")

            # Create email message
            msg = MIMEMultipart()
            msg['From'] = self.email_config['sender_email']
            msg['To'] = email
            msg['Subject'] = "GenPass - 2FA Verification Code"

            body = f"""
            Your verification code for GenPass 2FA setup is: {code}
            
            This code will expire in 5 minutes.
            If you did not request this code, please ignore this email.
            """
            msg.attach(MIMEText(body, 'plain'))

            # Send email
            with smtplib.SMTP(self.email_config['smtp_server'], 587) as server:
                server.starttls()
                server.login(self.email_config['sender_email'], 
                           self.email_config['sender_password'])
                server.send_message(msg)
                logger.debug("Verification email sent successfully")

            return code

        except Exception as e:
            logger.error(f"Failed to send verification code: {str(e)}")
            raise

    def verify_code(self, email, entered_code):
        """Verify the provided code"""
        try:
            logger.debug(f"Verifying code for {email}. Entered code: {entered_code}")
            logger.debug(f"Current verification_codes: {self.verification_codes}")
            
            # Convert email to lowercase for consistent lookup
            email = email.lower()
            
            if email not in self.verification_codes:
                logger.debug(f"No stored code found for email: {email}")
                return False

            stored_data = self.verification_codes[email]
            stored_code = stored_data['code']
            timestamp = stored_data['timestamp']

            # Check if code is expired (5 minutes)
            if datetime.now() - timestamp > timedelta(minutes=5):
                logger.debug("Code expired")
                del self.verification_codes[email]
                return False

            # Compare codes as strings after stripping whitespace
            result = str(entered_code).strip() == str(stored_code).strip()
            logger.debug(f"Code comparison result: {result}")
            
            if result:
                del self.verification_codes[email]
                
            return result

        except Exception as e:
            logger.error(f"Error during code verification: {str(e)}")
            return False

    def cleanup_expired_codes(self):
        """Clean up expired verification codes"""
        try:
            current_time = datetime.now()
            expired_emails = []

            for email, data in self.verification_codes.items():
                if current_time - data['timestamp'] > timedelta(minutes=5):
                    expired_emails.append(email)

            for email in expired_emails:
                del self.verification_codes[email]

        except Exception as e:
            raise Exception(f"Failed to cleanup expired codes: {str(e)}")

    def cleanup(self):
        """Clean up resources and expired codes"""
        try:
            # Clean up expired verification codes
            current_time = datetime.now()
            expired_emails = []

            for email, data in self.verification_codes.items():
                if current_time - data['timestamp'] > timedelta(minutes=5):
                    expired_emails.append(email)

            for email in expired_emails:
                del self.verification_codes[email]
                
        except Exception as e:
            print(f"Error during 2FA cleanup: {str(e)}")