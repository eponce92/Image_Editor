import json
from pathlib import Path
from app.config import SETTINGS_FILE

class SettingsManager:
    @staticmethod
    def load_settings():
        try:
            with open(SETTINGS_FILE, 'r') as f:
                return json.load(f)
        except:
            return {"fal_api_key": ""}  # Changed to single API key

    @staticmethod
    def save_settings(settings):
        with open(SETTINGS_FILE, 'w') as f:
            json.dump(settings, f)
