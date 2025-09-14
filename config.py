import json
import os
from typing import Any, Dict

class ExamConfig:
    """Configuration management for the Online Exam System."""
    
    def __init__(self, config_file: str = 'config.json'):
        self.config_file = config_file
        self.load_config()
    
    def load_config(self):
        """Load configuration from file."""
        default_config = {
            'exam_duration': 600,  # 10 minutes in seconds
            'questions_per_exam': 10,
            'passing_percentage': 60,
            'allow_review': True,
            'randomize_questions': True,
            'theme': 'light',
            'database_path': 'exam_system.db',
            'auto_save_answers': True,
            'show_timer_warning': True,
            'timer_warning_minutes': 2,
            'categories': ['General', 'Mathematics', 'Science', 'Programming', 'Geography', 'History'],
            'difficulty_levels': ['Easy', 'Medium', 'Hard'],
            'points_per_question': {
                'Easy': 1,
                'Medium': 2,
                'Hard': 3
            },
            'ui_settings': {
                'window_width': 900,
                'window_height': 700,
                'font_family': 'Arial',
                'font_size_normal': 12,
                'font_size_heading': 18,
                'font_size_title': 24
            }
        }
        
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    loaded_config = json.load(f)
                    self.config = {**default_config, **loaded_config}
            except (json.JSONDecodeError, FileNotFoundError):
                self.config = default_config
        else:
            self.config = default_config
            self.save_config()
    
    def save_config(self):
        """Save current configuration to file."""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            print(f"Error saving config: {e}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value."""
        keys = key.split('.')
        value = self.config
        
        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default
    
    def set(self, key: str, value: Any):
        """Set configuration value."""
        keys = key.split('.')
        config = self.config
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value
        self.save_config()
    
    def update(self, updates: Dict[str, Any]):
        """Update multiple configuration values."""
        for key, value in updates.items():
            self.set(key, value)
