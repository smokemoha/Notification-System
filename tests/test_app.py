"""
Test script for GitHub Repository Notification System.
"""
import os
import sys
import json
import logging
from datetime import datetime

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.config import Config
from src.github_client import GitHubClient
from src.state_manager import StateManager
from src.email_service import EmailService
from src.main import NotificationApp

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger("test_script")

def test_github_api():
    """Test GitHub API client functionality."""
    logger.info("Testing GitHub API client...")
    
    # Initialize client without token (for public repos)
    client = GitHubClient()
    
    # Test users to check
    test_users = ["smokemoha", "belfarz", "WatersE-Cadaniti", "manny-uncharted"]
    
    # Test getting repositories for each user
    for username in test_users:
        logger.info(f"Testing repository retrieval for user: {username}")
        repos = client.get_user_repositories(username)
        
        if repos:
            logger.info(f"✓ Successfully retrieved {len(repos)} repositories for {username}")
            # Print first repository details as sample
            if repos:
                sample_repo = repos[0]
                logger.info(f"  Sample repo: {sample_repo['name']} ({sample_repo['url']})")
        else:
            logger.warning(f"⚠ No repositories found for {username} or user doesn't exist")
    
    # Test rate limit check
    rate_limit = client.check_rate_limit()
    if "error" not in rate_limit:
        logger.info(f"✓ Rate limit check successful")
        if "resources" in rate_limit and "core" in rate_limit["resources"]:
            core = rate_limit["resources"]["core"]
            logger.info(f"  Remaining requests: {core.get('remaining', 'unknown')}/{core.get('limit', 'unknown')}")
    else:
        logger.error(f"✗ Rate limit check failed: {rate_limit['error']}")
    
    logger.info("GitHub API client test completed")

def test_state_manager():
    """Test state manager functionality."""
    logger.info("Testing state manager...")
    
    # Create temporary state file for testing
    test_state_file = "test_state.json"
    
    # Initialize state manager
    state_manager = StateManager(test_state_file)
    
    # Test repository tracking
    test_username = "test_user"
    test_repos = [
        {
            "id": 12345,
            "name": "test-repo-1",
            "full_name": "test_user/test-repo-1",
            "description": "Test repository 1",
            "url": "https://github.com/test_user/test-repo-1",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "owner": test_username
        },
        {
            "id": 67890,
            "name": "test-repo-2",
            "full_name": "test_user/test-repo-2",
            "description": "Test repository 2",
            "url": "https://github.com/test_user/test-repo-2",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "owner": test_username
        }
    ]
    
    # Update repositories
    state_manager.update_repositories(test_username, test_repos)
    logger.info(f"✓ Updated repositories for {test_username}")
    
    # Check known repositories
    known_repos = state_manager.get_known_repositories(test_username)
    if len(known_repos) == 2 and 12345 in known_repos and 67890 in known_repos:
        logger.info(f"✓ Successfully retrieved known repositories")
    else:
        logger.error(f"✗ Failed to retrieve correct known repositories")
    
    # Test new repository detection
    new_repo = {
        "id": 11111,
        "name": "test-repo-3",
        "full_name": "test_user/test-repo-3",
        "description": "Test repository 3",
        "url": "https://github.com/test_user/test-repo-3",
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
        "owner": test_username
    }
    
    # Add new repository to test list
    test_repos_with_new = test_repos + [new_repo]
    
    # Detect new repositories
    new_repos = state_manager.detect_new_repositories(test_username, test_repos_with_new)
    if len(new_repos) == 1 and new_repos[0]["id"] == 11111:
        logger.info(f"✓ Successfully detected new repository")
    else:
        logger.error(f"✗ Failed to detect new repository correctly")
    
    # Test last check time
    state_manager.update_last_check_time()
    last_check = state_manager.get_last_check_time()
    if last_check:
        logger.info(f"✓ Successfully updated and retrieved last check time: {last_check}")
    else:
        logger.error(f"✗ Failed to update or retrieve last check time")
    
    # Clean up test file
    try:
        os.remove(test_state_file)
        logger.info(f"✓ Cleaned up test state file")
    except:
        logger.warning(f"⚠ Could not clean up test state file")
    
    logger.info("State manager test completed")

def test_email_configuration():
    """Test email configuration validation."""
    logger.info("Testing email configuration validation...")
    
    # Test with incomplete configuration
    incomplete_config = {
        "enabled": True,
        "smtp_server": "smtp.gmail.com",
        "smtp_port": 587,
        # Missing credentials
    }
    
    email_service = EmailService(incomplete_config)
    if not email_service.is_properly_configured():
        logger.info("✓ Correctly identified incomplete configuration")
    else:
        logger.error("✗ Failed to identify incomplete configuration")
    
    # Test with complete configuration
    complete_config = {
        "enabled": True,
        "smtp_server": "smtp.gmail.com",
        "smtp_port": 587,
        "sender_email": "test@example.com",
        "sender_password": "password123",
        "recipient_email": "recipient@example.com"
    }
    
    email_service = EmailService(complete_config)
    if email_service.is_properly_configured():
        logger.info("✓ Correctly identified complete configuration")
    else:
        logger.error("✗ Failed to identify complete configuration")
    
    logger.info("Email configuration test completed")

def run_tests():
    """Run all tests."""
    logger.info("Starting tests for GitHub Repository Notification System")
    
    test_github_api()
    print("\n" + "-" * 50 + "\n")
    
    test_state_manager()
    print("\n" + "-" * 50 + "\n")
    
    test_email_configuration()
    print("\n" + "-" * 50 + "\n")
    
    logger.info("All tests completed")

if __name__ == "__main__":
    run_tests()
