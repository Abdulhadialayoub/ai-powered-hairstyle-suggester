"""
Unit tests for recommendation engine.

Tests filtering by face shape, ranking logic, and edge cases.
"""

import unittest
import json
import os
import tempfile
from services.recommendation_engine import RecommendationEngine, FACE_SHAPE_EXPLANATIONS
from services.database import HairstyleDatabase


class TestRecommendationEngine(unittest.TestCase):
    """Test recommendation engine functionality."""
    
    def setUp(self):
        """Set up test fixtures with a temporary database."""
        # Create a temporary JSON file with test data
        self.test_hairstyles = {
            "hairstyles": [
                {
                    "id": "test001",
                    "name": "Test Long Layers",
                    "description": "Test description",
                    "suitable_face_shapes": ["oval", "round"],
                    "image_url": "/test/image1.jpg",
                    "difficulty": "easy",
                    "popularity": 90,
                    "tags": ["long", "layered"]
                },
                {
                    "id": "test002",
                    "name": "Test Bob",
                    "description": "Test bob",
                    "suitable_face_shapes": ["oval", "square"],
                    "image_url": "/test/image2.jpg",
                    "difficulty": "medium",
                    "popularity": 85,
                    "tags": ["bob", "short"]
                },
                {
                    "id": "test003",
                    "name": "Test Pixie",
                    "description": "Test pixie",
                    "suitable_face_shapes": ["oval"],
                    "image_url": "/test/image3.jpg",
                    "difficulty": "hard",
                    "popularity": 70,
                    "tags": ["short", "pixie"]
                },
                {
                    "id": "test004",
                    "name": "Test Waves",
                    "description": "Test waves",
                    "suitable_face_shapes": ["round", "square"],
                    "image_url": "/test/image4.jpg",
                    "difficulty": "easy",
                    "popularity": 95,
                    "tags": ["wavy", "medium"]
                },
                {
                    "id": "test005",
                    "name": "Test Updo",
                    "description": "Test updo",
                    "suitable_face_shapes": ["heart"],
                    "image_url": "/test/image5.jpg",
                    "difficulty": "hard",
                    "popularity": 75,
                    "tags": ["updo", "formal"]
                }
            ]
        }
        
        # Create temporary file
        self.temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json')
        json.dump(self.test_hairstyles, self.temp_file)
        self.temp_file.close()
        
        # Create database and engine with test data
        self.database = HairstyleDatabase(db_path=self.temp_file.name)
        self.engine = RecommendationEngine(database=self.database)
    
    def tearDown(self):
        """Clean up temporary files."""
        if os.path.exists(self.temp_file.name):
            os.unlink(self.temp_file.name)
    
    def test_filter_by_face_shape_oval(self):
        """Test filtering hairstyles for oval face shape."""
        recommendations = self.engine.get_recommendations(
            face_shape='oval',
            limit=10,
            include_explanations=False
        )
        
        # Should return 3 hairstyles suitable for oval
        self.assertEqual(len(recommendations), 3)
        
        # Verify all returned hairstyles are suitable for oval
        for hairstyle in recommendations:
            self.assertIn('oval', [s.lower() for s in hairstyle['suitable_face_shapes']])
    
    def test_filter_by_face_shape_round(self):
        """Test filtering hairstyles for round face shape."""
        recommendations = self.engine.get_recommendations(
            face_shape='round',
            limit=10,
            include_explanations=False
        )
        
        # Should return 2 hairstyles suitable for round
        self.assertEqual(len(recommendations), 2)
        
        # Verify all returned hairstyles are suitable for round
        for hairstyle in recommendations:
            self.assertIn('round', [s.lower() for s in hairstyle['suitable_face_shapes']])
    
    def test_filter_by_face_shape_heart(self):
        """Test filtering hairstyles for heart face shape."""
        recommendations = self.engine.get_recommendations(
            face_shape='heart',
            limit=10,
            include_explanations=False
        )
        
        # Should return 1 hairstyle suitable for heart
        self.assertEqual(len(recommendations), 1)
        self.assertEqual(recommendations[0]['id'], 'test005')
    
    def test_ranking_by_popularity(self):
        """Test that hairstyles are ranked by popularity."""
        recommendations = self.engine.get_recommendations(
            face_shape='oval',
            limit=10,
            sort_by='popularity',
            include_explanations=False
        )
        
        # Should be sorted by popularity (descending)
        popularities = [h['popularity'] for h in recommendations]
        self.assertEqual(popularities, sorted(popularities, reverse=True))
        
        # Highest popularity should be first
        self.assertEqual(recommendations[0]['id'], 'test001')  # popularity 90
    
    def test_ranking_by_difficulty(self):
        """Test that hairstyles can be ranked by difficulty."""
        recommendations = self.engine.get_recommendations(
            face_shape='oval',
            limit=10,
            sort_by='difficulty',
            include_explanations=False
        )
        
        # Should be sorted by difficulty (easy -> medium -> hard)
        difficulty_order = {'easy': 1, 'medium': 2, 'hard': 3}
        difficulties = [difficulty_order[h['difficulty']] for h in recommendations]
        self.assertEqual(difficulties, sorted(difficulties))
    
    def test_limit_results(self):
        """Test that results are limited to specified number."""
        # Request only 2 recommendations
        recommendations = self.engine.get_recommendations(
            face_shape='oval',
            limit=2,
            include_explanations=False
        )
        
        # Should return exactly 2
        self.assertEqual(len(recommendations), 2)
    
    def test_limit_more_than_available(self):
        """Test limit when requesting more than available."""
        # Request 10 but only 1 available for heart
        recommendations = self.engine.get_recommendations(
            face_shape='heart',
            limit=10,
            include_explanations=False
        )
        
        # Should return only 1
        self.assertEqual(len(recommendations), 1)
    
    def test_empty_database_scenario(self):
        """Test with face shape that has no matching hairstyles."""
        # Diamond face shape has no matches in test data
        recommendations = self.engine.get_recommendations(
            face_shape='diamond',
            limit=5,
            include_explanations=False
        )
        
        # Should return empty list
        self.assertEqual(len(recommendations), 0)
        self.assertIsInstance(recommendations, list)
    
    def test_explanations_included(self):
        """Test that explanations are added to recommendations."""
        recommendations = self.engine.get_recommendations(
            face_shape='oval',
            limit=5,
            include_explanations=True
        )
        
        # All recommendations should have a 'reason' field
        for hairstyle in recommendations:
            self.assertIn('reason', hairstyle)
            self.assertIsInstance(hairstyle['reason'], str)
            self.assertGreater(len(hairstyle['reason']), 0)
    
    def test_explanations_not_included(self):
        """Test that explanations can be excluded."""
        recommendations = self.engine.get_recommendations(
            face_shape='oval',
            limit=5,
            include_explanations=False
        )
        
        # Recommendations should not have 'reason' field
        for hairstyle in recommendations:
            self.assertNotIn('reason', hairstyle)
    
    def test_explanation_generation_with_matching_tags(self):
        """Test that explanations use tag-specific reasons when available."""
        recommendations = self.engine.get_recommendations(
            face_shape='oval',
            limit=1,
            include_explanations=True
        )
        
        # First recommendation has 'long' and 'layered' tags
        reason = recommendations[0]['reason']
        
        # Should contain explanation related to the tags
        self.assertIsInstance(reason, str)
        self.assertGreater(len(reason), 10)
    
    def test_explanation_for_all_face_shapes(self):
        """Test that explanations work for all face shapes."""
        face_shapes = ['oval', 'round', 'square', 'heart', 'diamond']
        
        for face_shape in face_shapes:
            # Create a test hairstyle
            test_hairstyle = {
                'name': 'Test Style',
                'tags': ['long', 'layered']
            }
            
            explanation = self.engine._generate_explanation(test_hairstyle, face_shape)
            
            self.assertIsInstance(explanation, str)
            self.assertGreater(len(explanation), 0)
    
    def test_get_recommendations_with_confidence(self):
        """Test getting recommendations with confidence score."""
        result = self.engine.get_recommendations_with_confidence(
            face_shape='oval',
            confidence=0.85,
            limit=3
        )
        
        # Should return dictionary with required fields
        self.assertIn('face_shape', result)
        self.assertIn('confidence', result)
        self.assertIn('recommendations', result)
        
        # Verify values
        self.assertEqual(result['face_shape'], 'oval')
        self.assertEqual(result['confidence'], 0.85)
        self.assertIsInstance(result['recommendations'], list)
        self.assertLessEqual(len(result['recommendations']), 3)
        
        # Recommendations should have explanations
        for hairstyle in result['recommendations']:
            self.assertIn('reason', hairstyle)
    
    def test_case_insensitive_face_shape(self):
        """Test that face shape matching is case-insensitive."""
        recommendations_lower = self.engine.get_recommendations(
            face_shape='oval',
            limit=5,
            include_explanations=False
        )
        
        recommendations_upper = self.engine.get_recommendations(
            face_shape='OVAL',
            limit=5,
            include_explanations=False
        )
        
        # Should return same results
        self.assertEqual(len(recommendations_lower), len(recommendations_upper))


if __name__ == '__main__':
    unittest.main()
