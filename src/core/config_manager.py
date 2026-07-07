import json
import os
from src.core.logger import logger

CONFIG_FILE = "config/settings.json"

class ConfigManager:
    def __init__(self):
        self.config = {
            "gemini_api_key": "",
            "template_path": "assets/blank_template.docx",
            "output_directory": "output/",
            "theme": "System"
        }
        self.load_config()

    def load_config(self):
        if not os.path.exists("config"):
            os.makedirs("config")
            
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r") as f:
                    loaded = json.load(f)
                    self.config.update(loaded)
                logger.info("Configuration loaded successfully.")
            except Exception as e:
                logger.error(f"Failed to load config: {e}")
        else:
            self.save_config()

    def save_config(self):
        try:
            with open(CONFIG_FILE, "w") as f:
                json.dump(self.config, f, indent=4)
            logger.info("Configuration saved.")
        except Exception as e:
            logger.error(f"Failed to save config: {e}")

    def get(self, key):
        return self.config.get(key)

    def set(self, key, value):
        self.config[key] = value
        self.save_config()