"""
Email notification service for GitHub repository alerts.
"""
import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, List, Any

logger = logging.getLogger(__name__)

class EmailService:
    """Service for sending email notifications."""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize email service with configuration.
        
        Args:
            config: Email configuration dictionary
        """
        self.config = config
        self.enabled = config.get("enabled", False)
        self.smtp_server = config.get("smtp_server", "smtp.gmail.com")
        self.smtp_port = config.get("smtp_port", 587)
        self.sender_email = config.get("sender_email", "")
        self.sender_password = config.get("sender_password", "")
        self.recipient_email = config.get("recipient_email", "")
        self.subject_template = config.get("subject_template", "New GitHub Repository Alert: {repo_name}")
        self.body_template = config.get("body_template", "")
    
    def is_properly_configured(self) -> bool:
        """
        Check if email service is properly configured.
        
        Returns:
            Boolean indicating if configuration is complete
        """
        return (
            self.enabled and
            self.smtp_server and
            self.smtp_port and
            self.sender_email and
            self.sender_password and
            self.recipient_email
        )
    
    def send_new_repo_notification(self, repo_data: Dict[str, Any]) -> bool:
        """
        Send notification email for a new repository.
        
        Args:
            repo_data: Repository data dictionary
            
        Returns:
            Boolean indicating success or failure
        """
        if not self.is_properly_configured():
            logger.warning("Email service not properly configured. Skipping notification.")
            return False
        
        try:
            # Format subject and body using repository data
            subject = self.subject_template.format(
                repo_name=repo_data.get("name", "Unknown Repository")
            )
            
            # Format the body with repository information
            body = self.body_template.format(
                username=repo_data.get("owner", "Unknown User"),
                repo_name=repo_data.get("name", "Unknown Repository"),
                repo_description=repo_data.get("description", "No description available"),
                repo_url=repo_data.get("url", "#"),
                created_date=repo_data.get("created_at", "Unknown date")
            )
            
            # Create message
            message = MIMEMultipart("alternative")
            message["Subject"] = subject
            message["From"] = self.sender_email
            message["To"] = self.recipient_email
            
            # Attach HTML content
            html_part = MIMEText(body, "html")
            message.attach(html_part)
            
            # Connect to server and send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.sender_email, self.sender_password)
                server.sendmail(
                    self.sender_email,
                    self.recipient_email,
                    message.as_string()
                )
            
            logger.info(f"Notification email sent for repository: {repo_data.get('name')}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email notification: {str(e)}")
            return False
    
    def send_batch_notification(self, repos_by_user: Dict[str, List[Dict]]) -> Dict[str, int]:
        """
        Send notifications for multiple new repositories grouped by user.
        
        Args:
            repos_by_user: Dictionary mapping usernames to lists of new repository data
            
        Returns:
            Dictionary with counts of successful and failed notifications
        """
        results = {
            "success": 0,
            "failure": 0
        }
        
        for username, repos in repos_by_user.items():
            for repo in repos:
                success = self.send_new_repo_notification(repo)
                if success:
                    results["success"] += 1
                else:
                    results["failure"] += 1
        
        return results
