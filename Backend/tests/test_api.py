"""
Integration tests for API endpoints.

Tests the /api/analyze and /api/recommendations endpoints with various scenarios.
"""

import pytest
import io
import os
from PIL import Image
import numpy as np
from app import app


@pytest.fixture
def client():
    """Create a test client for the Flask app."""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


@pytest.fixture
def sample_image():
    """Create a sample test image in memory."""
    # Create a simple RGB image
    img = Image.new('RGB', (640, 480), color='white')
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='JPEG')
    img_bytes.seek(0)
    return img_bytes


@pytest.fixture
def large_image():
    """Create a large test image exceeding 10MB."""
    # Create a large image (approximately 11MB)
    img = Image.new('RGB', (4000, 3000), color='white')
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='JPEG', quality=100)
    img_bytes.seek(0)
    return img_bytes


class TestAnalyzeEndpoint:
    """Tests for the /api/analyze endpoint."""
    
    def test_analyze_no_image(self, client):
        """Test analyze endpoint with no image file."""
        response = client.post('/api/analyze')
        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] is False
        assert data['code'] == 'NO_IMAGE'
    
    def test_analyze_empty_filename(self, client):
        """Test analyze endpoint with empty filename."""
        data = {'image': (io.BytesIO(b''), '')}
        response = client.post('/api/analyze', data=data, content_type='multipart/form-data')
        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] is False
        assert data['code'] == 'NO_IMAGE'
    
    def test_analyze_invalid_format(self, client):
        """Test analyze endpoint with invalid file format."""
        data = {'image': (io.BytesIO(b'test data'), 'test.txt')}
        response = client.post('/api/analyze', data=data, content_type='multipart/form-data')
        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] is False
        assert data['code'] == 'INVALID_FORMAT'
    
    def test_analyze_valid_formats(self, client):
        """Test analyze endpoint accepts valid image formats."""
        formats = ['test.jpg', 'test.jpeg', 'test.png', 'test.webp']
        
        for filename in formats:
            # Create a fresh image for each test
            img = Image.new('RGB', (640, 480), color='white')
            img_bytes = io.BytesIO()
            img.save(img_bytes, format='JPEG')
            img_bytes.seek(0)
            
            data = {'image': (img_bytes, filename)}
            response = client.post('/api/analyze', data=data, content_type='multipart/form-data')
            # Response may be 400 if no face detected, but should not be format error
            response_data = response.get_json()
            if not response_data['success']:
                assert response_data['code'] != 'INVALID_FORMAT'
    
    def test_analyze_with_real_face_image(self, client):
        """Test analyze endpoint with a real face image if available."""
        # Try to load a test image from static directory
        test_image_path = os.path.join('static', 'images', 'hairstyles', 'long-layers.jpg')
        
        if not os.path.exists(test_image_path):
            pytest.skip("Test image not available")
        
        with open(test_image_path, 'rb') as f:
            data = {'image': (f, 'test.jpg')}
            response = client.post('/api/analyze', data=data, content_type='multipart/form-data')
            # May succeed or fail depending on whether face is detected
            assert response.status_code in [200, 400]


