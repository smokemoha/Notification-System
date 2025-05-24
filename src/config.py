"""
Configuration management for GitHub Repository Notification System.
"""
import json
import os
from typing import Dict, List, Any


class Config:
    """Configuration manager for the application."""
    
    DEFAULT_CONFIG = {
        "github": {
            "users_to_monitor": [
                "smokemoha",
                "belfarz",
                "WatersE-Cadaniti",
                "manny-uncharted"
            ],
            "check_interval_minutes": 60,
            "api_token": ""  # Optional for public repos
        },
        "email": {
            "enabled": True,
            "smtp_server": "smtp.gmail.com",
            "smtp_port": 587,
            "sender_email": "",
            "sender_password": "",  # App password for Gmail
            "recipient_email": "",
            "subject_template": "New GitHub Repository Alert: {repo_name}",
            "body_template": """
            <html>
            <body>
            <h2>New GitHub Repository Created</h2>
            <p>User <b>{username}</b> has created a new repository:</p>
            <h3>{repo_name}</h3>
            <p>{repo_description}</p>
            <p>View it here: <a href="{repo_url}">{repo_url}</a></p>
            <p>Created on: {created_date}</p>
            </body>
            </html>
            """
        },
        "state": {
            "file_path": "repo_state.json"
        },
        "logging": {
            "level": "INFO",
            "file_path": "notification_app.log"
        }
    }
    
    def __init__(self, config_path: str = "config.json"):
        """Initialize configuration from file or defaults."""
        self.config_path = config_path
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file or create default if not exists."""
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                print(f"Error loading config: {e}. Using defaults.")
                return self._create_default_config()
        else:
            return self._create_default_config()
    
    def _create_default_config(self) -> Dict[str, Any]:
        """Create and save default configuration."""
        with open(self.config_path, 'w') as f:
            json.dump(self.DEFAULT_CONFIG, f, indent=4)
        return self.DEFAULT_CONFIG
    
    def save(self) -> None:
        """Save current configuration to file."""
        with open(self.config_path, 'w') as f:
            json.dump(self.config, f, indent=4)
    
    def get_github_users(self) -> List[str]:
        """Get list of GitHub users to monitor."""
        return self.config["github"]["users_to_monitor"]
    
    def get_github_token(self) -> str:
        """Get GitHub API token if configured."""
        return self.config["github"].get("api_token", "")
    
    def get_check_interval(self) -> int:
        """Get check interval in minutes."""
        return self.config["github"]["check_interval_minutes"]
    
    def get_state_file_path(self) -> str:
        """Get path to state file."""
        return self.config["state"]["file_path"]
    
    def get_email_config(self) -> Dict[str, Any]:
        """Get email configuration."""
        return self.config["email"]
    
    def is_email_enabled(self) -> bool:
        """Check if email notifications are enabled."""
        return self.config["email"]["enabled"]
    
    def get_logging_config(self) -> Dict[str, str]:
        """Get logging configuration."""
        return self.config["logging"]
