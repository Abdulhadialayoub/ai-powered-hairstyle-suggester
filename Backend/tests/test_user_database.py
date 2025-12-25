"""
Unit tests for user database module.
"""

import pytest
import os
import tempfile
from services.user_database import UserDatabase


@pytest.fixture
def temp_db():
    """Create a temporary database for testing."""
    # Create a temporary file
    fd, path = tempfile.mkstemp(suffix='.db')
    os.close(fd)
    
    # Create database instance
    db = UserDatabase(db_path=path)
    
    yield db
    
    # Cleanup
    if os.path.exists(path):
        os.remove(path)


class TestUserDatabase:
    """Tests for UserDatabase class."""
    
    def test_create_session(self, temp_db):
        """Test creating a new session."""
        session_id = temp_db.create_session()
        assert session_id is not None
        assert len(session_id) > 0
        
        # Verify user was created
        user_id = temp_db.get_user_id(session_id)
        assert user_id is not None
    
    def test_get_user_id_invalid_session(self, temp_db):
        """Test getting user ID with invalid session."""
        user_id = temp_db.get_user_id('invalid-session-id')
        assert user_id is None
    
    def test_add_favorite(self, temp_db):
        """Test adding a favorite hairstyle."""
        session_id = temp_db.create_session()
        
        added = temp_db.add_favorite(
            session_id=session_id,
            hairstyle_id='hs001',
            hairstyle_name='Long Layers',
            face_shape='oval'
        )
        
        assert added is True
    
    def test_add_duplicate_favorite(self, temp_db):
        """Test adding the same favorite twice."""
        session_id = temp_db.create_session()
        
        # Add first time
        temp_db.add_favorite(session_id, 'hs001', 'Long Layers', 'oval')
        
        # Try to add again
        added = temp_db.add_favorite(session_id, 'hs001', 'Long Layers', 'oval')
        assert added is False
    
    def test_get_favorites(self, temp_db):
        """Test getting user's favorites."""
        session_id = temp_db.create_session()
        
        # Add multiple favorites
        temp_db.add_favorite(session_id, 'hs001', 'Long Layers', 'oval')
        temp_db.add_favorite(session_id, 'hs002', 'Bob Cut', 'round')
        temp_db.add_favorite(session_id, 'hs003', 'Pixie Cut', 'heart')
        
        favorites = temp_db.get_favorites(session_id)
        
        assert len(favorites) == 3
        # Check that all hairstyles are present
        hairstyle_ids = [fav['hairstyle_id'] for fav in favorites]
        assert 'hs001' in hairstyle_ids
        assert 'hs002' in hairstyle_ids
        assert 'hs003' in hairstyle_ids
    
    def test_get_favorites_empty(self, temp_db):
        """Test getting favorites for user with no favorites."""
        session_id = temp_db.create_session()
        favorites = temp_db.get_favorites(session_id)
        assert favorites == []
    
    def test_remove_favorite(self, temp_db):
        """Test removing a favorite."""
        session_id = temp_db.create_session()
        
        # Add favorite
        temp_db.add_favorite(session_id, 'hs001', 'Long Layers', 'oval')
        
        # Remove it
        removed = temp_db.remove_favorite(session_id, 'hs001')
        assert removed is True
        
        # Verify it's gone
        favorites = temp_db.get_favorites(session_id)
        assert len(favorites) == 0
    
    def test_remove_nonexistent_favorite(self, temp_db):
        """Test removing a favorite that doesn't exist."""
        session_id = temp_db.create_session()
        removed = temp_db.remove_favorite(session_id, 'nonexistent')
        assert removed is False
    
    def test_is_favorite(self, temp_db):
        """Test checking if hairstyle is favorite."""
        session_id = temp_db.create_session()
        
        # Not favorite initially
        assert temp_db.is_favorite(session_id, 'hs001') is False
        
        # Add favorite
        temp_db.add_favorite(session_id, 'hs001', 'Long Layers', 'oval')
        
        # Now it is favorite
        assert temp_db.is_favorite(session_id, 'hs001') is True
    
    def test_multiple_users(self, temp_db):
        """Test that favorites are isolated between users."""
        session1 = temp_db.create_session()
        session2 = temp_db.create_session()
        
        # User 1 adds favorite
        temp_db.add_favorite(session1, 'hs001', 'Long Layers', 'oval')
        
        # User 2 should not see it
        favorites2 = temp_db.get_favorites(session2)
        assert len(favorites2) == 0
        
        # User 1 should see it
        favorites1 = temp_db.get_favorites(session1)
        assert len(favorites1) == 1


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
