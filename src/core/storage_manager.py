from cryptography.fernet import Fernet
import json
import os
from datetime import datetime
import base64

class StorageManager:
    def __init__(self):
        self.data_dir = os.path.join("data")
        os.makedirs(self.data_dir, exist_ok=True)
        self.key = self._load_or_create_key()
        self.cipher_suite = Fernet(self.key)

    def _generate_key(self):
        return Fernet.generate_key()

    def _load_key(self):
        key_file = os.path.join("data", "secret.key")
        try:
            if os.path.exists(key_file):
                with open(key_file, "rb") as f:
                    return f.read()
            
            key = self._generate_key()
            os.makedirs(os.path.dirname(key_file), exist_ok=True)
            with open(key_file, "wb") as f:
                f.write(key)
            return key
        except Exception as e:
            raise Exception(f"Failed to load encryption key: {str(e)}")

    def encrypt_password(self, password):
        try:
            return self.cipher_suite.encrypt(password.encode()).decode()
        except Exception as e:
            raise Exception(f"Encryption failed: {str(e)}")

    def decrypt_password(self, encrypted_password):
        try:
            return self.cipher_suite.decrypt(encrypted_password.encode()).decode()
        except Exception as e:
            raise Exception(f"Decryption failed: {str(e)}")

    def save_password(self, username, site, password):
        """Save encrypted password for a user"""
        try:
            filename = os.path.join(self.data_dir, f"{username}_passwords.json")
            data = self._load_data(filename)
            
            # Encrypt the password
            encrypted_password = self.cipher_suite.encrypt(password.encode()).decode()
            
            # Update or add new entry
            entry_found = False
            for entry in data:
                if entry["site"] == site:
                    entry["password"] = encrypted_password
                    entry_found = True
                    break
                    
            if not entry_found:
                data.append({
                    "site": site,
                    "password": encrypted_password
                })
            
            # Save updated data
            with open(filename, "w") as f:
                json.dump(data, f, indent=4)
                
        except Exception as e:
            raise Exception(f"Failed to save password: {str(e)}")

    def get_password(self, username, site):
        """Retrieve decrypted password for a user and site"""
        try:
            filename = os.path.join(self.data_dir, f"{username}_passwords.json")
            if not os.path.exists(filename):
                return None
                
            data = self._load_data(filename)
            
            for entry in data:
                if entry["site"] == site:
                    # Decrypt the password
                    encrypted = entry["password"].encode()
                    decrypted = self.cipher_suite.decrypt(encrypted)
                    return decrypted.decode()
                    
            return None
            
        except Exception as e:
            raise Exception(f"Failed to retrieve password: {str(e)}")

    def get_all_passwords(self, username):
        """Get all password entries for a user (without decrypted passwords)"""
        try:
            filename = os.path.join(self.data_dir, f"{username}_passwords.json")
            return self._load_data(filename)
        except Exception as e:
            raise Exception(f"Failed to retrieve passwords: {str(e)}")

    def delete_password(self, username, site):
        """Delete a password entry"""
        try:
            filename = os.path.join(self.data_dir, f"{username}_passwords.json")
            data = self._load_data(filename)
            
            data = [entry for entry in data if entry["site"] != site]
            
            with open(filename, "w") as f:
                json.dump(data, f, indent=4)
                
        except Exception as e:
            raise Exception(f"Failed to delete password: {str(e)}")

    def _load_data(self, filename):
        """Load data from file or return empty list"""
        try:
            if os.path.exists(filename):
                with open(filename, "r") as f:
                    return json.load(f)
            return []
        except Exception as e:
            raise Exception(f"Failed to load data: {str(e)}")

    def _load_or_create_key(self):
        """Load existing encryption key or create new one"""
        key_file = os.path.join(self.data_dir, "encryption.key")
        try:
            if os.path.exists(key_file):
                with open(key_file, "rb") as f:
                    return base64.urlsafe_b64decode(f.read())
            else:
                key = Fernet.generate_key()
                with open(key_file, "wb") as f:
                    f.write(base64.urlsafe_b64encode(key))
                return key
        except Exception as e:
            raise Exception(f"Failed to handle encryption key: {str(e)}")

    def close(self):
        """Clean up resources"""
        try:
            # Close any open file handles
            pass
        except Exception as e:
            print(f"Error closing storage manager: {str(e)}")