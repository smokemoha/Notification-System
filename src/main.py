
"""
Main controller for GitHub Repository Notification System.
"""
import logging
import time
import sys
import os

# Add the project root directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from typing import Dict, List, Any

from src.config import Config
from src.github_client import GitHubClient
from src.state_manager import StateManager
from src.email_service import EmailService

# Set up logging
def setup_logging(config):
    """Configure logging based on configuration."""
    log_level = getattr(logging, config.get("level", "INFO"))
    log_file = config.get("file_path", "notification_app.log")
    
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(sys.stdout)
        ]
    )

class NotificationApp:
    """Main application controller."""
    
    def __init__(self, config_path: str = "config.json"):
        """
        Initialize the notification application.
        
        Args:
            config_path: Path to configuration file
        """
        # Load configuration
        self.config = Config(config_path)
        
        # Set up logging
        setup_logging(self.config.get_logging_config())
        self.logger = logging.getLogger(__name__)
        
        # Initialize components
        self.github_client = GitHubClient(self.config.get_github_token())
        self.state_manager = StateManager(self.config.get_state_file_path())
        self.email_service = EmailService(self.config.get_email_config())
        
        self.logger.info("Notification application initialized")
    
    def check_for_new_repositories(self) -> Dict[str, List[Dict]]:
        """
        Check for new repositories for all monitored users.
        
        Returns:
            Dictionary mapping usernames to lists of new repository data
        """
        users_to_monitor = self.config.get_github_users()
        self.logger.info(f"Checking for new repositories for users: {', '.join(users_to_monitor)}")
        
        new_repos_by_user = {}
        
        # Get current repositories for all users
        all_repos = self.github_client.get_repositories_for_users(users_to_monitor)
        
        # Process each user's repositories
        for username, repos in all_repos.items():
            # Detect new repositories
            new_repos = self.state_manager.detect_new_repositories(username, repos)
            
            if new_repos:
                self.logger.info(f"Found {len(new_repos)} new repositories for user {username}")
                new_repos_by_user[username] = new_repos
            else:
                self.logger.info(f"No new repositories found for user {username}")
            
            # Update state with current repositories
            self.state_manager.update_repositories(username, repos)
        
        # Update last check time
        self.state_manager.update_last_check_time()
        
        return new_repos_by_user
    
    def send_notifications(self, new_repos_by_user: Dict[str, List[Dict]]) -> Dict[str, int]:
        """
        Send notifications for new repositories.
        
        Args:
            new_repos_by_user: Dictionary mapping usernames to lists of new repository data
            
        Returns:
            Dictionary with counts of successful and failed notifications
        """
        if not new_repos_by_user:
            self.logger.info("No new repositories to notify about")
            return {"success": 0, "failure": 0}
        
        if not self.email_service.is_properly_configured():
            self.logger.warning("Email service not properly configured. Skipping notifications.")
            return {"success": 0, "failure": 0}
        
        self.logger.info("Sending notifications for new repositories")
        return self.email_service.send_batch_notification(new_repos_by_user)
    
    def run_once(self) -> Dict[str, Any]:
        """
        Run a single check and notification cycle.
        
        Returns:
            Dictionary with results summary
        """
        self.logger.info("Starting repository check cycle")
        
        # Check for new repositories
        new_repos_by_user = self.check_for_new_repositories()
        
        # Count total new repositories
        total_new_repos = sum(len(repos) for repos in new_repos_by_user.values())
        
        # Send notifications if new repositories found
        notification_results = {"success": 0, "failure": 0}
        if total_new_repos > 0:
            notification_results = self.send_notifications(new_repos_by_user)
        
        # Prepare results summary
        results = {
            "checked_users": len(self.config.get_github_users()),
            "new_repositories": total_new_repos,
            "notifications_sent": notification_results["success"],
            "notifications_failed": notification_results["failure"],
            "check_time": self.state_manager.get_last_check_time()
        }
        
        self.logger.info(f"Repository check cycle completed. Found {total_new_repos} new repositories.")
        return results
    
    def run_scheduled(self) -> None:
        """Run the application on a schedule based on configuration."""
        check_interval_minutes = self.config.get_check_interval()
        check_interval_seconds = check_interval_minutes * 60
        
        self.logger.info(f"Starting scheduled monitoring every {check_interval_minutes} minutes")
        
        try:
            while True:
                self.run_once()
                self.logger.info(f"Sleeping for {check_interval_minutes} minutes until next check")
                time.sleep(check_interval_seconds)
        except KeyboardInterrupt:
            self.logger.info("Monitoring stopped by user")
        except Exception as e:
            self.logger.error(f"Error in monitoring loop: {str(e)}")
            raise

def main():
    """Main entry point for the application."""
    # Get configuration path from command line argument or use default
    config_path = sys.argv[1] if len(sys.argv) > 1 else "config.json"
    
    # Initialize and run application
    app = NotificationApp(config_path)
    
    # Check if this is a one-time run or scheduled run
    if "--once" in sys.argv:
        app.run_once()
    else:
        app.run_scheduled()

if __name__ == "__main__":
    main()
