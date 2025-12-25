"""
Pytest configuration and shared fixtures.

This file contains common fixtures and configuration for all tests.
"""

import pytest
import sys
import os
from pathlib import Path

# Add backend directory to Python path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))


@pytest.fixture
def sample_image_bytes():
    """Provide sample image bytes for testing."""
    # Create a simple 100x100 RGB image
    from PIL import Image
    from io import BytesIO
    
    img = Image.new('RGB', (100, 100), color='red')
    buffer = BytesIO()
    img.save(buffer, format='JPEG')
    buffer.seek(0)
    return buffer.read()


@pytest.fixture
def sample_face_data():
    """Provide sample face analysis data."""
    return {
        'face_shape': 'oval',
        'confidence': 0.95,
        'features': {
            'face_width': 150,
            'face_height': 200,
            'jaw_width': 120
        }
    }


@pytest.fixture
def sample_hairstyle():
    """Provide sample hairstyle data."""
    return {
        'id': 'test-001',
        'name': 'Classic Fade',
        'description': 'A timeless fade cut',
        'tags': ['short', 'modern', 'easy'],
        'difficulty': 'easy',
        'face_shapes': ['oval', 'square'],
        'image_url': '/static/hairstyles/fade.jpg'
    }


@pytest.fixture
def mock_env_vars(monkeypatch):
    """Set up mock environment variables."""
    monkeypatch.setenv('REPLICATE_API_TOKEN', 'test_token_123')
    monkeypatch.setenv('STABILITY_API_KEY', 'test_stability_key')
    monkeypatch.setenv('GEMINI_API_KEY', 'test_gemini_key')


@pytest.fixture
def app_client():
    """Provide Flask test client."""
    from app import app
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client
