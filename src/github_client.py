"""
GitHub API client for repository monitoring.
"""
import requests
import logging
from typing import Dict, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class GitHubClient:
    """Client for interacting with GitHub API to monitor repositories."""
    
    BASE_URL = "https://api.github.com"
    
    def __init__(self, token: str = ""):
        """Initialize GitHub client with optional authentication token."""
        self.token = token
        self.headers = {
            "Accept": "application/vnd.github.v3+json"
        }
        if token:
            self.headers["Authorization"] = f"token {token}"
    
    def get_user_repositories(self, username: str) -> List[Dict]:
        """
        Get repositories for a specific GitHub user.
        
        Args:
            username: GitHub username to query
            
        Returns:
            List of repository data dictionaries
            
        Raises:
            Exception: If API request fails
        """
        url = f"{self.BASE_URL}/users/{username}/repos"
        params = {
            "sort": "created",
            "direction": "desc",
            "per_page": 100  # Maximum allowed by GitHub API
        }
        
        try:
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            
            repos = response.json()
            logger.info(f"Retrieved {len(repos)} repositories for user {username}")
            
            # Extract relevant information for each repository
            processed_repos = []
            for repo in repos:
                processed_repos.append({
                    "id": repo["id"],
                    "name": repo["name"],
                    "full_name": repo["full_name"],
                    "description": repo["description"] or "",
                    "url": repo["html_url"],
                    "created_at": repo["created_at"],
                    "updated_at": repo["updated_at"],
                    "owner": username
                })
            
            return processed_repos
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching repositories for {username}: {str(e)}")
            if hasattr(e.response, 'status_code') and e.response.status_code == 404:
                logger.warning(f"User {username} not found")
                return []
            elif hasattr(e.response, 'status_code') and e.response.status_code == 403:
                logger.warning("Rate limit exceeded. Consider using a GitHub token.")
                return []
            raise Exception(f"GitHub API error: {str(e)}")
    
    def get_repositories_for_users(self, usernames: List[str]) -> Dict[str, List[Dict]]:
        """
        Get repositories for multiple GitHub users.
        
        Args:
            usernames: List of GitHub usernames to query
            
        Returns:
            Dictionary mapping usernames to their repository lists
        """
        all_repos = {}
        
        for username in usernames:
            try:
                repos = self.get_user_repositories(username)
                all_repos[username] = repos
            except Exception as e:
                logger.error(f"Failed to get repositories for {username}: {str(e)}")
                all_repos[username] = []
        
        return all_repos
    
    def check_rate_limit(self) -> Dict:
        """
        Check GitHub API rate limit status.
        
        Returns:
            Dictionary with rate limit information
        """
        url = f"{self.BASE_URL}/rate_limit"
        
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error checking rate limit: {str(e)}")
            return {"error": str(e)}
