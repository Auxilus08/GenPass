import tkinter as tk
from tkinter import ttk, messagebox
from src.auth.user_auth import UserAuth
from src.auth.two_factor import TwoFactorAuth
from src.ui.main_window import MainWindow
from src.ui.theme_manager import ThemeManager

class LoginWindow:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("GenPass - Login")
        self.root.geometry("400x500")
        
        self.auth = UserAuth()
        self.two_factor = TwoFactorAuth()
        self.is_dark_mode = False
        self.setup_ui()

    def setup_ui(self):
        self.apply_theme()
        
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Login Frame
        self.login_frame = self.create_login_frame(main_frame)
        self.login_frame.pack(fill=tk.BOTH, expand=True)

        # Register Frame (initially hidden)
        self.register_frame = self.create_register_frame(main_frame)

        # 2FA Frame (initially hidden)
        self.two_factor_frame = self.create_two_factor_frame(main_frame)

        # Theme toggle button
        theme_btn = tk.Button(
            self.root,
            text="Toggle Theme",
            command=self.toggle_theme,
            **ThemeManager.get_button_style(self.is_dark_mode)
        )
        theme_btn.pack(side=tk.BOTTOM, pady=10)

    def create_login_frame(self, parent):
        frame = ttk.LabelFrame(parent, text="Login")

        ttk.Label(frame, text="Username:").pack(pady=5)
        self.login_username = ttk.Entry(frame)
        self.login_username.pack(pady=5)

        ttk.Label(frame, text="Password:").pack(pady=5)
        self.login_password = ttk.Entry(frame, show="*")
        self.login_password.pack(pady=5)

        login_btn = tk.Button(
            frame,
            text="Login",
            command=self.handle_login,
            **ThemeManager.get_button_style(self.is_dark_mode)
        )
        login_btn.pack(pady=10)

        register_link = tk.Button(
            frame,
            text="Don't have an account? Register",
            command=self.show_register,
            **ThemeManager.get_button_style(self.is_dark_mode)
        )
        register_link.pack(pady=5)

        return frame

    def create_register_frame(self, parent):
        frame = ttk.LabelFrame(parent, text="Register")

        ttk.Label(frame, text="Username:").pack(pady=5)
        self.reg_username = ttk.Entry(frame)
        self.reg_username.pack(pady=5)

        ttk.Label(frame, text="Email:").pack(pady=5)
        self.reg_email = ttk.Entry(frame)
        self.reg_email.pack(pady=5)

        ttk.Label(frame, text="Password:").pack(pady=5)
        self.reg_password = ttk.Entry(frame, show="*")
        self.reg_password.pack(pady=5)

        ttk.Label(frame, text="Confirm Password:").pack(pady=5)
        self.reg_confirm = ttk.Entry(frame, show="*")
        self.reg_confirm.pack(pady=5)

        register_btn = tk.Button(
            frame,
            text="Register",
            command=self.handle_register,
            **ThemeManager.get_button_style(self.is_dark_mode)
        )
        register_btn.pack(pady=10)

        login_link = tk.Button(
            frame,
            text="Already have an account? Login",
            command=self.show_login,
            **ThemeManager.get_button_style(self.is_dark_mode)
        )
        login_link.pack(pady=5)

        return frame

    def create_two_factor_frame(self, parent):
        frame = ttk.LabelFrame(parent, text="Two-Factor Authentication")

        ttk.Label(frame, text="Enter the code sent to your email:").pack(pady=5)
        self.otp_entry = ttk.Entry(frame)
        self.otp_entry.pack(pady=5)

        verify_btn = tk.Button(
            frame,
            text="Verify",
            command=self.verify_otp,
            **ThemeManager.get_button_style(self.is_dark_mode)
        )
        verify_btn.pack(pady=10)

        resend_btn = tk.Button(
            frame,
            text="Resend Code",
            command=self.resend_otp,
            **ThemeManager.get_button_style(self.is_dark_mode)
        )
        resend_btn.pack(pady=5)

        return frame

    def handle_login(self):
        username = self.login_username.get()
        password = self.login_password.get()

        try:
            if self.auth.verify_user(username, password):
                if self.auth.is_2fa_enabled(username):
                    self.current_user = username
                    self.send_otp()
                    self.show_two_factor()
                else:
                    self.login_success(username)
            else:
                messagebox.showerror("Error", "Invalid username or password")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def handle_register(self):
        username = self.reg_username.get()
        email = self.reg_email.get()
        password = self.reg_password.get()
        confirm = self.reg_confirm.get()

        if password != confirm:
            messagebox.showerror("Error", "Passwords do not match")
            return

        try:
            self.auth.save_user_credentials(username, password, email)
            messagebox.showinfo("Success", "Registration successful!")
            self.show_login()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def send_otp(self):
        try:
            email = self.auth.get_user_email(self.current_user)
            self.two_factor.send_otp_email(email)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to send OTP: {str(e)}")

    def verify_otp(self):
        """Verify OTP code"""
        otp = self.otp_entry.get().strip()
        try:
            if self.two_factor.verify_otp(otp):
                self.login_success(self.current_user)
            else:
                messagebox.showerror("Error", "Invalid OTP")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def resend_otp(self):
        self.send_otp()
        messagebox.showinfo("Success", "New OTP sent to your email")

    def show_login(self):
        self.register_frame.pack_forget()
        self.two_factor_frame.pack_forget()
        self.login_frame.pack(fill=tk.BOTH, expand=True)

    def show_register(self):
        self.login_frame.pack_forget()
        self.two_factor_frame.pack_forget()
        self.register_frame.pack(fill=tk.BOTH, expand=True)

    def show_two_factor(self):
        self.login_frame.pack_forget()
        self.register_frame.pack_forget()
        self.two_factor_frame.pack(fill=tk.BOTH, expand=True)

    def login_success(self, username):
        self.root.destroy()
        root = tk.Tk()
        main_window = MainWindow(root)
        main_window.username = username
        main_window.run()

    def toggle_theme(self):
        self.is_dark_mode = not self.is_dark_mode
        self.apply_theme()

    def apply_theme(self):
        theme = ThemeManager.get_theme(self.is_dark_mode)
        self.root.configure(bg=theme['bg'])
        
        style = ttk.Style()
        style.configure("TLabel", background=theme['bg'], foreground=theme['fg'])
        style.configure("TFrame", background=theme['bg'])
        style.configure("TLabelframe", background=theme['bg'])
        style.configure("TLabelframe.Label", background=theme['bg'], foreground=theme['fg'])
        style.configure("TEntry", fieldbackground=theme['entry_bg'], foreground=theme['entry_fg'])

    def run(self):
        self.root.mainloop()