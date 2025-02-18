class ThemeManager:
    LIGHT_THEME = {
        'bg': "#f0f0f0",
        'fg': "#000000",
        'button_bg': "#3f51b5",
        'button_fg': "white",
        'entry_bg': "white",
        'entry_fg': "black",
        'error_fg': "#f44336",
        'success_fg': "#2ecc71",
        'warning_fg': "#f1c40f",
        'highlight_bg': "#e3f2fd",
        'disabled_bg': "#cccccc",
        'disabled_fg': "#666666"
    }
    
    DARK_THEME = {
        'bg': "#2c2c2c",
        'fg': "#ffffff",
        'button_bg': "#424242",
        'button_fg': "#ffffff",
        'entry_bg': "#3c3c3c",
        'entry_fg': "#ffffff",
        'error_fg': "#ff5252",
        'success_fg': "#69f0ae",
        'warning_fg': "#ffd740",
        'highlight_bg': "#3f51b5",
        'disabled_bg': "#1a1a1a",
        'disabled_fg': "#808080"
    }

    @classmethod
    def get_theme(cls, is_dark_mode=False):
        return cls.DARK_THEME if is_dark_mode else cls.LIGHT_THEME

    @classmethod
    def get_disabled_style(cls, is_dark_mode=False):
        theme = cls.get_theme(is_dark_mode)
        return {
            'background': theme['disabled_bg'],
            'foreground': theme['disabled_fg']
        }

    @classmethod
    def get_button_style(cls, is_dark_mode=False):
        theme = cls.get_theme(is_dark_mode)
        return {
            'background': theme['button_bg'],
            'foreground': theme['button_fg'],
            'activebackground': theme['highlight_bg'],
            'activeforeground': theme['button_fg'],
            'borderwidth': 0,
            'padx': 10,
            'pady': 5
        }

    @classmethod
    def get_entry_style(cls, is_dark_mode=False):
        theme = cls.get_theme(is_dark_mode)
        return {
            'background': theme['entry_bg'],
            'foreground': theme['entry_fg'],
            'insertbackground': theme['fg']
        }