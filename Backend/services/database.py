"""
Database access layer for hairstyle recommendations.

This module provides functions to load, query, filter, and rank hairstyles
from the JSON database.
"""

import json
import os
from typing import List, Dict, Optional


class HairstyleDatabase:
    """Manages access to the hairstyle database."""
    
    def __init__(self, db_path: str = None):
        """
        Initialize the database with the path to the JSON file.
        
        Args:
            db_path: Path to the hairstyles.json file. If None, uses default path.
        """
        if db_path is None:
            # Default path relative to this file (services/ folder)
            # Go up one level to backend/, then into data/
            current_dir = os.path.dirname(os.path.abspath(__file__))
            parent_dir = os.path.dirname(current_dir)
            db_path = os.path.join(parent_dir, 'data', 'hairstyles.json')
        
        self.db_path = db_path
        self._hairstyles = None
    
    def load_hairstyles(self) -> List[Dict]:
        """
        Load hairstyles from the JSON database file.
        
        Returns:
            List of hairstyle dictionaries.
            
        Raises:
            FileNotFoundError: If the database file doesn't exist.
            json.JSONDecodeError: If the JSON file is malformed.
        """
        if self._hairstyles is not None:
            return self._hairstyles
        
        if not os.path.exists(self.db_path):
            raise FileNotFoundError(f"Hairstyle database not found at {self.db_path}")
        
        with open(self.db_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        self._hairstyles = data.get('hairstyles', [])
        return self._hairstyles
    
    def query_by_face_shape(self, face_shape: str) -> List[Dict]:
        """
        Query hairstyles that are suitable for a specific face shape.
        
        Args:
            face_shape: The face shape to query (e.g., 'oval', 'round', 'square', 'heart', 'diamond').
        
        Returns:
            List of hairstyle dictionaries suitable for the given face shape.
        """
        hairstyles = self.load_hairstyles()
        face_shape_lower = face_shape.lower()
        
        matching_hairstyles = [
            hairstyle for hairstyle in hairstyles
            if face_shape_lower in [shape.lower() for shape in hairstyle.get('suitable_face_shapes', [])]
        ]
        
        return matching_hairstyles
    
    def filter_and_rank(
        self,
        hairstyles: List[Dict],
        limit: int = 5,
        sort_by: str = 'popularity',
        min_popularity: Optional[int] = None,
        difficulty: Optional[str] = None
    ) -> List[Dict]:
        """
        Filter and rank hairstyles based on various criteria.
        
        Args:
            hairstyles: List of hairstyle dictionaries to filter and rank.
            limit: Maximum number of hairstyles to return (default: 5).
            sort_by: Field to sort by ('popularity' or 'difficulty'). Default: 'popularity'.
            min_popularity: Minimum popularity score (0-100). If None, no filtering.
            difficulty: Filter by difficulty level ('easy', 'medium', 'hard'). If None, no filtering.
        
        Returns:
            Filtered and ranked list of hairstyle dictionaries.
        """
        filtered = hairstyles.copy()
        
        # Apply filters
        if min_popularity is not None:
            filtered = [h for h in filtered if h.get('popularity', 0) >= min_popularity]
        
        if difficulty is not None:
            difficulty_lower = difficulty.lower()
            filtered = [h for h in filtered if h.get('difficulty', '').lower() == difficulty_lower]
        
        # Sort by specified field
        if sort_by == 'popularity':
            filtered.sort(key=lambda x: x.get('popularity', 0), reverse=True)
        elif sort_by == 'difficulty':
            # Sort by difficulty: easy -> medium -> hard
            difficulty_order = {'easy': 1, 'medium': 2, 'hard': 3}
            filtered.sort(key=lambda x: difficulty_order.get(x.get('difficulty', 'medium').lower(), 2))
        
        # Apply limit
        return filtered[:limit]
    
    def get_recommendations(
        self,
        face_shape: str,
        limit: int = 5,
        sort_by: str = 'popularity',
        **kwargs
    ) -> List[Dict]:
        """
        Get hairstyle recommendations for a specific face shape.
        
        This is a convenience method that combines querying by face shape
        and filtering/ranking in one call.
        
        Args:
            face_shape: The face shape to get recommendations for.
            limit: Maximum number of recommendations to return (default: 5).
            sort_by: Field to sort by ('popularity' or 'difficulty'). Default: 'popularity'.
            **kwargs: Additional filtering parameters (min_popularity, difficulty).
        
        Returns:
            List of recommended hairstyle dictionaries.
        """
        matching_hairstyles = self.query_by_face_shape(face_shape)
        return self.filter_and_rank(matching_hairstyles, limit=limit, sort_by=sort_by, **kwargs)
    
    def get_hairstyle_by_id(self, hairstyle_id: str) -> Optional[Dict]:
        """
        Get a specific hairstyle by its ID.
        
        Args:
            hairstyle_id: The unique ID of the hairstyle.
        
        Returns:
            Hairstyle dictionary if found, None otherwise.
        """
        hairstyles = self.load_hairstyles()
        for hairstyle in hairstyles:
            if hairstyle.get('id') == hairstyle_id:
                return hairstyle
        return None
    
    def get_all_face_shapes(self) -> List[str]:
        """
        Get a list of all unique face shapes in the database.
        
        Returns:
            List of face shape strings.
        """
        hairstyles = self.load_hairstyles()
        face_shapes = set()
        
        for hairstyle in hairstyles:
            shapes = hairstyle.get('suitable_face_shapes', [])
            face_shapes.update(shapes)
        
        return sorted(list(face_shapes))


# Singleton instance for easy access
_db_instance = None


def get_database() -> HairstyleDatabase:
    """
    Get the singleton database instance.
    
    Returns:
        HairstyleDatabase instance.
    """
    global _db_instance
    if _db_instance is None:
        _db_instance = HairstyleDatabase()
    return _db_instance
