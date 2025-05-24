"""
State manager for tracking repository information between runs.
"""
import json
import os
import logging
from typing import Dict, List, Set, Any
from datetime import datetime

logger = logging.getLogger(__name__)

class StateManager:
    """Manages persistent state for repository tracking."""
    
    def __init__(self, state_file_path: str):
        """
        Initialize state manager with path to state file.
        
        Args:
            state_file_path: Path to the JSON file for state persistence
        """
        self.state_file_path = state_file_path
        self.state = self._load_state()
    
    def _load_state(self) -> Dict[str, Any]:
        """
        Load state from file or create default if not exists.
        
        Returns:
            Dictionary containing application state
        """
        if os.path.exists(self.state_file_path):
            try:
                with open(self.state_file_path, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                logger.error(f"Error loading state file: {str(e)}. Creating new state.")
                return self._create_default_state()
        else:
            return self._create_default_state()
    
    def _create_default_state(self) -> Dict[str, Any]:
        """
        Create default state structure.
        
        Returns:
            Default state dictionary
        """
        default_state = {
            "last_check": "",
            "repositories": {}
        }
        self._save_state(default_state)
        return default_state
    
    def _save_state(self, state: Dict[str, Any] = None) -> None:
        """
        Save state to file.
        
        Args:
            state: State dictionary to save (uses self.state if None)
        """
        if state is None:
            state = self.state
            
        try:
            with open(self.state_file_path, 'w') as f:
                json.dump(state, f, indent=4)
        except IOError as e:
            logger.error(f"Error saving state file: {str(e)}")
    
    def get_known_repositories(self, username: str) -> Set[int]:
        """
        Get set of known repository IDs for a user.
        
        Args:
            username: GitHub username to query
            
        Returns:
            Set of known repository IDs
        """
        if username not in self.state["repositories"]:
            return set()
        
        return {int(repo_id) for repo_id in self.state["repositories"][username].keys()}
    
    def update_repositories(self, username: str, repositories: List[Dict]) -> None:
        """
        Update stored repositories for a user.
        
        Args:
            username: GitHub username
            repositories: List of repository data dictionaries
        """
        if username not in self.state["repositories"]:
            self.state["repositories"][username] = {}
        
        for repo in repositories:
            repo_id = str(repo["id"])
            self.state["repositories"][username][repo_id] = repo
        
        self._save_state()
    
    def detect_new_repositories(self, username: str, current_repos: List[Dict]) -> List[Dict]:
        """
        Detect new repositories by comparing current repos with stored state.
        
        Args:
            username: GitHub username
            current_repos: Current list of repository data dictionaries
            
        Returns:
            List of new repository data dictionaries
        """
        known_repo_ids = self.get_known_repositories(username)
        new_repos = []
        
        for repo in current_repos:
            if repo["id"] not in known_repo_ids:
                new_repos.append(repo)
        
        return new_repos
    
    def update_last_check_time(self) -> None:
        """Update the timestamp of the last repository check."""
        self.state["last_check"] = datetime.now().isoformat()
        self._save_state()
    
    def get_last_check_time(self) -> str:
        """
        Get the timestamp of the last repository check.
        
        Returns:
            ISO format timestamp string or empty string if never checked
        """
        return self.state.get("last_check", "")