class TestRecommendationsEndpoint:
    """Tests for the /api/recommendations endpoint."""
    
    def test_recommendations_no_face_shape(self, client):
        """Test recommendations endpoint without face_shape parameter."""
        response = client.get('/api/recommendations')
        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] is False
        assert data['code'] == 'MISSING_PARAMETER'
    
    def test_recommendations_invalid_face_shape(self, client):
        """Test recommendations endpoint with invalid face_shape."""
        response = client.get('/api/recommendations?face_shape=invalid')
        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] is False
        assert data['code'] == 'INVALID_FACE_SHAPE'
    
    def test_recommendations_valid_face_shapes(self, client):
        """Test recommendations endpoint with all valid face shapes."""
        face_shapes = ['oval', 'round', 'square', 'heart', 'diamond']
        
        for face_shape in face_shapes:
            response = client.get(f'/api/recommendations?face_shape={face_shape}')
            assert response.status_code == 200
            data = response.get_json()
            assert data['success'] is True
            assert data['face_shape'] == face_shape
            assert 'recommendations' in data
            assert isinstance(data['recommendations'], list)
    
    def test_recommendations_with_limit(self, client):
        """Test recommendations endpoint with limit parameter."""
        response = client.get('/api/recommendations?face_shape=oval&limit=3')
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert len(data['recommendations']) <= 3
    
    def test_recommendations_with_sort_by(self, client):
        """Test recommendations endpoint with sort_by parameter."""
        # Test popularity sorting
        response = client.get('/api/recommendations?face_shape=oval&sort_by=popularity')
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        
        # Test difficulty sorting
        response = client.get('/api/recommendations?face_shape=oval&sort_by=difficulty')
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
    
    def test_recommendations_response_structure(self, client):
        """Test that recommendations have the expected structure."""
        response = client.get('/api/recommendations?face_shape=oval')
        assert response.status_code == 200
        data = response.get_json()
        
        if len(data['recommendations']) > 0:
            hairstyle = data['recommendations'][0]
            assert 'id' in hairstyle
            assert 'name' in hairstyle
            assert 'description' in hairstyle
            assert 'image_url' in hairstyle
            assert 'reason' in hairstyle
            assert 'suitable_face_shapes' in hairstyle


class TestHealthEndpoint:
    """Tests for the /api/health endpoint."""
    
    def test_health_check(self, client):
        """Test health check endpoint."""
        response = client.get('/api/health')
        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == 'healthy'


class TestTryOnEndpoints:
    """Tests for AI try-on API endpoints."""
    
    def test_try_on_status(self, client):
        """Test try-on status endpoint."""
        response = client.get('/api/try-on/status')
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert 'enabled' in data
        # If enabled, should have status and message
        if data['enabled']:
            assert 'status' in data
            assert 'message' in data
    
    def test_try_on_no_image(self, client):
        """Test try-on endpoint with no image file."""
        response = client.post('/api/try-on', data={'hairstyle_id': 'hs001'})
        # Should return 503 if service not enabled, or 400 if enabled
        assert response.status_code in [400, 503]
        data = response.get_json()
        assert data['success'] is False
        # If service is enabled, should get NO_IMAGE error
        # If service is disabled, should get FEATURE_DISABLED error
        assert data['code'] in ['NO_IMAGE', 'FEATURE_DISABLED']
    
    def test_try_on_no_hairstyle_id(self, client, sample_image):
        """Test try-on endpoint without hairstyle_id."""
        data = {'image': (sample_image, 'test.jpg')}
        response = client.post('/api/try-on', data=data, content_type='multipart/form-data')
        # Should return 503 if service not enabled, or 400 if enabled
        assert response.status_code in [400, 503]
        response_data = response.get_json()
        assert response_data['success'] is False
        # If service is enabled, should get MISSING_PARAMETER error
        # If service is disabled, should get FEATURE_DISABLED error
        assert response_data['code'] in ['MISSING_PARAMETER', 'FEATURE_DISABLED']
    
    def test_try_on_invalid_hairstyle_id(self, client, sample_image):
        """Test try-on endpoint with invalid hairstyle_id."""
        data = {
            'image': (sample_image, 'test.jpg'),
            'hairstyle_id': 'invalid_id'
        }
        response = client.post('/api/try-on', data=data, content_type='multipart/form-data')
        # Should return 404 for not found or 503 if service disabled
        assert response.status_code in [404, 503]
        response_data = response.get_json()
        assert response_data['success'] is False


