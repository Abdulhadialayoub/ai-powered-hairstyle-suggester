"""
Tests for Stable Image Ultra Service - Task 1 & 2.1
"""

import pytest
import os
import base64
import requests
from io import BytesIO
from PIL import Image
from dotenv import load_dotenv
from stable_image_ultra_service import StableImageUltraService, get_stable_image_ultra_service

# Load environment variables from .env file
load_dotenv()


def create_test_image(width: int, height: int, mode: str = 'RGB', format: str = 'PNG') -> bytes:
    """
    Helper function to create test images in various formats.
    
    Args:
        width: Image width in pixels
        height: Image height in pixels
        mode: PIL image mode (RGB, RGBA, L, etc.)
        format: Output format (PNG, JPEG, WebP)
    
    Returns:
        Image data as bytes
    """
    # Create a simple test image with colored rectangles
    image = Image.new(mode, (width, height), color='white')
    
    # Add some colored regions to make it more realistic
    from PIL import ImageDraw
    draw = ImageDraw.Draw(image)
    
    if mode in ['RGB', 'RGBA']:
        draw.rectangle([10, 10, width-10, height-10], fill='blue')
        draw.ellipse([width//4, height//4, 3*width//4, 3*height//4], fill='red')
    else:
        draw.rectangle([10, 10, width-10, height-10], fill=128)
    
    # Save to bytes
    buffer = BytesIO()
    if format == 'JPEG' and mode == 'RGBA':
        # JPEG doesn't support RGBA, convert first
        rgb_image = Image.new('RGB', image.size, (255, 255, 255))
        rgb_image.paste(image, mask=image.split()[3] if mode == 'RGBA' else None)
        rgb_image.save(buffer, format=format)
    else:
        image.save(buffer, format=format)
    
    buffer.seek(0)
    return buffer.read()


class TestStableImageUltraServiceInitialization:
    """Test service initialization and API key validation."""
    
    def test_init_with_api_key(self):
        """Test initialization with explicit API key."""
        service = StableImageUltraService(api_key="test_key_123")
        assert service.api_key == "test_key_123"
        assert service.enabled is True
        assert service.ultra_endpoint == "https://api.stability.ai/v2beta/stable-image/generate/ultra"
    
    def test_init_from_environment(self):
        """Test initialization from environment variable."""
        # This should work since STABILITY_API_KEY is in .env
        service = StableImageUltraService()
        assert service.api_key is not None
        assert service.enabled is True
    
    def test_init_without_api_key_raises_error(self):
        """Test that missing API key raises ValueError."""
        # Temporarily remove API key from environment
        original_key = os.environ.get('STABILITY_API_KEY')
        if original_key:
            del os.environ['STABILITY_API_KEY']
        
        try:
            with pytest.raises(ValueError) as exc_info:
                StableImageUltraService()
            assert "STABILITY_API_KEY not found" in str(exc_info.value)
        finally:
            # Restore original key
            if original_key:
                os.environ['STABILITY_API_KEY'] = original_key
    
    def test_singleton_pattern(self):
        """Test that get_stable_image_ultra_service returns singleton."""
        service1 = get_stable_image_ultra_service()
        service2 = get_stable_image_ultra_service()
        
        assert service1 is not None
        assert service1 is service2  # Same instance
    
    def test_check_api_status_structure(self):
        """Test that check_api_status returns correct structure."""
        service = StableImageUltraService(api_key="test_key")
        status = service.check_api_status()
        
        # Verify response structure
        assert "status" in status
        assert "enabled" in status
        assert "message" in status
        assert isinstance(status["enabled"], bool)
        assert isinstance(status["message"], str)


class TestImagePreprocessing:
    """Test image preprocessing functionality - Task 2.1"""
    
    def test_preprocess_jpeg_image(self):
        """Test image loading with JPEG format."""
        service = StableImageUltraService(api_key="test_key")
        
        # Create a test JPEG image
        jpeg_bytes = create_test_image(800, 600, mode='RGB', format='JPEG')
        
        # Preprocess the image
        result = service._preprocess_image(jpeg_bytes)
        
        # Verify result
        assert isinstance(result, Image.Image)
        assert result.mode == 'RGB'
        assert result.size == (800, 600)
    
    def test_preprocess_png_image(self):
        """Test image loading with PNG format."""
        service = StableImageUltraService(api_key="test_key")
        
        # Create a test PNG image
        png_bytes = create_test_image(1024, 768, mode='RGB', format='PNG')
        
        # Preprocess the image
        result = service._preprocess_image(png_bytes)
        
        # Verify result
        assert isinstance(result, Image.Image)
        assert result.mode == 'RGB'
        assert result.size == (1024, 768)
    
    def test_preprocess_webp_image(self):
        """Test image loading with WebP format."""
        service = StableImageUltraService(api_key="test_key")
        
        # Create a test WebP image
        webp_bytes = create_test_image(640, 480, mode='RGB', format='WebP')
        
        # Preprocess the image
        result = service._preprocess_image(webp_bytes)
        
        # Verify result
        assert isinstance(result, Image.Image)
        assert result.mode == 'RGB'
        assert result.size == (640, 480)
    
    def test_rgba_to_rgb_conversion(self):
        """Test RGBA to RGB conversion."""
        service = StableImageUltraService(api_key="test_key")
        
        # Create a test RGBA image (PNG with transparency)
        rgba_bytes = create_test_image(500, 500, mode='RGBA', format='PNG')
        
        # Preprocess the image
        result = service._preprocess_image(rgba_bytes)
        
        # Verify conversion to RGB
        assert result.mode == 'RGB'
        assert result.size == (500, 500)
    
    def test_resize_large_image_width(self):
        """Test resizing logic with image wider than MAX_IMAGE_SIZE."""
        service = StableImageUltraService(api_key="test_key")
        
        # Create an image larger than 1536px in width
        large_bytes = create_test_image(2000, 1000, mode='RGB', format='PNG')
        
        # Preprocess the image
        result = service._preprocess_image(large_bytes)
        
        # Verify image was resized
        assert result.width <= service.MAX_IMAGE_SIZE
        assert result.height <= service.MAX_IMAGE_SIZE
        # Width should be 1536, height should be proportionally scaled
        assert result.width == 1536
        assert result.height == 768  # 1000 * (1536/2000) = 768
    
    def test_resize_large_image_height(self):
        """Test resizing logic with image taller than MAX_IMAGE_SIZE."""
        service = StableImageUltraService(api_key="test_key")
        
        # Create an image larger than 1536px in height
        large_bytes = create_test_image(1000, 2000, mode='RGB', format='PNG')
        
        # Preprocess the image
        result = service._preprocess_image(large_bytes)
        
        # Verify image was resized
        assert result.width <= service.MAX_IMAGE_SIZE
        assert result.height <= service.MAX_IMAGE_SIZE
        # Height should be 1536, width should be proportionally scaled
        assert result.height == 1536
        assert result.width == 768  # 1000 * (1536/2000) = 768
    
    def test_resize_square_large_image(self):
        """Test resizing logic with square image larger than MAX_IMAGE_SIZE."""
        service = StableImageUltraService(api_key="test_key")
        
        # Create a large square image
        large_bytes = create_test_image(2048, 2048, mode='RGB', format='PNG')
        
        # Preprocess the image
        result = service._preprocess_image(large_bytes)
        
        # Verify image was resized to square
        assert result.width == service.MAX_IMAGE_SIZE
        assert result.height == service.MAX_IMAGE_SIZE
        assert result.width == result.height  # Still square
    
    def test_no_resize_small_image(self):
        """Test that small images are not resized."""
        service = StableImageUltraService(api_key="test_key")
        
        # Create a small image
        small_bytes = create_test_image(800, 600, mode='RGB', format='PNG')
        
        # Preprocess the image
        result = service._preprocess_image(small_bytes)
        
        # Verify image was NOT resized
        assert result.size == (800, 600)
    
    def test_aspect_ratio_preservation_landscape(self):
        """Test aspect ratio preservation for landscape images."""
        service = StableImageUltraService(api_key="test_key")
        
        # Create a landscape image that needs resizing
        # Original aspect ratio: 3000/1500 = 2.0
        large_bytes = create_test_image(3000, 1500, mode='RGB', format='PNG')
        
        # Preprocess the image
        result = service._preprocess_image(large_bytes)
        
        # Calculate aspect ratios
        original_ratio = 3000 / 1500
        result_ratio = result.width / result.height
        
        # Verify aspect ratio is preserved (within small tolerance for rounding)
        assert abs(original_ratio - result_ratio) < 0.01
    
    def test_aspect_ratio_preservation_portrait(self):
        """Test aspect ratio preservation for portrait images."""
        service = StableImageUltraService(api_key="test_key")
        
        # Create a portrait image that needs resizing
        # Original aspect ratio: 1200/1800 = 0.667
        large_bytes = create_test_image(1200, 1800, mode='RGB', format='PNG')
        
        # Preprocess the image
        result = service._preprocess_image(large_bytes)
        
        # Calculate aspect ratios
        original_ratio = 1200 / 1800
        result_ratio = result.width / result.height
        
        # Verify aspect ratio is preserved (within small tolerance for rounding)
        assert abs(original_ratio - result_ratio) < 0.01
    
    def test_invalid_image_data(self):
        """Test that invalid image data raises ValueError."""
        service = StableImageUltraService(api_key="test_key")
        
        # Try to preprocess invalid data
        with pytest.raises(ValueError) as exc_info:
            service._preprocess_image(b"not an image")
        
        assert "Failed to preprocess image" in str(exc_info.value)
    
    def test_encode_image_to_base64(self):
        """Test base64 encoding of images."""
        service = StableImageUltraService(api_key="test_key")
        
        # Create a test image
        test_bytes = create_test_image(100, 100, mode='RGB', format='PNG')
        image = Image.open(BytesIO(test_bytes))
        
        # Encode to base64
        result = service._encode_image_to_base64(image)
        
        # Verify result is a base64 string
        assert isinstance(result, str)
        assert len(result) > 0
        
        # Verify it can be decoded back
        import base64
        decoded = base64.b64decode(result)
        decoded_image = Image.open(BytesIO(decoded))
        assert decoded_image.size == (100, 100)


class TestPromptGeneration:
    """Test prompt engineering functionality - Task 3.1"""
    
    def test_build_prompt_includes_same_person(self):
        """Test prompt includes 'same person' keyword."""
        service = StableImageUltraService(api_key="test_key")
        
        hairstyle_desc = "long wavy blonde hair"
        prompt = service._build_prompt(hairstyle_desc)
        
        # Verify "same person" is in the prompt
        assert "same person" in prompt.lower()
    
    def test_build_prompt_includes_same_facial_features(self):
        """Test prompt includes 'same facial features' keyword."""
        service = StableImageUltraService(api_key="test_key")
        
        hairstyle_desc = "short curly brown hair"
        prompt = service._build_prompt(hairstyle_desc)
        
        # Verify "same facial features" is in the prompt
        assert "same facial features" in prompt.lower()
    
    def test_build_prompt_includes_hairstyle_description(self):
        """Test prompt includes the hairstyle description."""
        service = StableImageUltraService(api_key="test_key")
        
        hairstyle_desc = "pixie cut with side bangs"
        prompt = service._build_prompt(hairstyle_desc)
        
        # Verify hairstyle description is in the prompt
        assert hairstyle_desc in prompt
    
    def test_build_prompt_includes_quality_keywords(self):
        """Test prompt includes quality-enhancing keywords."""
        service = StableImageUltraService(api_key="test_key")
        
        hairstyle_desc = "medium length layered hair"
        prompt = service._build_prompt(hairstyle_desc)
        
        # Verify quality keywords are present
        assert "photorealistic" in prompt.lower()
        assert "high detail" in prompt.lower()
    
    def test_build_prompt_format_is_correct(self):
        """Test prompt format is correct and well-structured."""
        service = StableImageUltraService(api_key="test_key")
        
        hairstyle_desc = "bob cut with highlights"
        prompt = service._build_prompt(hairstyle_desc)
        
        # Verify prompt is a non-empty string
        assert isinstance(prompt, str)
        assert len(prompt) > 0
        
        # Verify it contains all key components
        assert "professional portrait photograph" in prompt.lower()
        assert hairstyle_desc in prompt
        assert "same person" in prompt.lower()
        assert "same facial features" in prompt.lower()
        assert "photorealistic" in prompt.lower()
    
    def test_build_negative_prompt_includes_different_person(self):
        """Test negative prompt includes 'different person' keyword."""
        service = StableImageUltraService(api_key="test_key")
        
        negative_prompt = service._build_negative_prompt()
        
        # Verify "different person" is in the negative prompt
        assert "different person" in negative_prompt.lower()
    
    def test_build_negative_prompt_includes_multiple_faces(self):
        """Test negative prompt includes 'multiple faces' keyword."""
        service = StableImageUltraService(api_key="test_key")
        
        negative_prompt = service._build_negative_prompt()
        
        # Verify "multiple faces" is in the negative prompt
        assert "multiple faces" in negative_prompt.lower()
    
    def test_build_negative_prompt_includes_blurry(self):
        """Test negative prompt includes 'blurry' keyword."""
        service = StableImageUltraService(api_key="test_key")
        
        negative_prompt = service._build_negative_prompt()
        
        # Verify "blurry" is in the negative prompt
        assert "blurry" in negative_prompt.lower()
    
    def test_build_negative_prompt_includes_unwanted_keywords(self):
        """Test negative prompt includes all unwanted keywords."""
        service = StableImageUltraService(api_key="test_key")
        
        negative_prompt = service._build_negative_prompt()
        
        # Verify multiple unwanted keywords are present
        assert "different face" in negative_prompt.lower()
        assert "multiple people" in negative_prompt.lower()
        assert "low quality" in negative_prompt.lower()
        assert "distorted" in negative_prompt.lower()
        assert "cartoon" in negative_prompt.lower()
        assert "deformed" in negative_prompt.lower()
    
    def test_build_negative_prompt_format_is_correct(self):
        """Test negative prompt format is correct."""
        service = StableImageUltraService(api_key="test_key")
        
        negative_prompt = service._build_negative_prompt()
        
        # Verify negative prompt is a non-empty string
        assert isinstance(negative_prompt, str)
        assert len(negative_prompt) > 0
    
    def test_prompt_with_different_hairstyles(self):
        """Test prompt generation with various hairstyle descriptions."""
        service = StableImageUltraService(api_key="test_key")
        
        hairstyles = [
            "long straight black hair",
            "short spiky blonde hair",
            "medium wavy red hair with bangs",
            "afro hairstyle",
            "braided ponytail"
        ]
        
        for hairstyle in hairstyles:
            prompt = service._build_prompt(hairstyle)
            
            # Each prompt should include the hairstyle description
            assert hairstyle in prompt
            # Each prompt should include face preservation keywords
            assert "same person" in prompt.lower()
            assert "same facial features" in prompt.lower()


class TestTryOnFunctionality:
    """Test core try-on functionality - Task 4.1"""
    
    def test_try_on_with_mock_successful_response(self, monkeypatch):
        """Test try-on functionality with mocked successful API response."""
        service = StableImageUltraService(api_key="test_key")
        
        # Create a test image
        test_image_bytes = create_test_image(800, 600, mode='RGB', format='PNG')
        
        # Create a mock response image
        mock_result_image = create_test_image(512, 512, mode='RGB', format='PNG')
        mock_result_base64 = base64.b64encode(mock_result_image).decode('utf-8')
        
        # Mock the requests.post call
        class MockResponse:
            status_code = 200
            text = "Success"
            
            def json(self):
                return {
                    "id": "test-generation-id",
                    "image": mock_result_base64,
                    "finish_reason": "SUCCESS",
                    "seed": 12345
                }
        
        def mock_post(*args, **kwargs):
            return MockResponse()
        
        monkeypatch.setattr(requests, "post", mock_post)
        
        # Call try_on_hairstyle
        result = service.try_on_hairstyle(
            user_image_bytes=test_image_bytes,
            hairstyle_description="long wavy blonde hair",
            style_strength=0.35
        )
        
        # Verify result
        assert result is not None
        assert isinstance(result, bytes)
        assert len(result) > 0
        
        # Verify it's a valid image
        result_image = Image.open(BytesIO(result))
        assert result_image.size == (512, 512)
    
    def test_try_on_request_headers_include_bearer_token(self, monkeypatch):
        """Test that request headers include Bearer token authentication."""
        service = StableImageUltraService(api_key="test_api_key_123")
        
        # Create a test image
        test_image_bytes = create_test_image(800, 600, mode='RGB', format='PNG')
        
        # Track the headers sent
        captured_headers = {}
        
        class MockResponse:
            status_code = 200
            text = "Success"
            
            def json(self):
                return {
                    "image": base64.b64encode(create_test_image(512, 512)).decode('utf-8')
                }
        
        def mock_post(*args, **kwargs):
            # Capture headers
            captured_headers.update(kwargs.get('headers', {}))
            return MockResponse()
        
        monkeypatch.setattr(requests, "post", mock_post)
        
        # Call try_on_hairstyle
        service.try_on_hairstyle(
            user_image_bytes=test_image_bytes,
            hairstyle_description="short curly hair",
            style_strength=0.4
        )
        
        # Verify Bearer token is in headers
        assert "Authorization" in captured_headers
        assert captured_headers["Authorization"] == "Bearer test_api_key_123"
    
    def test_try_on_request_parameters_set_correctly(self, monkeypatch):
        """Test that request parameters are set correctly."""
        service = StableImageUltraService(api_key="test_key")
        
        # Create a test image
        test_image_bytes = create_test_image(800, 600, mode='RGB', format='PNG')
        
        # Track the request parameters
        captured_data = {}
        captured_files = {}
        
        class MockResponse:
            status_code = 200
            text = "Success"
            
            def json(self):
                return {
                    "image": base64.b64encode(create_test_image(512, 512)).decode('utf-8')
                }
        
        def mock_post(*args, **kwargs):
            # Capture data and files
            captured_data.update(kwargs.get('data', {}))
            captured_files.update(kwargs.get('files', {}))
            return MockResponse()
        
        monkeypatch.setattr(requests, "post", mock_post)
        
        # Call try_on_hairstyle
        hairstyle_desc = "pixie cut with bangs"
        service.try_on_hairstyle(
            user_image_bytes=test_image_bytes,
            hairstyle_description=hairstyle_desc,
            style_strength=0.35
        )
        
        # Verify parameters
        assert "prompt" in captured_data
        assert hairstyle_desc in captured_data["prompt"]
        assert "same person" in captured_data["prompt"].lower()
        
        assert "negative_prompt" in captured_data
        assert "different person" in captured_data["negative_prompt"].lower()
        
        assert "output_format" in captured_data
        assert captured_data["output_format"] == "png"
        
        # Verify image file is included
        assert "image" in captured_files
    
    def test_try_on_response_parsing_and_image_extraction(self, monkeypatch):
        """Test response parsing and image extraction."""
        service = StableImageUltraService(api_key="test_key")
        
        # Create a test image
        test_image_bytes = create_test_image(800, 600, mode='RGB', format='PNG')
        
        # Create a specific mock result
        mock_result_image = create_test_image(1024, 1024, mode='RGB', format='PNG')
        mock_result_base64 = base64.b64encode(mock_result_image).decode('utf-8')
        
        class MockResponse:
            status_code = 200
            text = "Success"
            
            def json(self):
                return {
                    "id": "gen-12345",
                    "image": mock_result_base64,
                    "finish_reason": "SUCCESS",
                    "seed": 98765
                }
        
        def mock_post(*args, **kwargs):
            return MockResponse()
        
        monkeypatch.setattr(requests, "post", mock_post)
        
        # Call try_on_hairstyle
        result = service.try_on_hairstyle(
            user_image_bytes=test_image_bytes,
            hairstyle_description="bob cut",
            style_strength=0.4
        )
        
        # Verify result is extracted correctly
        assert result is not None
        assert result == mock_result_image
        
        # Verify it's a valid image
        result_image = Image.open(BytesIO(result))
        assert result_image.size == (1024, 1024)
    
    def test_try_on_with_api_error_response(self, monkeypatch):
        """Test try-on handles API error responses gracefully."""
        from stable_image_ultra_service import ServerError
        import time as time_module
        
        service = StableImageUltraService(api_key="test_key")
        
        # Create a test image
        test_image_bytes = create_test_image(800, 600, mode='RGB', format='PNG')
        
        class MockResponse:
            status_code = 500
            text = "Internal Server Error"
            
            def json(self):
                return {"error": "Internal server error"}
        
        def mock_post(*args, **kwargs):
            return MockResponse()
        
        # Mock time.sleep to avoid actual delay
        def mock_sleep(seconds):
            pass
        
        monkeypatch.setattr(requests, "post", mock_post)
        monkeypatch.setattr(time_module, "sleep", mock_sleep)
        
        # Should raise ServerError after retry fails
        with pytest.raises(ServerError):
            service.try_on_hairstyle(
                user_image_bytes=test_image_bytes,
                hairstyle_description="long straight hair",
                style_strength=0.35
            )
    
    def test_try_on_with_timeout(self, monkeypatch):
        """Test try-on handles timeout gracefully."""
        service = StableImageUltraService(api_key="test_key")
        
        # Create a test image
        test_image_bytes = create_test_image(800, 600, mode='RGB', format='PNG')
        
        def mock_post(*args, **kwargs):
            raise requests.exceptions.Timeout("Request timed out")
        
        monkeypatch.setattr(requests, "post", mock_post)
        
        # Should raise TimeoutError
        with pytest.raises(TimeoutError):
            service.try_on_hairstyle(
                user_image_bytes=test_image_bytes,
                hairstyle_description="afro hairstyle",
                style_strength=0.35
            )
    
    def test_try_on_with_missing_image_in_response(self, monkeypatch):
        """Test try-on handles missing image field in response."""
        service = StableImageUltraService(api_key="test_key")
        
        # Create a test image
        test_image_bytes = create_test_image(800, 600, mode='RGB', format='PNG')
        
        class MockResponse:
            status_code = 200
            text = "Success"
            
            def json(self):
                return {
                    "id": "gen-12345",
                    "finish_reason": "SUCCESS"
                    # Missing "image" field
                }
        
        def mock_post(*args, **kwargs):
            return MockResponse()
        
        monkeypatch.setattr(requests, "post", mock_post)
        
        # Should raise ValueError for invalid response
        with pytest.raises(ValueError):
            service.try_on_hairstyle(
                user_image_bytes=test_image_bytes,
                hairstyle_description="medium wavy hair",
                style_strength=0.35
            )
    
    def test_try_on_style_strength_validation(self):
        """Test that style_strength parameter is validated."""
        service = StableImageUltraService(api_key="test_key")
        
        # Create a test image
        test_image_bytes = create_test_image(800, 600, mode='RGB', format='PNG')
        
        # Test with invalid style_strength (too low)
        with pytest.raises(ValueError) as exc_info:
            service.try_on_hairstyle(
                user_image_bytes=test_image_bytes,
                hairstyle_description="short hair",
                style_strength=0.2  # Below 0.3
            )
        assert "style_strength must be between 0.3 and 0.5" in str(exc_info.value)
        
        # Test with invalid style_strength (too high)
        with pytest.raises(ValueError) as exc_info:
            service.try_on_hairstyle(
                user_image_bytes=test_image_bytes,
                hairstyle_description="short hair",
                style_strength=0.6  # Above 0.5
            )
        assert "style_strength must be between 0.3 and 0.5" in str(exc_info.value)
    
    def test_try_on_with_valid_style_strength_range(self, monkeypatch):
        """Test try-on works with valid style_strength values."""
        service = StableImageUltraService(api_key="test_key")
        
        # Create a test image
        test_image_bytes = create_test_image(800, 600, mode='RGB', format='PNG')
        
        class MockResponse:
            status_code = 200
            text = "Success"
            
            def json(self):
                return {
                    "image": base64.b64encode(create_test_image(512, 512)).decode('utf-8')
                }
        
        def mock_post(*args, **kwargs):
            return MockResponse()
        
        monkeypatch.setattr(requests, "post", mock_post)
        
        # Test with minimum valid value
        result = service.try_on_hairstyle(
            user_image_bytes=test_image_bytes,
            hairstyle_description="short hair",
            style_strength=0.3
        )
        assert result is not None
        
        # Test with maximum valid value
        result = service.try_on_hairstyle(
            user_image_bytes=test_image_bytes,
            hairstyle_description="short hair",
            style_strength=0.5
        )
        assert result is not None
        
        # Test with middle value
        result = service.try_on_hairstyle(
            user_image_bytes=test_image_bytes,
            hairstyle_description="short hair",
            style_strength=0.35
        )
        assert result is not None
    
    def test_try_on_endpoint_url_is_correct(self, monkeypatch):
        """Test that the correct Ultra API endpoint is used."""
        service = StableImageUltraService(api_key="test_key")
        
        # Create a test image
        test_image_bytes = create_test_image(800, 600, mode='RGB', format='PNG')
        
        # Track the URL used
        captured_url = []
        
        class MockResponse:
            status_code = 200
            text = "Success"
            
            def json(self):
                return {
                    "image": base64.b64encode(create_test_image(512, 512)).decode('utf-8')
                }
        
        def mock_post(url, *args, **kwargs):
            captured_url.append(url)
            return MockResponse()
        
        monkeypatch.setattr(requests, "post", mock_post)
        
        # Call try_on_hairstyle
        service.try_on_hairstyle(
            user_image_bytes=test_image_bytes,
            hairstyle_description="long hair",
            style_strength=0.35
        )
        
        # Verify correct endpoint was used
        assert len(captured_url) == 1
        assert captured_url[0] == "https://api.stability.ai/v2beta/stable-image/generate/ultra"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])


