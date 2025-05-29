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
        """Determines the path to the INI file in the user's local folder"""
        if os.name == 'nt':  # Windows
            # %LOCALAPPDATA%\app_name\config.ini
            local_app_data = os.environ.get('LOCALAPPDATA', Path.home() / 'AppData' / 'Local')
            config_dir = Path(local_app_data) / self.app_name
        else:  # Linux/macOS
            # ~/.local/share/app_name/config.ini
            config_dir = Path.home() / '.local' / 'share' / self.app_name

        # Create directory if it does not exist
        config_dir.mkdir(parents=True, exist_ok=True)
        return config_dir / 'config.ini'

    def _load_config(self):
        """Loads the configuration from the INI file"""
        if self.config_file.exists():
            try:
                self.config.read(self.config_file, encoding='utf-8')
            except Exception as e:
                print(f"Error loading config: {e}")
                self._create_default_config()
        else:
            self._create_default_config()

    def _create_default_config(self):
        """Creates a default configuration"""
        self.config['THEME'] = {
            'current_theme': 'nightbee'
        }
        self._save_config()

    def _save_config(self):
        """Saves the configuration to an INI file"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                self.config.write(f)
            return True
        except Exception as e:
            print(f"Error saving config: {e}")
            return False

    def get_theme(self) -> str:
        """Gets the current theme"""
        return self.config.get('THEME', 'current_theme', fallback='nightbee')

    def set_theme(self, theme: str) -> bool:
        """Saves the selected theme"""
        if 'THEME' not in self.config:
            self.config.add_section('THEME')

        self.config.set('THEME', 'current_theme', theme)
        return self._save_config()


# Example usage
if __name__ == "__main__":
    config = ConfigManager("honeycomb")

    print(f"Config is saved to: {config.config_file}")
    print(f"Current theme: {config.get_theme()}")

    # Change theme
    config.set_theme("cyberhive")
    print(f"New theme: {config.get_theme()}")

