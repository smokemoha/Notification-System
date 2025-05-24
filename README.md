# GitHub Repository Notification System - Setup Guide

## Overview

This application monitors specified GitHub users for new repository creation and sends email notifications to your Gmail account when new repositories are detected. The system is designed as a simple Python script that can be run manually or scheduled to run periodically.

## Features

- Monitor multiple GitHub users for new repository creation
- Send customized email notifications via Gmail
- Track repository state between runs to detect only new repositories
- Configurable check intervals and notification templates
- Detailed logging for monitoring and troubleshooting

## Requirements

- Python 3.6 or higher
- Internet connection to access GitHub API
- Gmail account for sending notifications
- (Optional) GitHub Personal Access Token for higher API rate limits

## Installation

1. **Clone or download the application files** to your local machine.

2. **Install required Python packages**:
   ```
   pip install requests
   ```

3. **Configure the application** by editing the `config.json` file (see Configuration section below).

## Configuration

Before running the application, you need to configure it by editing the `config.json` file:

### GitHub Configuration

```json
"github": {
    "users_to_monitor": [
        "smokemoha",
        "belfarz",
        "WatersE-Cadaniti",
        "manny-uncharted"
    ],
    "check_interval_minutes": 60,
    "api_token": ""  // Optional for public repos
}
```

- `users_to_monitor`: List of GitHub usernames to monitor for new repositories
- `check_interval_minutes`: How often to check for new repositories (in minutes)
- `api_token`: (Optional) GitHub Personal Access Token for higher API rate limits

### Email Configuration

```json
"email": {
    "enabled": true,
    "smtp_server": "smtp.gmail.com",
    "smtp_port": 587,
    "sender_email": "your.email@gmail.com",
    "sender_password": "your-app-password",
    "recipient_email": "recipient@example.com",
    "subject_template": "New GitHub Repository Alert: {repo_name}",
    "body_template": "..."
}
```

- `enabled`: Set to `true` to enable email notifications, `false` to disable
- `smtp_server` and `smtp_port`: Gmail SMTP server settings (default values should work)
- `sender_email`: Your Gmail address that will send notifications
- `sender_password`: Your Gmail app password (see Gmail App Password section below)
- `recipient_email`: Email address to receive notifications (can be the same as sender)
- `subject_template` and `body_template`: Templates for notification emails

### Gmail App Password

For security reasons, Gmail requires an "App Password" instead of your regular password:

1. Go to your Google Account settings: https://myaccount.google.com/
2. Select "Security" from the left menu
3. Under "Signing in to Google," select "2-Step Verification" (enable if not already)
4. At the bottom, select "App passwords"
5. Generate a new app password for "Mail" and "Other (Custom name)"
6. Use this generated password in the configuration file

## Usage

### Running Manually

To run the application once:

```
python src/main.py --once
```

### Running on Schedule

To run the application continuously based on the configured check interval:

```
python src/main.py
```

### Running as a Background Service

#### On Linux/Mac (using cron):

1. Edit your crontab:
   ```
   crontab -e
   ```

2. Add a line to run the script every hour (adjust path as needed):
   ```
   0 * * * * cd /path/to/github_notification_app && python src/main.py --once
   ```

#### On Windows (using Task Scheduler):

1. Open Task Scheduler
2. Create a new Basic Task
3. Set the trigger to run on a schedule (e.g., hourly)
4. Set the action to start a program: `python`
5. Add arguments: `src/main.py --once`
6. Set the start in directory to your application folder

## Customization

### Notification Templates

You can customize the email notification templates in the `config.json` file:

- `subject_template`: Template for email subject line
- `body_template`: HTML template for email body

Available template variables:
- `{username}`: GitHub username who created the repository
- `{repo_name}`: Name of the new repository
- `{repo_description}`: Repository description
- `{repo_url}`: URL to the repository
- `{created_date}`: Date the repository was created

### Logging

Logging settings can be adjusted in the `config.json` file:

```json
"logging": {
    "level": "INFO",
    "file_path": "notification_app.log"
}
```

- `level`: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- `file_path`: Path to log file

## Troubleshooting

### Common Issues

1. **No notifications received**:
   - Check if email configuration is correct
   - Verify Gmail app password is valid
   - Check if any repositories were actually created since last run
   - Review log file for errors

2. **GitHub API rate limit exceeded**:
   - Add a GitHub Personal Access Token to increase rate limits
   - Reduce check frequency

3. **Script not running on schedule**:
   - Check system scheduler configuration
   - Verify script has correct permissions
   - Check log file for execution errors

### Logs

Check the log file (default: `notification_app.log`) for detailed information about the application's operation and any errors that may have occurred.

## Future Enhancements

- Web interface for configuration management
- Support for monitoring organizations and teams
- Additional notification channels (SMS, push notifications)
- Cloud deployment options

## Support

For issues or questions, please refer to the documentation or contact the developer.

---

Happy monitoring!
