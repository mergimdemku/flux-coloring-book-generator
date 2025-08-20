"""
Application configuration and constants
"""

from pathlib import Path
from typing import Dict, Any
import json

class AppConfig:
    """Central configuration manager"""
    
    def __init__(self):
        self.app_dir = Path.home() / "ColoringBookGenerator"
        self.books_dir = self.app_dir / "Books"
        self.temp_dir = self.app_dir / "Temp"
        self.config_file = self.app_dir / "config.json"
        
        # Ensure directories exist
        self.books_dir.mkdir(parents=True, exist_ok=True)
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        
        # Load configuration
        self.settings = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file"""
        default_config = {
            "image_settings": {
                "width": 2480,
                "height": 3508,
                "dpi": 300,
                "format": "PNG"
            },
            "pdf_settings": {
                "page_size": "A4",
                "margin_mm": 15,
                "include_metadata": True
            },
            "generation_settings": {
                "model_name": "flux-schnell",
                "guidance_scale": 7.5,
                "num_inference_steps": 4,
                "seed": None
            },
            "branding": {
                "company": "3D Gravity Kids",
                "subtitle": "Kopshti Magjik",
                "website": "kopshtimagjik.com"
            }
        }
        
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                # Merge with defaults
                for key, value in default_config.items():
                    if key not in config:
                        config[key] = value
                return config
            except Exception as e:
                print(f"Error loading config: {e}")
                return default_config
        
        return default_config
    
    def save_config(self):
        """Save current configuration to file"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.settings, f, indent=2)
        except Exception as e:
            print(f"Error saving config: {e}")
    
    def get(self, key: str, default=None):
        """Get configuration value"""
        keys = key.split('.')
        value = self.settings
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        return value
    
    def set(self, key: str, value):
        """Set configuration value"""
        keys = key.split('.')
        config = self.settings
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        config[keys[-1]] = value
        self.save_config()