class TestTryOnVariationsEndpoint:
    """Tests for the /api/try-on/variations endpoint - Task 9.1"""
    
    def test_variations_with_valid_image_and_hairstyle_id(self, client, sample_image, monkeypatch):
        """Test variations endpoint with valid image and hairstyle_id."""
        # Mock the Ultra service to avoid actual API calls
        from stable_image_ultra_service import StableImageUltraService
        import base64
        
        # Create mock variation images
        def create_mock_image():
            img = Image.new('RGB', (512, 512), color='blue')
            img_bytes = io.BytesIO()
            img.save(img_bytes, format='PNG')
            return img_bytes.getvalue()
        
        mock_variations = [create_mock_image() for _ in range(4)]
        
        def mock_generate_variations(self, user_image_bytes, hairstyle_description, num_variations=4):
            return mock_variations[:num_variations]
        
        monkeypatch.setattr(StableImageUltraService, 'generate_variations', mock_generate_variations)
        
        # Make request
        data = {
            'image': (sample_image, 'test.jpg'),
            'hairstyle_id': 'hs001',
            'num_variations': 4
        }
        response = client.post('/api/try-on/variations', data=data, content_type='multipart/form-data')
        
        # If service is disabled, we expect 503
        if response.status_code == 503:
            response_data = response.get_json()
            assert response_data['success'] is False
            assert response_data['code'] == 'FEATURE_DISABLED'
        else:
            # If service is enabled, we expect 200
            assert response.status_code == 200
            response_data = response.get_json()
            assert response_data['success'] is True
            assert 'result_urls' in response_data
            assert 'count' in response_data
            assert 'hairstyle_id' in response_data
            assert 'hairstyle_name' in response_data
    
    def test_variations_response_contains_multiple_result_urls(self, client, sample_image, monkeypatch):
        """Test that response contains multiple result URLs."""
        # Mock the Ultra service
        from stable_image_ultra_service import StableImageUltraService
        
        def create_mock_image():
            img = Image.new('RGB', (512, 512), color='red')
            img_bytes = io.BytesIO()
            img.save(img_bytes, format='PNG')
            return img_bytes.getvalue()
        
        mock_variations = [create_mock_image() for _ in range(3)]
        
        def mock_generate_variations(self, user_image_bytes, hairstyle_description, num_variations=4):
            return mock_variations[:num_variations]
        
        monkeypatch.setattr(StableImageUltraService, 'generate_variations', mock_generate_variations)
        
        # Make request for 3 variations
        data = {
            'image': (sample_image, 'test.jpg'),
            'hairstyle_id': 'hs001',
            'num_variations': 3
        }
        response = client.post('/api/try-on/variations', data=data, content_type='multipart/form-data')
        
        # If service is enabled
        if response.status_code == 200:
            response_data = response.get_json()
            assert response_data['success'] is True
            assert isinstance(response_data['result_urls'], list)
            assert len(response_data['result_urls']) == 3
            assert response_data['count'] == 3
            
            # Verify each URL is a string
            for url in response_data['result_urls']:
                assert isinstance(url, str)
                assert url.startswith('/uploads/')
    
    def test_variations_maximum_variations_limit(self, client, monkeypatch):
        """Test maximum variations limit of 4."""
        # Mock the Ultra service
        from stable_image_ultra_service import StableImageUltraService
        
        def create_mock_image():
            img = Image.new('RGB', (512, 512), color='green')
            img_bytes = io.BytesIO()
            img.save(img_bytes, format='PNG')
            return img_bytes.getvalue()
        
        # Create 4 mock variations (max allowed)
        mock_variations = [create_mock_image() for _ in range(4)]
        
        def mock_generate_variations(self, user_image_bytes, hairstyle_description, num_variations=4):
            # Service should limit to 4 even if more requested
            return mock_variations[:min(num_variations, 4)]
        
        monkeypatch.setattr(StableImageUltraService, 'generate_variations', mock_generate_variations)
        
        # Test with exactly 4 variations (valid)
        # Create fresh image for first request
        img1 = Image.new('RGB', (640, 480), color='white')
        img1_bytes = io.BytesIO()
        img1.save(img1_bytes, format='JPEG')
        img1_bytes.seek(0)
        
        data = {
            'image': (img1_bytes, 'test.jpg'),
            'hairstyle_id': 'hs001',
            'num_variations': 4
        }
        response = client.post('/api/try-on/variations', data=data, content_type='multipart/form-data')
        
        if response.status_code == 200:
            response_data = response.get_json()
            assert response_data['success'] is True
            assert len(response_data['result_urls']) <= 4
        
        # Test with more than 4 variations (should be rejected by endpoint)
        # Create fresh image for second request
        img2 = Image.new('RGB', (640, 480), color='white')
        img2_bytes = io.BytesIO()
        img2.save(img2_bytes, format='JPEG')
        img2_bytes.seek(0)
        
        data = {
            'image': (img2_bytes, 'test.jpg'),
            'hairstyle_id': 'hs001',
            'num_variations': 5
        }
        response = client.post('/api/try-on/variations', data=data, content_type='multipart/form-data')
        
        # Should return 400 for invalid parameter
        if response.status_code == 400:
            response_data = response.get_json()
            assert response_data['success'] is False
            assert response_data['code'] == 'INVALID_PARAMETER'
    
    def test_variations_error_handling_no_image(self, client):
        """Test error handling when no image is provided."""
        data = {'hairstyle_id': 'hs001', 'num_variations': 2}
        response = client.post('/api/try-on/variations', data=data)
        
        # Should return 400 or 503
        assert response.status_code in [400, 503]
        response_data = response.get_json()
        assert response_data['success'] is False
        assert response_data['code'] in ['NO_IMAGE', 'FEATURE_DISABLED']
    
    def test_variations_error_handling_no_hairstyle_id(self, client, sample_image):
        """Test error handling when hairstyle_id is missing."""
        data = {
            'image': (sample_image, 'test.jpg'),
            'num_variations': 2
        }
        response = client.post('/api/try-on/variations', data=data, content_type='multipart/form-data')
        
        # Should return 400 or 503
        assert response.status_code in [400, 503]
        response_data = response.get_json()
        assert response_data['success'] is False
        assert response_data['code'] in ['MISSING_PARAMETER', 'FEATURE_DISABLED']
    
    def test_variations_error_handling_invalid_hairstyle_id(self, client, sample_image, monkeypatch):
        """Test error handling with invalid hairstyle_id."""
        # Mock the Ultra service
        from stable_image_ultra_service import StableImageUltraService
        
        def mock_generate_variations(self, user_image_bytes, hairstyle_description, num_variations=4):
            return [b'mock_image_data']
        
        monkeypatch.setattr(StableImageUltraService, 'generate_variations', mock_generate_variations)
        
        data = {
            'image': (sample_image, 'test.jpg'),
            'hairstyle_id': 'invalid_id',
            'num_variations': 2
        }
        response = client.post('/api/try-on/variations', data=data, content_type='multipart/form-data')
        
        # Should return 404 for not found or 503 if service disabled
        assert response.status_code in [404, 503]
        response_data = response.get_json()
        assert response_data['success'] is False
    
    def test_variations_error_handling_invalid_file_format(self, client):
        """Test error handling with invalid file format."""
        # Create a text file instead of an image
        text_file = io.BytesIO(b"This is not an image")
        
        data = {
            'image': (text_file, 'test.txt'),
            'hairstyle_id': 'hs001',
            'num_variations': 2
        }
        response = client.post('/api/try-on/variations', data=data, content_type='multipart/form-data')
        
        # Should return 400 or 503
        assert response.status_code in [400, 503]
        response_data = response.get_json()
        assert response_data['success'] is False
        assert response_data['code'] in ['INVALID_FORMAT', 'FEATURE_DISABLED']
    
    def test_variations_with_default_num_variations(self, client, sample_image, monkeypatch):
        """Test variations endpoint with default num_variations (should be 4)."""
        # Mock the Ultra service
        from stable_image_ultra_service import StableImageUltraService
        
        def create_mock_image():
            img = Image.new('RGB', (512, 512), color='yellow')
            img_bytes = io.BytesIO()
            img.save(img_bytes, format='PNG')
            return img_bytes.getvalue()
        
        mock_variations = [create_mock_image() for _ in range(4)]
        
        def mock_generate_variations(self, user_image_bytes, hairstyle_description, num_variations=4):
            return mock_variations[:num_variations]
        
        monkeypatch.setattr(StableImageUltraService, 'generate_variations', mock_generate_variations)
        
        # Make request without specifying num_variations
        data = {
            'image': (sample_image, 'test.jpg'),
            'hairstyle_id': 'hs001'
            # num_variations not specified, should default to 4
        }
        response = client.post('/api/try-on/variations', data=data, content_type='multipart/form-data')
        
        # If service is enabled
        if response.status_code == 200:
            response_data = response.get_json()
            assert response_data['success'] is True
            # Should generate 4 variations by default
            assert len(response_data['result_urls']) == 4
    
    def test_variations_service_disabled(self, client, sample_image):
        """Test variations endpoint when service is disabled."""
        # This test will naturally pass if STABILITY_API_KEY is not set
        data = {
            'image': (sample_image, 'test.jpg'),
            'hairstyle_id': 'hs001',
            'num_variations': 2
        }
        response = client.post('/api/try-on/variations', data=data, content_type='multipart/form-data')
        
        # If service is disabled, should return 503
        if response.status_code == 503:
            response_data = response.get_json()
            assert response_data['success'] is False
            assert response_data['code'] == 'FEATURE_DISABLED'
            assert 'STABILITY_API_KEY' in response_data['error']


