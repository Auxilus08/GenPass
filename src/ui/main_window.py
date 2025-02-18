import tkinter as tk
from tkinter import ttk, messagebox
import pyperclip
from src.core.password_generator import PasswordGenerator
from src.core.storage_manager import StorageManager
from src.ui.theme_manager import ThemeManager
import sys
from src.auth.user_auth import UserAuth
from src.auth.two_factor import TwoFactorAuth
import logging
import os
import json

logger = logging.getLogger(__name__)

class MainWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("GenPass")
        self.username = None  # Will be set later
        self.storage = StorageManager()
        self.auth = UserAuth()
        self.two_factor = TwoFactorAuth()
        
        # Load theme preference before creating widgets
        self.load_theme_preference()
        
        # Initialize style with theme
        style = ttk.Style()
        theme_prefix = "Dark." if self.is_dark_mode else "Light."
        style.theme_use('default')  # Reset to default theme
        
        # Create and apply initial theme
        self.apply_theme()
        
        # Create widgets with themed styles
        self.setup_ui()
        self.create_menu()
        
        # Bind window close event
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def setup_ui(self):
        """Setup the main user interface"""
        # Password Generation Frame
        gen_frame = ttk.LabelFrame(self.root, text="Generate Password")
        gen_frame.pack(fill=tk.X, padx=10, pady=5)

        # Length Entry
        length_frame = ttk.Frame(gen_frame)
        length_frame.pack(fill=tk.X, padx=5, pady=5)
        
        length_label = ttk.Label(length_frame, text="Length:")
        length_label.pack(side=tk.LEFT, padx=5)
        
        self.length_var = tk.StringVar(value="12")
        self.length_entry = ttk.Entry(length_frame, textvariable=self.length_var, width=10)
        self.length_entry.pack(side=tk.LEFT, padx=5)

        # Strength Options
        strength_frame = ttk.Frame(gen_frame)
        strength_frame.pack(fill=tk.X, padx=5, pady=5)
        
        strength_label = ttk.Label(strength_frame, text="Strength:")
        strength_label.pack(side=tk.LEFT, padx=5)
        
        self.strength_var = tk.IntVar(value=3)
        
        strengths = [
            ("Basic (a-z)", 1),
            ("Medium (a-z, A-Z)", 2),
            ("Strong (a-z, A-Z, 0-9)", 3),
            ("Very Strong (a-z, A-Z, 0-9, symbols)", 4)
        ]
        
        for text, value in strengths:
            rb = ttk.Radiobutton(
                strength_frame,
                text=text,
                variable=self.strength_var,
                value=value
            )
            rb.pack(side=tk.LEFT, padx=5)

        # Generate Button
        gen_btn = ttk.Button(
            gen_frame,
            text="Generate Password",
            command=self.generate_password
        )
        gen_btn.pack(pady=10)

        # Site and Password Entry Frame
        entry_frame = ttk.LabelFrame(self.root, text="Save Password")
        entry_frame.pack(fill=tk.X, padx=10, pady=5)

        # Site Entry
        site_label = ttk.Label(entry_frame, text="Site:")
        site_label.pack(pady=5)
        self.site_entry = ttk.Entry(entry_frame)
        self.site_entry.pack(pady=5)

        # Password Entry
        pass_label = ttk.Label(entry_frame, text="Password:")
        pass_label.pack(pady=5)
        self.password_entry = ttk.Entry(entry_frame)
        self.password_entry.pack(pady=5)

        # Save Button
        save_btn = ttk.Button(
            entry_frame,
            text="Save Password",
            command=self.save_password
        )
        save_btn.pack(pady=10)

        # Saved Passwords Frame
        saved_frame = ttk.LabelFrame(self.root, text="Saved Passwords")
        saved_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Create Treeview
        self.password_tree = ttk.Treeview(
            saved_frame,
            columns=("site", "password"),
            show="headings"
        )
        self.password_tree.heading("site", text="Site")
        self.password_tree.heading("password", text="Password")
        self.password_tree.pack(fill=tk.BOTH, expand=True, pady=5)

        # Buttons Frame
        button_frame = ttk.Frame(saved_frame)
        button_frame.pack(fill=tk.X, pady=5)

        copy_btn = ttk.Button(
            button_frame,
            text="Copy Password",
            command=self.copy_password
        )
        copy_btn.pack(side=tk.LEFT, padx=5)

        delete_btn = ttk.Button(
            button_frame,
            text="Delete Password",
            command=self.delete_password
        )
        delete_btn.pack(side=tk.LEFT, padx=5)

    def generate_password(self):
        """Generate a password based on selected criteria"""
        try:
            length = int(self.length_var.get())
            strength = self.strength_var.get()
            
            password = PasswordGenerator.generate_password(length, strength)
            self.password_entry.delete(0, tk.END)
            self.password_entry.insert(0, password)
            
        except ValueError as e:
            messagebox.showerror("Error", str(e))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate password: {str(e)}")

    def save_password(self):
        """Save password entry"""
        site = self.site_entry.get()
        password = self.password_entry.get()

        if not site or not password:
            messagebox.showerror("Error", "Please enter both site and password")
            return

        try:
            self.storage.save_password(self.username, site, password)
            self.password_entry.delete(0, tk.END)
            self.site_entry.delete(0, tk.END)
            self.update_password_list()
            messagebox.showinfo("Success", "Password saved successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save password: {str(e)}")

    def copy_password(self):
        """Copy selected password to clipboard"""
        selection = self.password_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a password to copy")
            return

        try:
            site = self.password_tree.item(selection[0])['values'][0]
            password = self.storage.get_password(self.username, site)
            if password:
                pyperclip.copy(password)
                messagebox.showinfo("Success", "Password copied to clipboard!")
            else:
                messagebox.showerror("Error", "Failed to retrieve password")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to copy password: {str(e)}")

    def delete_password(self):
        """Delete selected password"""
        selection = self.password_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a password to delete")
            return

        if messagebox.askyesno("Confirm", "Are you sure you want to delete this password?"):
            try:
                site = self.password_tree.item(selection[0])['values'][0]
                self.storage.delete_password(self.username, site)
                self.update_password_list()
                messagebox.showinfo("Success", "Password deleted successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete password: {str(e)}")

    def update_password_list(self):
        """Update the password list display"""
        for item in self.password_tree.get_children():
            self.password_tree.delete(item)
            
        try:
            passwords = self.storage.get_all_passwords(self.username)
            for entry in passwords:
                self.password_tree.insert('', 'end', values=(entry['site'], '*' * 12))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update password list: {str(e)}")

    def run(self):
        """Start the application"""
        self.update_password_list()
        self.root.mainloop()

    def on_closing(self):
        """Handle window closing"""
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            self.save_theme_preference()
            self.root.destroy()

    def load_theme_preference(self):
        """Load theme preference from file"""
        try:
            config_file = os.path.join("config", "theme_preference.json")
            if os.path.exists(config_file):
                with open(config_file, 'r') as f:
                    data = json.load(f)
                    self.is_dark_mode = data.get('dark_mode', False)
            else:
                self.is_dark_mode = False
        except Exception as e:
            print(f"Error loading theme preference: {str(e)}")
            self.is_dark_mode = False

    def save_theme_preference(self):
        """Save theme preference to file"""
        try:
            os.makedirs("config", exist_ok=True)
            config_file = os.path.join("config", "theme_preference.json")
            with open(config_file, 'w') as f:
                json.dump({'dark_mode': self.is_dark_mode}, f)
        except Exception as e:
            print(f"Error saving theme preference: {str(e)}")

    def toggle_theme(self):
        """Toggle between light and dark theme"""
        self.is_dark_mode = not self.is_dark_mode
        self.apply_theme()

    def apply_theme(self):
        """Apply the current theme"""
        theme = ThemeManager.get_theme(self.is_dark_mode)
        
        style = ttk.Style()
        style.configure("TLabel", background=theme['bg'], foreground=theme['fg'])
        style.configure("TFrame", background=theme['bg'])
        style.configure("TLabelframe", background=theme['bg'])
        style.configure("TLabelframe.Label", background=theme['bg'], foreground=theme['fg'])
        style.configure("TEntry", fieldbackground=theme['entry_bg'], foreground=theme['entry_fg'])
        style.configure("TButton", background=theme['button_bg'], foreground=theme['button_fg'])
        
        self.root.configure(bg=theme['bg'])

    def create_menu(self):
        """Create the menu bar"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        # File Menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Exit", command=self.on_closing)

        # Settings Menu
        settings_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Settings", menu=settings_menu)
        settings_menu.add_command(label="2FA Settings", command=self.show_2fa_settings)
        settings_menu.add_command(label="Toggle Theme", command=self.toggle_theme)

    def show_2fa_settings(self):
        """Show 2FA settings dialog"""
        try:
            dialog = tk.Toplevel(self.root)
            dialog.title("2FA Settings")
            dialog.geometry("300x150")
            dialog.resizable(False, False)
            
            # Center the dialog
            dialog.transient(self.root)
            dialog.grab_set()
            
            # Apply theme
            theme = ThemeManager.get_theme(self.is_dark_mode)
            dialog.configure(bg=theme['bg'])
            
            # Create content
            frame = ttk.Frame(dialog)
            frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
            
            is_enabled = self.auth.is_2fa_enabled(self.username)
            status_text = "2FA is currently " + ("enabled" if is_enabled else "disabled")
            
            ttk.Label(frame, text=status_text).pack(pady=10)
            
            button_text = "Disable 2FA" if is_enabled else "Enable 2FA"
            ttk.Button(
                frame,
                text=button_text,
                command=lambda: self.toggle_2fa(dialog, is_enabled)
            ).pack(pady=10)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open 2FA settings: {str(e)}")

    def toggle_2fa(self, dialog, currently_enabled):
        """Toggle 2FA status"""
        try:
            if currently_enabled:
                self.auth.disable_2fa(self.username)
                messagebox.showinfo("Success", "2FA has been disabled")
            else:
                self.auth.enable_2fa(self.username)
                messagebox.showinfo("Success", "2FA has been enabled")
            dialog.destroy()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to toggle 2FA: {str(e)}")