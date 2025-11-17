import json
import os
from pathlib import Path

class Config:
    def __init__(self):
        self.config_dir = Path.home() / '.yt_downloader'
        self.config_file = self.config_dir / 'config.json'
        self.history_file = self.config_dir / 'history.json'
        self.config_dir.mkdir(exist_ok=True)
        
        self.default_config = {
            'download_path': str(Path.home() / 'Downloads' / 'YouTube'),
            'quality': 'best',
            'max_concurrent': 3,
            'auto_retry': True,
            'max_retries': 3,
            'download_subtitles': False,
            'embed_thumbnail': True,
            'format_preference': 'mp4'
        }
        
        self.settings = self.load_config()
    
    def load_config(self):
        if self.config_file.exists():
            with open(self.config_file, 'r') as f:
                return {**self.default_config, **json.load(f)}
        return self.default_config.copy()
    
    def save_config(self):
        with open(self.config_file, 'w') as f:
            json.dump(self.settings, f, indent=2)
    
    def get(self, key):
        return self.settings.get(key)
    
    def set(self, key, value):
        self.settings[key] = value
        self.save_config()
    
    def load_history(self):
        if self.history_file.exists():
            with open(self.history_file, 'r') as f:
                return json.load(f)
        return []
    
    def save_history(self, history):
        with open(self.history_file, 'w') as f:
            json.dump(history, f, indent=2)