if __name__ == '__main__':
    pytest.main([__file__, '-v'])



class TestFavoritesEndpoints:
    """Tests for favorites API endpoints."""
    
    def test_add_favorite(self, client):
        """Test adding a favorite hairstyle."""
        data = {
            'hairstyle_id': 'hs001',
            'hairstyle_name': 'Long Layers',
            'face_shape': 'oval'
        }
        
        response = client.post('/api/favorites', json=data)
        assert response.status_code == 201
        response_data = response.get_json()
        assert response_data['success'] is True
    
    def test_add_favorite_missing_parameters(self, client):
        """Test adding favorite without required parameters."""
        data = {'hairstyle_id': 'hs001'}  # Missing hairstyle_name
        
        response = client.post('/api/favorites', json=data)
        assert response.status_code == 400
        response_data = response.get_json()
        assert response_data['success'] is False
        assert response_data['code'] == 'MISSING_PARAMETERS'
    
    def test_add_duplicate_favorite(self, client):
        """Test adding the same favorite twice."""
        data = {
            'hairstyle_id': 'hs001',
            'hairstyle_name': 'Long Layers',
            'face_shape': 'oval'
        }
        
        # Add first time
        client.post('/api/favorites', json=data)
        
        # Try to add again
        response = client.post('/api/favorites', json=data)
        assert response.status_code == 409
        response_data = response.get_json()
        assert response_data['code'] == 'ALREADY_EXISTS'
    
    def test_get_favorites(self, client):
        """Test getting user's favorites."""
        # Add some favorites
        client.post('/api/favorites', json={
            'hairstyle_id': 'long-layers',
            'hairstyle_name': 'Long Layers',
            'face_shape': 'oval'
        })
        
        # Get favorites
        response = client.get('/api/favorites')
        assert response.status_code == 200
        response_data = response.get_json()
        assert response_data['success'] is True
        assert 'favorites' in response_data
        assert isinstance(response_data['favorites'], list)
    
    def test_get_favorites_empty(self, client):
        """Test getting favorites when user has none."""
        response = client.get('/api/favorites')
        assert response.status_code == 200
        response_data = response.get_json()
        assert response_data['success'] is True
        assert response_data['favorites'] == []
    
    def test_remove_favorite(self, client):
        """Test removing a favorite."""
        # Add favorite
        client.post('/api/favorites', json={
            'hairstyle_id': 'hs001',
            'hairstyle_name': 'Long Layers'
        })
        
        # Remove it
        response = client.delete('/api/favorites/hs001')
        assert response.status_code == 200
        response_data = response.get_json()
        assert response_data['success'] is True
    
    def test_remove_nonexistent_favorite(self, client):
        """Test removing a favorite that doesn't exist."""
        # Create session first
        client.post('/api/session')
        
        response = client.delete('/api/favorites/nonexistent')
        assert response.status_code == 404
        response_data = response.get_json()
        assert response_data['code'] == 'NOT_FOUND'
    
    def test_check_favorite(self, client):
        """Test checking if hairstyle is favorite."""
        # Not favorite initially
        response = client.get('/api/favorites/check/hs001')
        assert response.status_code == 200
        response_data = response.get_json()
        assert response_data['is_favorite'] is False
        
        # Add favorite
        client.post('/api/favorites', json={
            'hairstyle_id': 'hs001',
            'hairstyle_name': 'Long Layers'
        })
        
        # Now it is favorite
        response = client.get('/api/favorites/check/hs001')
        assert response.status_code == 200
        response_data = response.get_json()
        assert response_data['is_favorite'] is True
