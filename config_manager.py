import configparser
import os
from pathlib import Path


class ConfigManager:
    def __init__(self, app_name: str = "honeycomb"):
        self.app_name = app_name
        self.config_file = self._get_config_path()
        self.config = configparser.ConfigParser()
        self._load_config()

    def _get_config_path(self) -> Path:
        """Determines the path to the INI file"""
        if os.name == 'nt':  # Windows
            # In the user's folder: C:\Users\Username\.honeycomb.ini
            config_path = Path.home() / f".{self.app_name}.ini"
        else:  # Linux/macOS
            # In the home folder: ~/.honeycomb.ini
            config_path = Path.home() / f".{self.app_name}.ini"

        return config_path

    def _load_config(self):
        """Loads configuration from the INI file"""
        if self.config_file.exists():
            try:
                self.config.read(self.config_file, encoding='utf-8')
                print(f"✓ Configuration loaded from: {self.config_file}")
            except Exception as e:
                print(f"⚠ Error loading config: {e}")
                self._create_default_config()
        else:
            print(f"⚠ Config not found, creating new: {self.config_file}")
            self._create_default_config()

    def _create_default_config(self):
        """Creates default configuration"""
        # Main settings
        self.config['THEME'] = {
            'current_theme': 'nightbee',
            'available_themes': 'nightbee,choosenbee,barbee,farbee,daybee,beethoven,cyberhive'
        }

        # Window settings
        self.config['WINDOW'] = {
            'last_width': '100',
            'last_height': '30',
            'maximized': 'false'
        }

        # Other settings
        self.config['GENERAL'] = {
            'show_help_on_startup': 'true',
            'last_opened_file': '',
            'auto_save': 'true'
        }

        self._save_config()

    def _save_config(self):
        """Saves configuration to the INI file"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                self.config.write(f)
            return True
        except Exception as e:
            print(f"⚠ Error saving config: {e}")
            return False

    # === METHODS FOR WORKING WITH THEMES ===

    def get_theme(self) -> str:
        """Gets the current theme"""
        return self.config.get('THEME', 'current_theme', fallback='nightbee')

    def set_theme(self, theme: str) -> bool:
        """Saves the selected theme"""
        if 'THEME' not in self.config:
            self.config.add_section('THEME')

        self.config.set('THEME', 'current_theme', theme)
        success = self._save_config()

        if success:
            print(f"✓ Theme '{theme}' saved")

        return success

    # === METHODS FOR WORKING WITH THE WINDOW ===

    def get_window_size(self) -> tuple[int, int]:
        """Gets the window size"""
        width = self.config.getint('WINDOW', 'last_width', fallback=100)
        height = self.config.getint('WINDOW', 'last_height', fallback=30)
        return width, height

    def set_window_size(self, width: int, height: int) -> bool:
        """Saves the window size"""
        if 'WINDOW' not in self.config:
            self.config.add_section('WINDOW')

        self.config.set('WINDOW', 'last_width', str(width))
        self.config.set('WINDOW', 'last_height', str(height))
        return self._save_config()

    def is_maximized(self) -> bool:
        """Checks if the window was maximized"""
        return self.config.getboolean('WINDOW', 'maximized', fallback=False)

    def set_maximized(self, maximized: bool) -> bool:
        """Saves the maximized window state"""
        if 'WINDOW' not in self.config:
            self.config.add_section('WINDOW')

        self.config.set('WINDOW', 'maximized', str(maximized).lower())
        return self._save_config()

    # === GENERAL METHODS ===

    def get_last_file(self) -> str:
        """Gets the path to the last opened file"""
        return self.config.get('GENERAL', 'last_opened_file', fallback='')

    def set_last_file(self, file_path: str) -> bool:
        """Saves the path to the last file"""
        if 'GENERAL' not in self.config:
            self.config.add_section('GENERAL')

        self.config.set('GENERAL', 'last_opened_file', file_path)
        return self._save_config()

    def show_help_on_startup(self) -> bool:
        """Whether to show help on startup"""
        return self.config.getboolean('GENERAL', 'show_help_on_startup', fallback=True)

    def set_show_help_on_startup(self, show: bool) -> bool:
        """Sets whether to show help on startup"""
        if 'GENERAL' not in self.config:
            self.config.add_section('GENERAL')

        self.config.set('GENERAL', 'show_help_on_startup', str(show).lower())
        return self._save_config()

    # === UNIVERSAL METHODS ===

    def get_setting(self, section: str, key: str, fallback: str = '') -> str:
        """Universal method for getting a setting"""
        return self.config.get(section, key, fallback=fallback)

    def set_setting(self, section: str, key: str, value: str) -> bool:
        """Universal method for saving a setting"""
        if section not in self.config:
            self.config.add_section(section)

        self.config.set(section, key, value)
        return self._save_config()

    def print_config(self):
        """Prints the current configuration (for debugging)"""
        print(f"\n=== Configuration {self.app_name} ===")
        for section_name in self.config.sections():
            print(f"[{section_name}]")
            for key, value in self.config.items(section_name):
                print(f"  {key} = {value}")
        print("=" * 40)


# === APPLICATION INTEGRATION ===

# Example usage in main.py
def example_usage():
    """Example usage of ConfigManager"""

    # Create a configuration manager
    config = ConfigManager("honeycomb")

    # Load the theme when the application starts
    saved_theme = config.get_theme()
    print(f"Loaded theme: {saved_theme}")

    # Load the window size
    width, height = config.get_window_size()
    print(f"Window size: {width}x{height}")

    # Check the last file
    last_file = config.get_last_file()
    if last_file:
        print(f"Last file: {last_file}")

    # Show the current configuration
    config.print_config()


# Modified ThemeSelectorModal for working with INI
class ThemeSelectorModal_INI:
    """Updated version with INI config support"""

    def __init__(self, config_manager: ConfigManager):
        super().__init__()
        self.config_manager = config_manager
        self.original_theme = None

    def on_mount(self) -> None:
        # Load the current theme from the config
        current_theme = self.config_manager.get_theme()
        self.original_theme = current_theme

        option_list = self.query_one(OptionList)
        option_list.focus()

        # Find and highlight the current theme
        if current_theme in self.THEMES:
            current_index = self.THEMES.index(current_theme)
            option_list.highlighted = current_index

    def on_option_list_option_selected(self, event) -> None:
        """Theme selection event with saving to INI"""
        selected_theme = event.option.prompt

        # Apply the theme
        self.app.theme = selected_theme

        # Save to the INI file
        self.config_manager.set_theme(selected_theme)

        self.app.pop_screen()

    def action_close_modal(self) -> None:
        """On cancel, restore the theme and do not save"""
        if self.original_theme:
            self.app.theme = self.original_theme
        self.app.pop_screen()


if __name__ == "__main__":
    # Test the configuration
    example_usage()

    # Test theme change
    config = ConfigManager("honeycomb")

    print(f"\nCurrent theme: {config.get_theme()}")

    # Change the theme
    config.set_theme("cyberhive")
    print(f"New theme: {config.get_theme()}")

    # Save the window size
    config.set_window_size(120, 40)
    width, height = config.get_window_size()
    print(f"Saved size: {width}x{height}")