class TestErrorHandling:
    """Test comprehensive error handling - Task 5.1"""
    
    def test_401_authentication_error(self, monkeypatch):
        """Test handling of 401 authentication errors."""
        from stable_image_ultra_service import AuthenticationError
        
        service = StableImageUltraService(api_key="invalid_key")
        test_image_bytes = create_test_image(800, 600, mode='RGB', format='PNG')
        
        class MockResponse:
            status_code = 401
            text = "Unauthorized"
            
            def json(self):
                return {"error": "Invalid API key"}
        
        def mock_post(*args, **kwargs):
            return MockResponse()
        
        monkeypatch.setattr(requests, "post", mock_post)
        
        # Should raise AuthenticationError
        with pytest.raises(AuthenticationError) as exc_info:
            service.try_on_hairstyle(
                user_image_bytes=test_image_bytes,
                hairstyle_description="short hair",
                style_strength=0.35
            )
        
        # Verify user-friendly error message
        assert "authentication failed" in str(exc_info.value).lower()
        # Verify service is disabled
        assert service.enabled is False
    
    def test_402_insufficient_credits_error(self, monkeypatch):
        """Test handling of 402 insufficient credits errors."""
        from stable_image_ultra_service import InsufficientCreditsError
        
        service = StableImageUltraService(api_key="test_key")
        test_image_bytes = create_test_image(800, 600, mode='RGB', format='PNG')
        
        class MockResponse:
            status_code = 402
            text = "Payment Required"
            
            def json(self):
                return {"error": "Insufficient credits"}
        
        def mock_post(*args, **kwargs):
            return MockResponse()
        
        monkeypatch.setattr(requests, "post", mock_post)
        
        # Should raise InsufficientCreditsError
        with pytest.raises(InsufficientCreditsError) as exc_info:
            service.try_on_hairstyle(
                user_image_bytes=test_image_bytes,
                hairstyle_description="long hair",
                style_strength=0.35
            )
        
        # Verify user-friendly error message
        assert "insufficient credits" in str(exc_info.value).lower()
    
    def test_429_rate_limit_error(self, monkeypatch):
        """Test handling of 429 rate limit errors with retry suggestion."""
        from stable_image_ultra_service import RateLimitError
        
        service = StableImageUltraService(api_key="test_key")
        test_image_bytes = create_test_image(800, 600, mode='RGB', format='PNG')
        
        class MockResponse:
            status_code = 429
            text = "Too Many Requests"
            
            def json(self):
                return {"error": "Rate limit exceeded"}
        
        def mock_post(*args, **kwargs):
            return MockResponse()
        
        monkeypatch.setattr(requests, "post", mock_post)
        
        # Should raise RateLimitError
        with pytest.raises(RateLimitError) as exc_info:
            service.try_on_hairstyle(
                user_image_bytes=test_image_bytes,
                hairstyle_description="curly hair",
                style_strength=0.35
            )
        
        # Verify user-friendly error message with retry suggestion
        error_msg = str(exc_info.value).lower()
        assert "too many requests" in error_msg or "rate limit" in error_msg
        assert "try again" in error_msg or "wait" in error_msg
    
    def test_400_validation_error(self, monkeypatch):
        """Test handling of 400 validation errors."""
        from stable_image_ultra_service import ValidationError
        
        service = StableImageUltraService(api_key="test_key")
        test_image_bytes = create_test_image(800, 600, mode='RGB', format='PNG')
        
        class MockResponse:
            status_code = 400
            text = "Bad Request"
            
            def json(self):
                return {"error": "Invalid parameters", "message": "Image format not supported"}
        
        def mock_post(*args, **kwargs):
            return MockResponse()
        
        monkeypatch.setattr(requests, "post", mock_post)
        
        # Should raise ValidationError
        with pytest.raises(ValidationError) as exc_info:
            service.try_on_hairstyle(
                user_image_bytes=test_image_bytes,
                hairstyle_description="wavy hair",
                style_strength=0.35
            )
        
        # Verify user-friendly error message
        assert "validation failed" in str(exc_info.value).lower()
    
    def test_500_server_error_with_retry(self, monkeypatch):
        """Test handling of 500 server errors with retry logic."""
        from stable_image_ultra_service import ServerError
        import time as time_module
        
        service = StableImageUltraService(api_key="test_key")
        test_image_bytes = create_test_image(800, 600, mode='RGB', format='PNG')
        
        call_count = [0]
        
        class MockResponse:
            def __init__(self):
                call_count[0] += 1
                # First call fails, second succeeds
                if call_count[0] == 1:
                    self.status_code = 500
                    self.text = "Internal Server Error"
                else:
                    self.status_code = 200
                    self.text = "Success"
            
            def json(self):
                if self.status_code == 500:
                    return {"error": "Internal server error"}
                else:
                    return {
                        "image": base64.b64encode(create_test_image(512, 512)).decode('utf-8')
                    }
        
        def mock_post(*args, **kwargs):
            return MockResponse()
        
        # Mock time.sleep to avoid actual delay
        def mock_sleep(seconds):
            pass
        
        monkeypatch.setattr(requests, "post", mock_post)
        monkeypatch.setattr(time_module, "sleep", mock_sleep)
        
        # Should succeed on retry
        result = service.try_on_hairstyle(
            user_image_bytes=test_image_bytes,
            hairstyle_description="straight hair",
            style_strength=0.35
        )
        
        # Verify retry was attempted and succeeded
        assert call_count[0] == 2  # First call + retry
        assert result is not None
    
    def test_500_server_error_retry_fails(self, monkeypatch):
        """Test handling of 500 server errors when retry also fails."""
        from stable_image_ultra_service import ServerError
        import time as time_module
        
        service = StableImageUltraService(api_key="test_key")
        test_image_bytes = create_test_image(800, 600, mode='RGB', format='PNG')
        
        class MockResponse:
            status_code = 500
            text = "Internal Server Error"
            
            def json(self):
                return {"error": "Internal server error"}
        
        def mock_post(*args, **kwargs):
            return MockResponse()
        
        # Mock time.sleep to avoid actual delay
        def mock_sleep(seconds):
            pass
        
        monkeypatch.setattr(requests, "post", mock_post)
        monkeypatch.setattr(time_module, "sleep", mock_sleep)
        
        # Should raise ServerError after retry fails
        with pytest.raises(ServerError) as exc_info:
            service.try_on_hairstyle(
                user_image_bytes=test_image_bytes,
                hairstyle_description="braided hair",
                style_strength=0.35
            )
        
        # Verify user-friendly error message
        error_msg = str(exc_info.value).lower()
        assert "temporarily unavailable" in error_msg or "service" in error_msg
    
    def test_503_service_unavailable_error(self, monkeypatch):
        """Test handling of 503 service unavailable errors."""
        from stable_image_ultra_service import ServerError
        import time as time_module
        
        service = StableImageUltraService(api_key="test_key")
        test_image_bytes = create_test_image(800, 600, mode='RGB', format='PNG')
        
        class MockResponse:
            status_code = 503
            text = "Service Unavailable"
            
            def json(self):
                return {"error": "Service temporarily unavailable"}
        
        def mock_post(*args, **kwargs):
            return MockResponse()
        
        # Mock time.sleep to avoid actual delay
        def mock_sleep(seconds):
            pass
        
        monkeypatch.setattr(requests, "post", mock_post)
        monkeypatch.setattr(time_module, "sleep", mock_sleep)
        
        # Should raise ServerError
        with pytest.raises(ServerError) as exc_info:
            service.try_on_hairstyle(
                user_image_bytes=test_image_bytes,
                hairstyle_description="ponytail",
                style_strength=0.35
            )
        
        # Verify user-friendly error message
        error_msg = str(exc_info.value).lower()
        assert "unavailable" in error_msg or "temporarily" in error_msg
    
    def test_timeout_handling(self, monkeypatch):
        """Test timeout handling for requests exceeding 60 seconds."""
        service = StableImageUltraService(api_key="test_key")
        test_image_bytes = create_test_image(800, 600, mode='RGB', format='PNG')
        
        def mock_post(*args, **kwargs):
            raise requests.exceptions.Timeout("Request timed out after 60 seconds")
        
        monkeypatch.setattr(requests, "post", mock_post)
        
        # Should raise TimeoutError
        with pytest.raises(TimeoutError) as exc_info:
            service.try_on_hairstyle(
                user_image_bytes=test_image_bytes,
                hairstyle_description="mohawk",
                style_strength=0.35
            )
        
        # Verify user-friendly error message
        error_msg = str(exc_info.value).lower()
        assert "taking too long" in error_msg or "timeout" in error_msg or "try again" in error_msg
    
    def test_connection_error_handling(self, monkeypatch):
        """Test handling of connection errors."""
        service = StableImageUltraService(api_key="test_key")
        test_image_bytes = create_test_image(800, 600, mode='RGB', format='PNG')
        
        def mock_post(*args, **kwargs):
            raise requests.exceptions.ConnectionError("Failed to establish connection")
        
        monkeypatch.setattr(requests, "post", mock_post)
        
        # Should raise ConnectionError
        with pytest.raises(ConnectionError) as exc_info:
            service.try_on_hairstyle(
                user_image_bytes=test_image_bytes,
                hairstyle_description="buzz cut",
                style_strength=0.35
            )
        
        # Verify user-friendly error message
        error_msg = str(exc_info.value).lower()
        assert "connect" in error_msg or "internet" in error_msg
    
    def test_error_logging_on_failure(self, monkeypatch, caplog):
        """Test that errors are logged with full details for debugging."""
        import logging
        import time as time_module
        
        service = StableImageUltraService(api_key="test_key")
        test_image_bytes = create_test_image(800, 600, mode='RGB', format='PNG')
        
        class MockResponse:
            status_code = 500
            text = "Internal Server Error - Database connection failed"
            
            def json(self):
                return {"error": "Database error"}
        
        def mock_post(*args, **kwargs):
            return MockResponse()
        
        # Mock time.sleep to avoid actual delay
        def mock_sleep(seconds):
            pass
        
        monkeypatch.setattr(requests, "post", mock_post)
        monkeypatch.setattr(time_module, "sleep", mock_sleep)
        
        # Capture logs
        with caplog.at_level(logging.ERROR):
            try:
                service.try_on_hairstyle(
                    user_image_bytes=test_image_bytes,
                    hairstyle_description="dreadlocks",
                    style_strength=0.35
                )
            except:
                pass
        
        # Verify error was logged
        assert len(caplog.records) > 0
        # Check that error details are in logs
        log_messages = " ".join([record.message for record in caplog.records])
        assert "500" in log_messages or "error" in log_messages.lower()
    
    def test_user_friendly_error_messages_no_technical_details(self, monkeypatch):
        """Test that user-friendly error messages don't expose technical details."""
        from stable_image_ultra_service import AuthenticationError
        
        service = StableImageUltraService(api_key="test_key")
        test_image_bytes = create_test_image(800, 600, mode='RGB', format='PNG')
        
        class MockResponse:
            status_code = 401
            text = "Unauthorized - API key sk_test_12345 is invalid for endpoint /v2beta/stable-image/generate/ultra"
            
            def json(self):
                return {"error": "Invalid API key"}
        
        def mock_post(*args, **kwargs):
            return MockResponse()
        
        monkeypatch.setattr(requests, "post", mock_post)
        
        # Should raise AuthenticationError
        with pytest.raises(AuthenticationError) as exc_info:
            service.try_on_hairstyle(
                user_image_bytes=test_image_bytes,
                hairstyle_description="afro",
                style_strength=0.35
            )
        
        # Verify error message is user-friendly and doesn't contain technical details
        error_msg = str(exc_info.value)
        assert "sk_test" not in error_msg  # No API key exposed
        assert "/v2beta" not in error_msg  # No endpoint exposed
        assert "authentication" in error_msg.lower()  # User-friendly message
    
    def test_check_api_status_handles_401(self, monkeypatch):
        """Test check_api_status handles 401 errors."""
        service = StableImageUltraService(api_key="invalid_key")
        
        class MockResponse:
            status_code = 401
            text = "Unauthorized"
        
        def mock_get(*args, **kwargs):
            return MockResponse()
        
        monkeypatch.setattr(requests, "get", mock_get)
        
        status = service.check_api_status()
        
        assert status["status"] == "error"
        assert status["enabled"] is False
        assert "authentication" in status["message"].lower()
        assert status["error_code"] == "AUTH_FAILED"
    
    def test_check_api_status_handles_402(self, monkeypatch):
        """Test check_api_status handles 402 errors."""
        service = StableImageUltraService(api_key="test_key")
        
        class MockResponse:
            status_code = 402
            text = "Payment Required"
        
        def mock_get(*args, **kwargs):
            return MockResponse()
        
        monkeypatch.setattr(requests, "get", mock_get)
        
        status = service.check_api_status()
        
        assert status["status"] == "error"
        assert status["enabled"] is False
        assert "insufficient credits" in status["message"].lower()
        assert status["error_code"] == "INSUFFICIENT_CREDITS"
    
    def test_check_api_status_handles_429(self, monkeypatch):
        """Test check_api_status handles 429 errors."""
        service = StableImageUltraService(api_key="test_key")
        
        class MockResponse:
            status_code = 429
            text = "Too Many Requests"
        
        def mock_get(*args, **kwargs):
            return MockResponse()
        
        monkeypatch.setattr(requests, "get", mock_get)
        
        status = service.check_api_status()
        
        assert status["status"] == "error"
        assert status["enabled"] is False
        assert "rate limit" in status["message"].lower()
        assert status["error_code"] == "RATE_LIMIT"
    
    def test_check_api_status_handles_500(self, monkeypatch):
        """Test check_api_status handles 500 errors."""
        service = StableImageUltraService(api_key="test_key")
        
        class MockResponse:
            status_code = 500
            text = "Internal Server Error"
        
        def mock_get(*args, **kwargs):
            return MockResponse()
        
        monkeypatch.setattr(requests, "get", mock_get)
        
        status = service.check_api_status()
        
        assert status["status"] == "error"
        assert status["enabled"] is False
        assert "unavailable" in status["message"].lower()
        assert status["error_code"] == "SERVER_ERROR"
    
    def test_check_api_status_handles_503(self, monkeypatch):
        """Test check_api_status handles 503 errors."""
        service = StableImageUltraService(api_key="test_key")
        
        class MockResponse:
            status_code = 503
            text = "Service Unavailable"
        
        def mock_get(*args, **kwargs):
            return MockResponse()
        
        monkeypatch.setattr(requests, "get", mock_get)
        
        status = service.check_api_status()
        
        assert status["status"] == "error"
        assert status["enabled"] is False
        assert "unavailable" in status["message"].lower()
        assert status["error_code"] == "SERVER_ERROR"
    
    def test_check_api_status_handles_timeout(self, monkeypatch):
        """Test check_api_status handles timeout errors."""
        service = StableImageUltraService(api_key="test_key")
        
        def mock_get(*args, **kwargs):
            raise requests.exceptions.Timeout("Request timed out")
        
        monkeypatch.setattr(requests, "get", mock_get)
        
        status = service.check_api_status()
        
        assert status["status"] == "error"
        assert status["enabled"] is False
        assert "timed out" in status["message"].lower() or "timeout" in status["message"].lower()
        assert status["error_code"] == "TIMEOUT"
    
    def test_check_api_status_handles_connection_error(self, monkeypatch):
        """Test check_api_status handles connection errors."""
        service = StableImageUltraService(api_key="test_key")
        
        def mock_get(*args, **kwargs):
            raise requests.exceptions.ConnectionError("Failed to connect")
        
        monkeypatch.setattr(requests, "get", mock_get)
        
        status = service.check_api_status()
        
        assert status["status"] == "error"
        assert status["enabled"] is False
        assert "connect" in status["message"].lower()
        assert status["error_code"] == "CONNECTION_ERROR"
    
    def test_invalid_response_format_handling(self, monkeypatch):
        """Test handling of invalid response format from API."""
        service = StableImageUltraService(api_key="test_key")
        test_image_bytes = create_test_image(800, 600, mode='RGB', format='PNG')
        
        class MockResponse:
            status_code = 200
            text = "Success"
            
            def json(self):
                # Return response without 'image' field
                return {
                    "id": "gen-12345",
                    "finish_reason": "SUCCESS"
                }
        
        def mock_post(*args, **kwargs):
            return MockResponse()
        
        monkeypatch.setattr(requests, "post", mock_post)
        
        # Should raise ValueError for invalid response
        with pytest.raises(ValueError) as exc_info:
            service.try_on_hairstyle(
                user_image_bytes=test_image_bytes,
                hairstyle_description="bob cut",
                style_strength=0.35
            )
        
        # Verify error message
        error_msg = str(exc_info.value).lower()
        assert "invalid response" in error_msg or "process" in error_msg or "response" in error_msg
    
    def test_image_preprocessing_error_handling(self):
        """Test that image preprocessing errors are handled properly."""
        service = StableImageUltraService(api_key="test_key")
        
        # Try with invalid image data
        with pytest.raises(ValueError) as exc_info:
            service.try_on_hairstyle(
                user_image_bytes=b"not a valid image",
                hairstyle_description="short hair",
                style_strength=0.35
            )
        
        # Verify error message is user-friendly
        error_msg = str(exc_info.value).lower()
        assert "failed to process image" in error_msg or "image" in error_msg


