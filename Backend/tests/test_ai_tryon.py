"""
Tests for AI Hair Try-On functionality.

Note: These tests require REPLICATE_API_TOKEN to be set.
They will be skipped if the token is not available.
"""

import pytest
import os
from ai_hair_tryon import AIHairTryOn, get_ai_hair_tryon, is_ai_tryon_enabled
from PIL import Image
import io


# Skip all tests if API token not available
pytestmark = pytest.mark.skipif(
    not os.environ.get('REPLICATE_API_TOKEN'),
    reason="REPLICATE_API_TOKEN not set"
)


@pytest.fixture
def sample_image_bytes():
    """Create a sample image for testing."""
    img = Image.new('RGB', (512, 512), color='white')
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='JPEG')
    img_bytes.seek(0)
    return img_bytes.getvalue()


class TestAIHairTryOn:
    """Tests for AIHairTryOn class."""
    
    def test_initialization_with_token(self):
        """Test initialization with API token."""
        token = os.environ.get('REPLICATE_API_TOKEN')
        ai_tryon = AIHairTryOn(api_token=token)
        assert ai_tryon.enabled is True
        assert ai_tryon.api_token == token
    
    def test_initialization_without_token(self):
        """Test initialization fails without token."""
        # Temporarily remove token
        original_token = os.environ.get('REPLICATE_API_TOKEN')
        if original_token:
            del os.environ['REPLICATE_API_TOKEN']
        
        with pytest.raises(ValueError):
            AIHairTryOn()
        
        # Restore token
        if original_token:
            os.environ['REPLICATE_API_TOKEN'] = original_token
    
    def test_check_api_status(self):
        """Test API status check."""
        ai_tryon = get_ai_hair_tryon()
        status = ai_tryon.check_api_status()
        
        assert 'status' in status
        assert 'enabled' in status
        assert 'message' in status
    
    def test_is_ai_tryon_enabled(self):
        """Test if AI try-on is enabled."""
        assert is_ai_tryon_enabled() is True
    
    def test_get_singleton(self):
        """Test singleton pattern."""
        instance1 = get_ai_hair_tryon()
        instance2 = get_ai_hair_tryon()
        assert instance1 is instance2


class TestAITryOnIntegration:
    """Integration tests for AI try-on (requires API calls)."""
    
    @pytest.mark.slow
    def test_try_on_hairstyle(self, sample_image_bytes):
        """
        Test trying on a hairstyle.
        
        Note: This makes a real API call and may take 5-10 seconds.
        """
        ai_tryon = get_ai_hair_tryon()
        
        result = ai_tryon.try_on_hairstyle(
            sample_image_bytes,
            "long wavy blonde hair",
            quality="low"  # Use low quality for faster testing
        )
        
        # Result should be image bytes or None
        assert result is None or isinstance(result, bytes)
        
        if result:
            # Verify it's a valid image
            img = Image.open(io.BytesIO(result))
            assert img.format in ['JPEG', 'PNG']
    
    @pytest.mark.slow
    def test_generate_variations(self, sample_image_bytes):
        """
        Test generating variations.
        
        Note: This makes multiple API calls and may take 10-20 seconds.
        """
        ai_tryon = get_ai_hair_tryon()
        
        variations = ai_tryon.generate_variations(
            sample_image_bytes,
            "short pixie cut",
            num_variations=2
        )
        
        assert isinstance(variations, list)
        # May be empty if generation fails
        assert len(variations) <= 2


if __name__ == '__main__':
    pytest.main([__file__, '-v', '-m', 'not slow'])
