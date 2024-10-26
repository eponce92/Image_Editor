import json
import os
from pathlib import Path
from app.config import SETTINGS_FILE, CannySettings

class SettingsManager:
    @staticmethod
    def load_settings():
        try:
            if os.path.exists(SETTINGS_FILE):
                with open(SETTINGS_FILE, 'r') as f:
                    settings = json.load(f)
                    # Ensure all settings exist with defaults if missing
                    return {
                        "fal_api_key": settings.get("fal_api_key", ""),
                        "controlnet_type": settings.get("controlnet_type", "none"),
                        "controlnet_scale": settings.get("controlnet_scale", 0.7),
                        "auto_preprocess": settings.get("auto_preprocess", True),
                        "strength": settings.get("strength", 0.85),
                        "canny_settings": {
                            "low_threshold": settings.get("canny_settings", {}).get("low_threshold", CannySettings.DEFAULT_LOW_THRESHOLD),
                            "high_threshold": settings.get("canny_settings", {}).get("high_threshold", CannySettings.DEFAULT_HIGH_THRESHOLD),
                            "blur_size": settings.get("canny_settings", {}).get("blur_size", CannySettings.DEFAULT_BLUR_SIZE),
                            "dilate_iterations": settings.get("canny_settings", {}).get("dilate_iterations", CannySettings.DEFAULT_DILATE_ITERATIONS)
                        }
                    }
        except Exception as e:
            print(f"Error loading settings: {e}")
        
        # Default settings if file doesn't exist or error occurs
        return {
            "fal_api_key": "",
            "controlnet_type": "none",
            "controlnet_scale": 0.7,
            "auto_preprocess": True,
            "strength": 0.85,
            "canny_settings": {
                "low_threshold": CannySettings.DEFAULT_LOW_THRESHOLD,
                "high_threshold": CannySettings.DEFAULT_HIGH_THRESHOLD,
                "blur_size": CannySettings.DEFAULT_BLUR_SIZE,
                "dilate_iterations": CannySettings.DEFAULT_DILATE_ITERATIONS
            }
        }

    @staticmethod
    def save_settings(settings):
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(SETTINGS_FILE), exist_ok=True)
            with open(SETTINGS_FILE, 'w') as f:
                json.dump(settings, f, indent=4)
        except Exception as e:
            print(f"Error saving settings: {e}")