class TestVariationsGeneration:
    """Test variations generation functionality - Task 6.1"""
    
    def test_generate_variations_with_different_strengths(self, monkeypatch):
        """Test variations are generated with different style strengths."""
        service = StableImageUltraService(api_key="test_key")
        
        # Create a test image
        test_image_bytes = create_test_image(800, 600, mode='RGB', format='PNG')
        
        # Track the style strengths used
        captured_strengths = []
        
        # Create mock responses for each variation
        def create_mock_result(strength):
            # Create slightly different images for each strength
            size = int(512 + strength * 100)  # Different sizes to distinguish
            return create_test_image(size, size, mode='RGB', format='PNG')
        
        class MockResponse:
            def __init__(self, strength):
                self.status_code = 200
                self.text = "Success"
                self.strength = strength
            
            def json(self):
                return {
                    "image": base64.b64encode(create_mock_result(self.strength)).decode('utf-8')
                }
        
        def mock_post(*args, **kwargs):
            # Extract style_strength from the data (not used in this mock, but captured)
            # We'll track calls instead
            return MockResponse(len(captured_strengths) * 0.05 + 0.3)
        
        # Mock try_on_hairstyle to capture strengths
        original_try_on = service.try_on_hairstyle
        
        def mock_try_on(user_image_bytes, hairstyle_description, style_strength):
            captured_strengths.append(style_strength)
            # Create a unique result for each strength
            return create_mock_result(style_strength)
        
        monkeypatch.setattr(service, "try_on_hairstyle", mock_try_on)
        
        # Generate 4 variations
        results = service.generate_variations(
            user_image_bytes=test_image_bytes,
            hairstyle_description="long wavy hair",
            num_variations=4
        )
        
        # Verify 4 different strengths were used
        assert len(captured_strengths) == 4
        assert captured_strengths == [0.3, 0.35, 0.4, 0.45]
        
        # Verify 4 results were returned
        assert len(results) == 4
    
    def test_generate_variations_maximum_of_4(self, monkeypatch):
        """Test maximum of 4 variations is enforced."""
        service = StableImageUltraService(api_key="test_key")
        
        # Create a test image
        test_image_bytes = create_test_image(800, 600, mode='RGB', format='PNG')
        
        # Track calls
        call_count = [0]
        
        def mock_try_on(user_image_bytes, hairstyle_description, style_strength):
            call_count[0] += 1
            return create_test_image(512, 512, mode='RGB', format='PNG')
        
        monkeypatch.setattr(service, "try_on_hairstyle", mock_try_on)
        
        # Try to request more than 4 variations
        results = service.generate_variations(
            user_image_bytes=test_image_bytes,
            hairstyle_description="short curly hair",
            num_variations=10  # Request 10, should be limited to 4
        )
        
        # Verify only 4 variations were generated
        assert call_count[0] == 4
        assert len(results) == 4
    
    def test_generate_variations_all_returned(self, monkeypatch):
        """Test all variations are returned successfully."""
        service = StableImageUltraService(api_key="test_key")
        
        # Create a test image
        test_image_bytes = create_test_image(800, 600, mode='RGB', format='PNG')
        
        # Create unique results for each variation
        def mock_try_on(user_image_bytes, hairstyle_description, style_strength):
            # Create a unique image for each strength
            size = int(512 + style_strength * 1000)
            return create_test_image(size, size, mode='RGB', format='PNG')
        
        monkeypatch.setattr(service, "try_on_hairstyle", mock_try_on)
        
        # Generate variations
        results = service.generate_variations(
            user_image_bytes=test_image_bytes,
            hairstyle_description="medium length hair",
            num_variations=4
        )
        
        # Verify all 4 results are returned
        assert len(results) == 4
        
        # Verify each result is valid image bytes
        for result in results:
            assert isinstance(result, bytes)
            assert len(result) > 0
            # Verify it's a valid image
            img = Image.open(BytesIO(result))
            assert img.size[0] > 0
            assert img.size[1] > 0
    
    def test_generate_variations_with_mock_api_calls(self, monkeypatch):
        """Test variations generation with mocked API calls."""
        service = StableImageUltraService(api_key="test_key")
        
        # Create a test image
        test_image_bytes = create_test_image(800, 600, mode='RGB', format='PNG')
        
        # Track API calls
        api_calls = []
        
        class MockResponse:
            status_code = 200
            text = "Success"
            
            def json(self):
                return {
                    "image": base64.b64encode(create_test_image(512, 512)).decode('utf-8')
                }
        
        def mock_post(*args, **kwargs):
            api_calls.append({
                'url': args[0] if args else kwargs.get('url'),
                'data': kwargs.get('data', {})
            })
            return MockResponse()
        
        monkeypatch.setattr(requests, "post", mock_post)
        
        # Generate variations
        results = service.generate_variations(
            user_image_bytes=test_image_bytes,
            hairstyle_description="pixie cut",
            num_variations=4
        )
        
        # Verify 4 API calls were made
        assert len(api_calls) == 4
        
        # Verify 4 results were returned
        assert len(results) == 4
        
        # Verify all results are valid
        for result in results:
            assert isinstance(result, bytes)
            assert len(result) > 0
    
    def test_generate_variations_handles_partial_failures(self, monkeypatch):
        """Test that variations generation continues even if some fail."""
        service = StableImageUltraService(api_key="test_key")
        
        # Create a test image
        test_image_bytes = create_test_image(800, 600, mode='RGB', format='PNG')
        
        # Track calls
        call_count = [0]
        
        def mock_try_on(user_image_bytes, hairstyle_description, style_strength):
            call_count[0] += 1
            # Fail on the 2nd variation
            if call_count[0] == 2:
                raise Exception("API error for this variation")
            return create_test_image(512, 512, mode='RGB', format='PNG')
        
        monkeypatch.setattr(service, "try_on_hairstyle", mock_try_on)
        
        # Generate variations
        results = service.generate_variations(
            user_image_bytes=test_image_bytes,
            hairstyle_description="bob cut",
            num_variations=4
        )
        
        # Verify 4 attempts were made
        assert call_count[0] == 4
        
        # Verify 3 results were returned (1 failed)
        assert len(results) == 3
    
    def test_generate_variations_with_fewer_than_4(self, monkeypatch):
        """Test generating fewer than 4 variations."""
        service = StableImageUltraService(api_key="test_key")
        
        # Create a test image
        test_image_bytes = create_test_image(800, 600, mode='RGB', format='PNG')
        
        # Track calls
        call_count = [0]
        
        def mock_try_on(user_image_bytes, hairstyle_description, style_strength):
            call_count[0] += 1
            return create_test_image(512, 512, mode='RGB', format='PNG')
        
        monkeypatch.setattr(service, "try_on_hairstyle", mock_try_on)
        
        # Generate only 2 variations
        results = service.generate_variations(
            user_image_bytes=test_image_bytes,
            hairstyle_description="afro",
            num_variations=2
        )
        
        # Verify only 2 variations were generated
        assert call_count[0] == 2
        assert len(results) == 2
    
    def test_generate_variations_validates_num_variations(self, monkeypatch):
        """Test that num_variations parameter is validated."""
        service = StableImageUltraService(api_key="test_key")
        
        # Create a test image
        test_image_bytes = create_test_image(800, 600, mode='RGB', format='PNG')
        
        # Test with invalid num_variations (zero)
        with pytest.raises(ValueError) as exc_info:
            service.generate_variations(
                user_image_bytes=test_image_bytes,
                hairstyle_description="short hair",
                num_variations=0
            )
        assert "num_variations must be at least 1" in str(exc_info.value)
        
        # Test with invalid num_variations (negative)
        with pytest.raises(ValueError) as exc_info:
            service.generate_variations(
                user_image_bytes=test_image_bytes,
                hairstyle_description="short hair",
                num_variations=-1
            )
        assert "num_variations must be at least 1" in str(exc_info.value)
        
        # Test with num_variations > 4 (should be clamped to 4, not error)
        call_count = [0]
        
        def mock_try_on(user_image_bytes, hairstyle_description, style_strength):
            call_count[0] += 1
            return create_test_image(512, 512, mode='RGB', format='PNG')
        
        monkeypatch.setattr(service, "try_on_hairstyle", mock_try_on)
        
        # Request 10 variations, should be clamped to 4
        results = service.generate_variations(
            user_image_bytes=test_image_bytes,
            hairstyle_description="short hair",
            num_variations=10
        )
        
        # Verify only 4 were generated
        assert call_count[0] == 4
        assert len(results) == 4
    
    def test_generate_variations_uses_correct_strengths(self, monkeypatch):
        """Test that variations use the correct predefined strengths."""
        service = StableImageUltraService(api_key="test_key")
        
        # Create a test image
        test_image_bytes = create_test_image(800, 600, mode='RGB', format='PNG')
        
        # Track the strengths used
        captured_strengths = []
        
        def mock_try_on(user_image_bytes, hairstyle_description, style_strength):
            captured_strengths.append(style_strength)
            return create_test_image(512, 512, mode='RGB', format='PNG')
        
        monkeypatch.setattr(service, "try_on_hairstyle", mock_try_on)
        
        # Generate 3 variations
        service.generate_variations(
            user_image_bytes=test_image_bytes,
            hairstyle_description="wavy hair",
            num_variations=3
        )
        
        # Verify the first 3 strengths were used
        assert captured_strengths == [0.3, 0.35, 0.4]
    
    def test_generate_variations_returns_empty_list_on_all_failures(self, monkeypatch):
        """Test that empty list is returned if all variations fail."""
        service = StableImageUltraService(api_key="test_key")
        
        # Create a test image
        test_image_bytes = create_test_image(800, 600, mode='RGB', format='PNG')
        
        def mock_try_on(user_image_bytes, hairstyle_description, style_strength):
            raise Exception("API error")
        
        monkeypatch.setattr(service, "try_on_hairstyle", mock_try_on)
        
        # Generate variations
        results = service.generate_variations(
            user_image_bytes=test_image_bytes,
            hairstyle_description="dreadlocks",
            num_variations=4
        )
        
        # Verify empty list is returned
        assert len(results) == 0
        assert results == []
