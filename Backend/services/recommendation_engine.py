"""
Recommendation engine for hairstyle suggestions.

This module provides the logic to recommend hairstyles based on face shape,
including ranking and explanation text for each recommendation.
"""

from typing import List, Dict
from .database import HairstyleDatabase


# Face shape explanation templates
FACE_SHAPE_EXPLANATIONS = {
    'oval': {
        'general': 'Your oval face shape is well-balanced and versatile, allowing you to pull off most hairstyles.',
        'style_reasons': {
            'long': 'adds elegance and complements your balanced proportions',
            'short': 'highlights your facial symmetry',
            'layered': 'enhances your natural face structure',
            'bob': 'frames your face beautifully',
            'bangs': 'adds dimension without overwhelming your features',
            'updo': 'showcases your balanced facial features',
            'wavy': 'adds softness while maintaining your natural balance',
            'straight': 'emphasizes your symmetrical features',
            'curly': 'adds volume without disrupting your proportions'
        }
    },
    'round': {
        'general': 'Your round face shape benefits from styles that add height and create the illusion of length.',
        'style_reasons': {
            'long': 'elongates your face and adds vertical lines',
            'layered': 'creates angles and adds dimension',
            'side-part': 'adds asymmetry and creates length',
            'voluminous': 'adds height at the crown to elongate your face',
            'updo': 'lifts the hair up to create vertical lines',
            'bangs': 'frames your face and adds structure',
            'wavy': 'adds texture without adding width',
            'bob': 'creates angles when cut below the chin',
            'ponytail': 'pulls hair up to elongate your face shape'
        }
    },
    'square': {
        'general': 'Your square face shape is complemented by styles that soften angular features and add curves.',
        'style_reasons': {
            'wavy': 'softens your strong jawline with gentle curves',
            'layered': 'adds softness and movement around your face',
            'side-swept': 'creates diagonal lines that soften angles',
            'curly': 'adds softness and balances angular features',
            'bob': 'frames your face and softens your jawline',
            'long': 'draws attention downward and softens your features',
            'bangs': 'breaks up the strong horizontal lines of your face',
            'textured': 'adds softness to counterbalance angular features',
            'voluminous': 'adds curves to balance your strong features'
        }
    },
    'heart': {
        'general': 'Your heart-shaped face is balanced by styles that add width at the jawline and minimize forehead width.',
        'style_reasons': {
            'chin-length': 'adds width at your narrow jawline',
            'side-swept': 'minimizes your wider forehead',
            'layered': 'adds volume at the bottom to balance your face',
            'bob': 'creates fullness at the jawline',
            'wavy': 'adds width where you need it most',
            'long': 'draws the eye downward and balances proportions',
            'textured': 'adds dimension at the lower half of your face',
            'updo': 'can be styled to balance your proportions',
            'bangs': 'reduces the appearance of a wider forehead'
        }
    },
    'diamond': {
        'general': 'Your diamond face shape is enhanced by styles that add width at the forehead and chin while showcasing your cheekbones.',
        'style_reasons': {
            'side-swept': 'adds width at your narrow forehead',
            'chin-length': 'balances your narrow chin',
            'textured': 'adds fullness where needed',
            'wavy': 'softens your angular features',
            'layered': 'creates balance throughout your face',
            'bob': 'adds width at the jawline',
            'bangs': 'widens your narrow forehead',
            'curly': 'adds volume to balance your features',
            'updo': 'can highlight your beautiful cheekbones'
        }
    }
}


class RecommendationEngine:
    """Generates hairstyle recommendations with explanations."""
    
    def __init__(self, database: HairstyleDatabase = None):
        """
        Initialize the recommendation engine.
        
        Args:
            database: HairstyleDatabase instance. If None, creates a new one.
        """
        self.database = database if database else HairstyleDatabase()
    
    def _generate_explanation(self, hairstyle: Dict, face_shape: str) -> str:
        """
        Generate an explanation for why a hairstyle suits a face shape.
        
        Args:
            hairstyle: Hairstyle dictionary with tags and description.
            face_shape: The face shape (e.g., 'oval', 'round').
        
        Returns:
            Explanation string.
        """
        face_shape_lower = face_shape.lower()
        
        if face_shape_lower not in FACE_SHAPE_EXPLANATIONS:
            return f"This style complements your {face_shape} face shape."
        
        explanations = FACE_SHAPE_EXPLANATIONS[face_shape_lower]
        style_reasons = explanations['style_reasons']
        
        # Find matching tags in the hairstyle
        tags = hairstyle.get('tags', [])
        
        # Try to find a matching reason based on tags
        for tag in tags:
            tag_lower = tag.lower()
            if tag_lower in style_reasons:
                return f"This style {style_reasons[tag_lower]}."
        
        # If no specific tag matches, use general explanation
        return explanations['general']
    
    def get_recommendations(
        self,
        face_shape: str,
        limit: int = 5,
        sort_by: str = 'popularity',
        include_explanations: bool = True
    ) -> List[Dict]:
        """
        Get hairstyle recommendations for a specific face shape.
        
        Args:
            face_shape: The face shape to get recommendations for.
            limit: Maximum number of recommendations (default: 5).
            sort_by: Field to sort by ('popularity' or 'difficulty'). Default: 'popularity'.
            include_explanations: Whether to include explanation text (default: True).
        
        Returns:
            List of hairstyle dictionaries with added 'reason' field if include_explanations is True.
        """
        # Get recommendations from database
        recommendations = self.database.get_recommendations(
            face_shape=face_shape,
            limit=limit,
            sort_by=sort_by
        )
        
        # Add explanations if requested
        if include_explanations:
            for hairstyle in recommendations:
                hairstyle['reason'] = self._generate_explanation(hairstyle, face_shape)
        
        return recommendations
    
    def get_recommendations_with_confidence(
        self,
        face_shape: str,
        confidence: float,
        limit: int = 5,
        sort_by: str = 'popularity'
    ) -> Dict:
        """
        Get recommendations along with face shape analysis results.
        
        Args:
            face_shape: The detected face shape.
            confidence: Confidence score of the face shape detection.
            limit: Maximum number of recommendations (default: 5).
            sort_by: Field to sort by ('popularity' or 'difficulty'). Default: 'popularity'.
        
        Returns:
            Dictionary with face_shape, confidence, and recommendations.
        """
        recommendations = self.get_recommendations(
            face_shape=face_shape,
            limit=limit,
            sort_by=sort_by,
            include_explanations=True
        )
        
        return {
            'face_shape': face_shape,
            'confidence': confidence,
            'recommendations': recommendations
        }


# Singleton instance for easy access
_engine_instance = None


def get_recommendation_engine() -> RecommendationEngine:
    """
    Get the singleton recommendation engine instance.
    
    Returns:
        RecommendationEngine instance.
    """
    global _engine_instance
    if _engine_instance is None:
        _engine_instance = RecommendationEngine()
    return _engine_instance
