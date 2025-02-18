import sqlite3
import hashlib
import json
import os
from datetime import datetime
import re
import secrets
from .two_factor import TwoFactorAuth
import logging

class Auth:
    def __init__(self):
        self.db_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data")
        os.makedirs(self.db_dir, exist_ok=True)
        self.db_path = os.path.join(self.db_dir, "users.db")
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()
        self._create_tables()

    def _create_tables(self):
        """Create necessary database tables if they don't exist"""
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                username TEXT PRIMARY KEY,
                password TEXT NOT NULL,
                email TEXT NOT NULL,
                two_factor_enabled INTEGER DEFAULT 0
            )
        ''')
        self.conn.commit()

    def register(self, username, password, email):
        """Register a new user"""
        try:
            # Check if username already exists
            if self.get_user(username):
                return False, "Username already exists"

            # Hash the password
            hashed_password = self._hash_password(password)

            # Store user data
            query = "INSERT INTO users (username, password, email) VALUES (?, ?, ?)"
            self.cursor.execute(query, (username, hashed_password, email))
            self.conn.commit()
            return True, "Registration successful"

        except Exception as e:
            print(f"Registration error: {str(e)}")
            return False, f"Registration failed: {str(e)}"

    def login(self, username, password):
        """Authenticate a user"""
        try:
            user = self.get_user(username)
            if not user:
                return False, "Invalid username or password"

            hashed_password = self._hash_password(password)
            if hashed_password != user[1]:  # Compare with stored hash
                return False, "Invalid username or password"

            return True, "Login successful"

        except Exception as e:
            print(f"Login error: {str(e)}")
            return False, f"Login failed: {str(e)}"

    def get_user(self, username):
        """Retrieve user data"""
        query = "SELECT * FROM users WHERE username = ?"
        self.cursor.execute(query, (username,))
        return self.cursor.fetchone()

    def get_user_email(self, username):
        """Get user's email address"""
        query = "SELECT email FROM users WHERE username = ?"
        self.cursor.execute(query, (username,))
        result = self.cursor.fetchone()
        return result[0] if result else None

    def is_2fa_enabled(self, username):
        """Check if 2FA is enabled for user"""
        query = "SELECT two_factor_enabled FROM users WHERE username = ?"
        self.cursor.execute(query, (username,))
        result = self.cursor.fetchone()
        return bool(result[0]) if result else False

    def enable_2fa(self, username):
        """Enable 2FA for user"""
        query = "UPDATE users SET two_factor_enabled = 1 WHERE username = ?"
        self.cursor.execute(query, (username,))
        self.conn.commit()

    def disable_2fa(self, username):
        """Disable 2FA for user"""
        query = "UPDATE users SET two_factor_enabled = 0 WHERE username = ?"
        self.cursor.execute(query, (username,))
        self.conn.commit()

    def _hash_password(self, password):
        """Hash password using SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()

    def close(self):
        """Clean up resources"""
        try:
            if hasattr(self, 'conn'):
                self.conn.close()
        except Exception as e:
            print(f"Error closing auth manager: {str(e)}")

class UserAuth:
    def __init__(self):
        self.data_dir = os.path.join("data")
        os.makedirs(self.data_dir, exist_ok=True)
        self.filename = os.path.join(self.data_dir, "users.json")
        self.pepper = self._load_or_create_pepper()

    def _load_or_create_pepper(self):
        pepper_file = os.path.join(self.data_dir, "pepper.key")
        try:
            if os.path.exists(pepper_file):
                with open(pepper_file, "rb") as f:
                    return f.read()
            
            pepper = secrets.token_bytes(32)
            with open(pepper_file, "wb") as f:
                f.write(pepper)
            return pepper
        except Exception as e:
            raise Exception(f"Failed to load/create pepper: {str(e)}")

    def _hash_password(self, password):
        salt = secrets.token_hex(16)
        peppered = password.encode() + self.pepper
        hashed = hashlib.sha256(peppered + salt.encode()).hexdigest()
        return f"{salt}${hashed}"

    def _verify_password(self, password, stored_hash):
        try:
            if '$' not in stored_hash:
                peppered = password.encode() + self.pepper
                return hashlib.sha256(peppered).hexdigest() == stored_hash
            
            salt, hash_value = stored_hash.split('$')
            peppered = password.encode() + self.pepper
            return hashlib.sha256(peppered + salt.encode()).hexdigest() == hash_value
        except Exception as e:
            raise Exception(f"Password verification failed: {str(e)}")

    def _validate_email(self, email):
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None

    def _validate_username(self, username):
        if not 3 <= len(username) <= 30:
            return False
        return bool(re.match(r'^[a-zA-Z0-9_-]+$', username))

    def is_2fa_enabled(self, username):
        """Check if 2FA is enabled for a user"""
        try:
            if not os.path.exists(self.filename):
                return False

            with open(self.filename, "r") as f:
                data = json.load(f)
                for user in data:
                    if user["username"] == username:
                        return user.get("two_factor_enabled", False)
            return False
        except Exception as e:
            raise Exception(f"Failed to check 2FA status: {str(e)}")

    def enable_2fa(self, username):
        """Enable 2FA for a user"""
        try:
            if not os.path.exists(self.filename):
                return False

            with open(self.filename, "r") as f:
                data = json.load(f)
                
            for user in data:
                if user["username"] == username:
                    user["two_factor_enabled"] = True
                    with open(self.filename, "w") as f:
                        json.dump(data, f, indent=4)
                    return True
            return False
        except Exception as e:
            raise Exception(f"Failed to enable 2FA: {str(e)}")

    def disable_2fa(self, username):
        """Disable 2FA for a user"""
        try:
            if not os.path.exists(self.filename):
                return False

            with open(self.filename, "r") as f:
                data = json.load(f)
                
            for user in data:
                if user["username"] == username:
                    user["two_factor_enabled"] = False
                    with open(self.filename, "w") as f:
                        json.dump(data, f, indent=4)
                    return True
            return False
        except Exception as e:
            raise Exception(f"Failed to disable 2FA: {str(e)}")

    def save_user_credentials(self, username, password, email=""):
        """Save user credentials with 2FA status"""
        if not self._validate_username(username):
            raise ValueError("Invalid username format")
        if not email or not self._validate_email(email):
            raise ValueError("Invalid email format")

        try:
            data = []
            if os.path.exists(self.filename):
                with open(self.filename, "r") as f:
                    data = json.load(f)

            # Check if username already exists (case-insensitive comparison)
            if any(user["username"].lower() == username.lower() for user in data):
                raise ValueError("Username already exists")

            entry = {
                "username": username,
                "password": self._hash_password(password),
                "email": email.lower(),  # Store email in lowercase
                "two_factor_enabled": False,  # Default 2FA status
                "created_at": datetime.now().isoformat(),
                "last_login": None
            }

            data.append(entry)
            with open(self.filename, "w") as f:
                json.dump(data, f, indent=4)

        except Exception as e:
            raise Exception(f"Failed to save user credentials: {str(e)}")

    def verify_user(self, username, password):
        """Verify user credentials"""
        try:
            if not os.path.exists(self.filename):
                return False

            with open(self.filename, "r") as f:
                data = json.load(f)
                for user in data:
                    if user["username"] == username:
                        if self._verify_password(password, user["password"]):
                            # Update last login time
                            user["last_login"] = datetime.now().isoformat()
                            with open(self.filename, "w") as f:
                                json.dump(data, f, indent=4)
                            return True
            return False

        except Exception as e:
            raise Exception(f"Failed to verify user: {str(e)}")

    def get_user_email(self, username):
        if not os.path.exists(self.filename):
            return None

        with open(self.filename, "r") as f:
            data = json.load(f)
            for user in data:
                if user["username"] == username:
                    return user.get("email", None)
        return None

    def is_username_taken(self, username):
        if not os.path.exists(self.filename):
            return False

        with open(self.filename, "r") as f:
            data = json.load(f)
            return any(user["username"] == username for user in data)
    
            
    def close(self):
        """Clean up resources"""
        try:
            # Close any open connections
            pass
        except Exception as e:
            print(f"Error closing auth manager: {str(e)}") 