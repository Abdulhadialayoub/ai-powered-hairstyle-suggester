"""
Unit tests for face analysis module.

Tests face shape classification logic with known measurements
and edge cases.
"""

import unittest
import numpy as np
from services.face_analysis import FaceAnalyzer


class TestFaceShapeClassification(unittest.TestCase):
    """Test face shape classification logic."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.analyzer = FaceAnalyzer()
    
    def test_oval_face_classification(self):
        """Test classification of oval face shape."""
        # Oval: face_length > face_width, balanced forehead and jaw
        measurements = {
            'face_length': 200.0,
            'face_width': 150.0,
            'forehead_width': 140.0,
            'jawline_width': 135.0
        }
        
        face_shape, confidence = self.analyzer.classify_face_shape(measurements)
        
        self.assertEqual(face_shape, 'oval')
        self.assertGreater(confidence, 0.6)
        self.assertLessEqual(confidence, 1.0)
    
    def test_round_face_classification(self):
        """Test classification of round face shape."""
        # Round: face_length ≈ face_width, soft curves
        measurements = {
            'face_length': 150.0,
            'face_width': 148.0,
            'forehead_width': 135.0,
            'jawline_width': 130.0
        }
        
        face_shape, confidence = self.analyzer.classify_face_shape(measurements)
        
        self.assertEqual(face_shape, 'round')
        self.assertGreater(confidence, 0.6)
    
    def test_square_face_classification(self):
        """Test classification of square face shape."""
        # Square: face_length ≈ face_width, angular with similar forehead and jaw
        measurements = {
            'face_length': 150.0,
            'face_width': 148.0,
            'forehead_width': 145.0,
            'jawline_width': 143.0
        }
        
        face_shape, confidence = self.analyzer.classify_face_shape(measurements)
        
        self.assertEqual(face_shape, 'square')
        self.assertGreater(confidence, 0.6)
    
    def test_heart_face_classification(self):
        """Test classification of heart face shape."""
        # Heart: wide forehead, narrow jaw
        measurements = {
            'face_length': 180.0,
            'face_width': 140.0,
            'forehead_width': 145.0,
            'jawline_width': 110.0
        }
        
        face_shape, confidence = self.analyzer.classify_face_shape(measurements)
        
        self.assertEqual(face_shape, 'heart')
        self.assertGreater(confidence, 0.6)
    
    def test_diamond_face_classification(self):
        """Test classification of diamond face shape."""
        # Diamond: narrow forehead and jaw, wide cheekbones
        measurements = {
            'face_length': 180.0,
            'face_width': 150.0,
            'forehead_width': 120.0,
            'jawline_width': 115.0
        }
        
        face_shape, confidence = self.analyzer.classify_face_shape(measurements)
        
        self.assertEqual(face_shape, 'diamond')
        self.assertGreater(confidence, 0.6)
    
    def test_edge_case_very_long_face(self):
        """Test edge case with very elongated face."""
        measurements = {
            'face_length': 250.0,
            'face_width': 140.0,
            'forehead_width': 135.0,
            'jawline_width': 130.0
        }
        
        face_shape, confidence = self.analyzer.classify_face_shape(measurements)
        
        # Should classify as oval (elongated)
        self.assertEqual(face_shape, 'oval')
        self.assertIsInstance(confidence, float)
        self.assertGreater(confidence, 0.0)
    
    def test_edge_case_equal_measurements(self):
        """Test edge case with all equal measurements."""
        measurements = {
            'face_length': 150.0,
            'face_width': 150.0,
            'forehead_width': 150.0,
            'jawline_width': 150.0
        }
        
        face_shape, confidence = self.analyzer.classify_face_shape(measurements)
        
        # Should classify as either round or square
        self.assertIn(face_shape, ['round', 'square'])
        self.assertIsInstance(confidence, float)
    
    def test_confidence_score_range(self):
        """Test that confidence scores are always in valid range."""
        test_cases = [
            {'face_length': 200.0, 'face_width': 150.0, 'forehead_width': 140.0, 'jawline_width': 135.0},
            {'face_length': 150.0, 'face_width': 148.0, 'forehead_width': 135.0, 'jawline_width': 130.0},
            {'face_length': 180.0, 'face_width': 140.0, 'forehead_width': 145.0, 'jawline_width': 110.0},
        ]
        
        for measurements in test_cases:
            face_shape, confidence = self.analyzer.classify_face_shape(measurements)
            
            self.assertGreaterEqual(confidence, 0.0, f"Confidence {confidence} is below 0")
            self.assertLessEqual(confidence, 1.0, f"Confidence {confidence} is above 1")
    
    def test_calculate_face_measurements(self):
        """Test face measurement calculation from landmarks."""
        # Create mock landmarks (468 points as in MediaPipe Face Mesh)
        landmarks = np.zeros((468, 3))
        
        # Set key landmark positions (normalized coordinates)
        landmarks[10] = [0.5, 0.1, 0.0]   # Top of forehead
        landmarks[152] = [0.5, 0.9, 0.0]  # Bottom of chin
        landmarks[234] = [0.2, 0.5, 0.0]  # Left cheek
        landmarks[454] = [0.8, 0.5, 0.0]  # Right cheek
        landmarks[127] = [0.25, 0.2, 0.0] # Left forehead
        landmarks[356] = [0.75, 0.2, 0.0] # Right forehead
        landmarks[172] = [0.3, 0.8, 0.0]  # Left jaw
        landmarks[397] = [0.7, 0.8, 0.0]  # Right jaw
        
        image_shape = (1000, 1000)  # 1000x1000 image
        
        measurements = self.analyzer.calculate_face_measurements(landmarks, image_shape)
        
        # Verify all measurements are present
        self.assertIn('face_length', measurements)
        self.assertIn('face_width', measurements)
        self.assertIn('forehead_width', measurements)
        self.assertIn('jawline_width', measurements)
        
        # Verify measurements are positive
        for key, value in measurements.items():
            self.assertGreater(value, 0, f"{key} should be positive")
        
        # Verify approximate expected values
        # Face length: from y=0.1 to y=0.9 = 0.8 * 1000 = 800
        self.assertAlmostEqual(measurements['face_length'], 800.0, delta=10.0)
        
        # Face width: from x=0.2 to x=0.8 = 0.6 * 1000 = 600
        self.assertAlmostEqual(measurements['face_width'], 600.0, delta=10.0)


if __name__ == '__main__':
    unittest.main()
