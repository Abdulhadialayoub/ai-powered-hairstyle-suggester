"""
User database module for managing user favorites.

This module provides SQLite database functionality for storing
user sessions and favorite hairstyles.
"""

import sqlite3
import os
import uuid
from typing import List, Dict, Optional
from datetime import datetime


class UserDatabase:
    """Manages user data and favorites in SQLite database."""
    
    def __init__(self, db_path: str = None):
        """
        Initialize the user database.
        
        Args:
            db_path: Path to the SQLite database file. If None, uses default path.
        """
        if db_path is None:
            # Default path relative to this file (services/ folder)
            # Go up one level to backend/, then into data/
            current_dir = os.path.dirname(os.path.abspath(__file__))
            parent_dir = os.path.dirname(current_dir)
            db_path = os.path.join(parent_dir, 'data', 'users.db')
        
        self.db_path = db_path
        self._ensure_db_directory()
        self._initialize_database()
    
    def _ensure_db_directory(self):
        """Ensure the database directory exists."""
        db_dir = os.path.dirname(self.db_path)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir, exist_ok=True)
    
    def _get_connection(self) -> sqlite3.Connection:
        """Get a database connection."""
        conn = sqlite3.Connection(self.db_path)
        conn.row_factory = sqlite3.Row  # Enable column access by name
        return conn
    
    def _initialize_database(self):
        """Create database tables if they don't exist."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Create users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT UNIQUE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create favorites table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS favorites (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                hairstyle_id TEXT NOT NULL,
                hairstyle_name TEXT NOT NULL,
                face_shape TEXT,
                image_url TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
                UNIQUE(user_id, hairstyle_id)
            )
        ''')
        
        # Create index for faster queries
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_favorites_user_id 
            ON favorites(user_id)
        ''')
        
        # Migration: Add image_url column if it doesn't exist
        try:
            cursor.execute('ALTER TABLE favorites ADD COLUMN image_url TEXT')
            conn.commit()
        except sqlite3.OperationalError:
            # Column already exists
            pass
        
        conn.commit()
        conn.close()
    
    def create_session(self) -> str:
        """
        Create a new user session.
        
        Returns:
            Session ID string.
        """
        session_id = str(uuid.uuid4())
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            'INSERT INTO users (session_id) VALUES (?)',
            (session_id,)
        )
        
        conn.commit()
        conn.close()
        
        return session_id
    
    def get_user_id(self, session_id: str) -> Optional[int]:
        """
        Get user ID from session ID or username.
        
        Args:
            session_id: The session ID or username.
        
        Returns:
            User ID if found, None otherwise.
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Try to find by session_id first, then by username (for auth system)
        cursor.execute(
            'SELECT id FROM users WHERE session_id = ? OR session_id = ?',
            (session_id, session_id)
        )
        
        row = cursor.fetchone()
        
        # If not found, try creating a user with this username
        if not row:
            cursor.execute(
                'INSERT OR IGNORE INTO users (session_id) VALUES (?)',
                (session_id,)
            )
            conn.commit()
            
            cursor.execute(
                'SELECT id FROM users WHERE session_id = ?',
                (session_id,)
            )
            row = cursor.fetchone()
        
        conn.close()
        
        return row['id'] if row else None
    
    def add_favorite(
        self,
        session_id: str,
        hairstyle_id: str,
        hairstyle_name: str,
        face_shape: str = None,
        image_url: str = None
    ) -> bool:
        """
        Add a hairstyle to user's favorites.
        
        Args:
            session_id: User's session ID.
            hairstyle_id: ID of the hairstyle.
            hairstyle_name: Name of the hairstyle.
            face_shape: Optional face shape.
        
        Returns:
            True if added successfully, False if already exists.
        """
        user_id = self.get_user_id(session_id)
        if not user_id:
            return False
        
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute(
                '''INSERT INTO favorites (user_id, hairstyle_id, hairstyle_name, face_shape, image_url)
                   VALUES (?, ?, ?, ?, ?)''',
                (user_id, hairstyle_id, hairstyle_name, face_shape, image_url)
            )
            conn.commit()
            conn.close()
            return True
        except sqlite3.IntegrityError:
            # Already exists
            conn.close()
            return False
    
    def remove_favorite(self, session_id: str, hairstyle_id: str) -> bool:
        """
        Remove a hairstyle from user's favorites.
        
        Args:
            session_id: User's session ID.
            hairstyle_id: ID of the hairstyle to remove.
        
        Returns:
            True if removed successfully, False otherwise.
        """
        user_id = self.get_user_id(session_id)
        if not user_id:
            return False
        
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            'DELETE FROM favorites WHERE user_id = ? AND hairstyle_id = ?',
            (user_id, hairstyle_id)
        )
        
        deleted = cursor.rowcount > 0
        conn.commit()
        conn.close()
        
        return deleted
    
    def get_favorites(self, session_id: str) -> List[Dict]:
        """
        Get all favorites for a user.
        
        Args:
            session_id: User's session ID.
        
        Returns:
            List of favorite hairstyle dictionaries.
        """
        user_id = self.get_user_id(session_id)
        if not user_id:
            return []
        
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            '''SELECT id, hairstyle_id, hairstyle_name, face_shape, image_url, created_at
               FROM favorites
               WHERE user_id = ?
               ORDER BY created_at DESC''',
            (user_id,)
        )
        
        rows = cursor.fetchall()
        conn.close()
        
        favorites = []
        for row in rows:
            favorites.append({
                'id': row['id'],
                'hairstyle_id': row['hairstyle_id'],
                'hairstyle_name': row['hairstyle_name'],
                'face_shape': row['face_shape'],
                'image_url': row['image_url'],
                'created_at': row['created_at']
            })
        
        return favorites
    
    def is_favorite(self, session_id: str, hairstyle_id: str) -> bool:
        """
        Check if a hairstyle is in user's favorites.
        
        Args:
            session_id: User's session ID.
            hairstyle_id: ID of the hairstyle.
        
        Returns:
            True if favorite, False otherwise.
        """
        user_id = self.get_user_id(session_id)
        if not user_id:
            return False
        
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            'SELECT 1 FROM favorites WHERE user_id = ? AND hairstyle_id = ?',
            (user_id, hairstyle_id)
        )
        
        exists = cursor.fetchone() is not None
        conn.close()
        
        return exists


# Singleton instance
_user_db_instance = None


def get_user_database() -> UserDatabase:
    """
    Get the singleton user database instance.
    
    Returns:
        UserDatabase instance.
    """
    global _user_db_instance
    if _user_db_instance is None:
        _user_db_instance = UserDatabase()
    return _user_db_instance
