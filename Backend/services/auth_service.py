"""
Authentication service for user login and registration.

Provides secure user authentication with password hashing.
"""

import os
import json
import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Optional, Dict


class AuthService:
    """Service for user authentication and session management."""
    
    def __init__(self, users_file: str = 'data/users.json'):
        """
        Initialize auth service.
        
        Args:
            users_file: Path to users database file
        """
        self.users_file = users_file
        self._ensure_users_file()
    
    def _ensure_users_file(self):
        """Ensure users file exists."""
        os.makedirs(os.path.dirname(self.users_file), exist_ok=True)
        if not os.path.exists(self.users_file):
            with open(self.users_file, 'w') as f:
                json.dump({'users': {}}, f)
    
    def _load_users(self) -> Dict:
        """Load users from file."""
        try:
            with open(self.users_file, 'r') as f:
                return json.load(f)
        except:
            return {'users': {}}
    
    def _save_users(self, data: Dict):
        """Save users to file."""
        with open(self.users_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def _hash_password(self, password: str, salt: str = None) -> tuple:
        """
        Hash password with salt.
        
        Args:
            password: Plain text password
            salt: Optional salt (generated if not provided)
        
        Returns:
            Tuple of (hashed_password, salt)
        """
        if salt is None:
            salt = secrets.token_hex(32)
        
        hashed = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt.encode('utf-8'),
            100000
        )
        
        return hashed.hex(), salt
    
    def register(self, username: str, email: str, password: str) -> Dict:
        """
        Register a new user.
        
        Args:
            username: Username
            email: Email address
            password: Plain text password
        
        Returns:
            Dict with success status and message
        """
        # Validate input
        if not username or len(username) < 3:
            return {
                'success': False,
                'error': 'Username must be at least 3 characters'
            }
        
        if not email or '@' not in email:
            return {
                'success': False,
                'error': 'Invalid email address'
            }
        
        if not password or len(password) < 6:
            return {
                'success': False,
                'error': 'Password must be at least 6 characters'
            }
        
        # Load users
        data = self._load_users()
        users = data['users']
        
        # Check if username exists
        if username in users:
            return {
                'success': False,
                'error': 'Username already exists'
            }
        
        # Check if email exists
        for user_data in users.values():
            if user_data.get('email') == email:
                return {
                    'success': False,
                    'error': 'Email already registered'
                }
        
        # Hash password
        hashed_password, salt = self._hash_password(password)
        
        # Create user
        users[username] = {
            'email': email,
            'password': hashed_password,
            'salt': salt,
            'created_at': datetime.now().isoformat(),
            'favorites': []
        }
        
        # Save
        self._save_users(data)
        
        return {
            'success': True,
            'message': 'Registration successful',
            'username': username
        }
    
    def login(self, username: str, password: str) -> Dict:
        """
        Login user.
        
        Args:
            username: Username
            password: Plain text password
        
        Returns:
            Dict with success status and user data
        """
        # Load users
        data = self._load_users()
        users = data['users']
        
        # Check if user exists
        if username not in users:
            return {
                'success': False,
                'error': 'Invalid username or password'
            }
        
        user = users[username]
        
        # Verify password
        hashed_password, _ = self._hash_password(password, user['salt'])
        
        if hashed_password != user['password']:
            return {
                'success': False,
                'error': 'Invalid username or password'
            }
        
        # Generate session token
        session_token = secrets.token_urlsafe(32)
        
        # Update last login
        user['last_login'] = datetime.now().isoformat()
        user['session_token'] = session_token
        self._save_users(data)
        
        return {
            'success': True,
            'message': 'Login successful',
            'username': username,
            'email': user['email'],
            'session_token': session_token
        }
    
    def verify_session(self, session_token: str) -> Optional[str]:
        """
        Verify session token and return username.
        
        Args:
            session_token: Session token
        
        Returns:
            Username if valid, None otherwise
        """
        data = self._load_users()
        users = data['users']
        
        for username, user in users.items():
            if user.get('session_token') == session_token:
                return username
        
        return None
    
    def logout(self, session_token: str) -> bool:
        """
        Logout user by invalidating session token.
        
        Args:
            session_token: Session token
        
        Returns:
            True if successful
        """
        data = self._load_users()
        users = data['users']
        
        for username, user in users.items():
            if user.get('session_token') == session_token:
                user['session_token'] = None
                self._save_users(data)
                return True
        
        return False
    
    def get_user_info(self, username: str) -> Optional[Dict]:
        """
        Get user information.
        
        Args:
            username: Username
        
        Returns:
            User info dict (without password)
        """
        data = self._load_users()
        users = data['users']
        
        if username not in users:
            return None
        
        user = users[username].copy()
        user.pop('password', None)
        user.pop('salt', None)
        user.pop('session_token', None)
        user['username'] = username
        
        return user


# Singleton instance
_auth_service = None


def get_auth_service() -> AuthService:
    """Get singleton auth service instance."""
    global _auth_service
    if _auth_service is None:
        _auth_service = AuthService()
    return _auth_service
