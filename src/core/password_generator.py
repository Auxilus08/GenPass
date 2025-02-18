import random
import string
import re

class PasswordGenerator:
    SYMBOLS = "!@#$%^&*(),.?\":{}|<>"

    @staticmethod
    def generate_password(length, strength_choice):
        if not isinstance(length, int) or length <= 0 or length > 128:
            raise ValueError("Length must be between 1 and 128")
        if strength_choice not in [1, 2, 3, 4]:
            raise ValueError("Invalid strength choice")

        password = []
        lowercase = string.ascii_lowercase
        uppercase = string.ascii_uppercase
        digits = string.digits
        
        # Add required characters based on strength
        if strength_choice >= 1:
            password.append(random.choice(lowercase))
        if strength_choice >= 2:
            password.append(random.choice(uppercase))
        if strength_choice >= 3:
            password.append(random.choice(digits))
        if strength_choice == 4:
            password.append(random.choice(PasswordGenerator.SYMBOLS))

        # Build available character set
        available_chars = lowercase
        if strength_choice >= 2:
            available_chars += uppercase
        if strength_choice >= 3:
            available_chars += digits
        if strength_choice == 4:
            available_chars += PasswordGenerator.SYMBOLS

        # Fill remaining length
        while len(password) < length:
            password.append(random.choice(available_chars))

        random.shuffle(password)
        final_password = ''.join(password)

        if not PasswordGenerator._validate_password_requirements(final_password, strength_choice):
            return PasswordGenerator.generate_password(length, strength_choice)

        return final_password

    @staticmethod
    def _validate_password_requirements(password, strength_choice):
        has_lower = bool(re.search(r'[a-z]', password))
        has_upper = bool(re.search(r'[A-Z]', password))
        has_digit = bool(re.search(r'\d', password))
        has_symbol = bool(re.search(r'[!@#$%^&*(),.?":{}|<>]', password))

        if strength_choice >= 1 and not has_lower:
            return False
        if strength_choice >= 2 and not (has_lower and has_upper):
            return False
        if strength_choice >= 3 and not (has_lower and has_upper and has_digit):
            return False
        if strength_choice >= 4 and not (has_lower and has_upper and has_digit and has_symbol):
            return False

        return True