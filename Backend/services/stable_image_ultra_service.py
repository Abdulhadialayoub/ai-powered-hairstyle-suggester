"""
Stable Image Ultra Service

Integrates Stability AI's Stable Image Ultra model for high-quality virtual hair try-on.
Ultra provides superior photorealism, better face preservation, and enhanced detail.

Setup:
1. Get API key: https://platform.stability.ai/account/keys
2. Set environment variable: STABILITY_API_KEY=your_key

Pricing: $0.08 per image
API Documentation: https://platform.stability.ai/docs/api-reference#tag/Generate/paths/~1v2beta~1stable-image~1generate~1ultra/post
"""

import os
import logging
from typing import Dict, Optional, List
import requests
import base64
from io import BytesIO
from PIL import Image
import time
from datetime import datetime
from .usage_tracker import UsageTracker


# Custom exception classes for specific error handling
class AuthenticationError(Exception):
    """Raised when API authentication fails (401)."""
    pass


class InsufficientCreditsError(Exception):
    """Raised when account has insufficient credits (402)."""
    pass


class RateLimitError(Exception):
    """Raised when rate limit is exceeded (429)."""
    pass


class ValidationError(Exception):
    """Raised when request parameters are invalid (400)."""
    pass


class ServerError(Exception):
    """Raised when Stability AI service has issues (500, 503)."""
    pass


# Configure logging
logger = logging.getLogger('stable_image_ultra')
logger.setLevel(logging.INFO)

# Create formatter
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# File handler
file_handler = logging.FileHandler('stable_image_ultra.log')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)


class StableImageUltraService:
    """
    Service for applying hairstyles using Stable Image Ultra.
    
    Provides high-quality, photorealistic virtual try-on with excellent
    face preservation and hair detail.
    """
    
    # Maximum dimension for images (Ultra API limit)
    MAX_IMAGE_SIZE = 1536
    
    def __init__(self, api_key: str = None, usage_tracker: UsageTracker = None):
        """
        Initialize Stable Image Ultra service.
        
        Args:
            api_key: Stability AI API key. If not provided, reads from
                    STABILITY_API_KEY environment variable.
            usage_tracker: UsageTracker instance for logging API calls.
                          If not provided, creates a new instance.
        
        Raises:
            ValueError: If API key is not provided and not in environment.
        """
        self.api_key = api_key or os.environ.get('STABILITY_API_KEY')
        
        if not self.api_key:
            error_msg = (
                "STABILITY_API_KEY not found in environment. "
                "Get your key from https://platform.stability.ai/account/keys"
            )
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        self.api_host = "https://api.stability.ai"
        self.ultra_endpoint = f"{self.api_host}/v2beta/stable-image/generate/ultra"
        self.enabled = True
        
        # Initialize usage tracker
        self.usage_tracker = usage_tracker or UsageTracker()
        
        logger.info("StableImageUltraService initialized successfully")
    
    def _preprocess_image(self, image_bytes: bytes) -> Image.Image:
        """
        Preprocess image for API submission.
        
        Performs the following operations:
        1. Load and validate image from bytes
        2. Convert RGBA to RGB if needed
        3. Resize if dimensions exceed MAX_IMAGE_SIZE while maintaining aspect ratio
        4. Use high-quality LANCZOS resampling for resizing
        
        Args:
            image_bytes: Raw image data as bytes
        
        Returns:
            PIL Image object ready for API submission
        
        Raises:
            ValueError: If image cannot be loaded or is invalid
        """
        try:
            # Load image from bytes
            image = Image.open(BytesIO(image_bytes))
            logger.info(f"Loaded image: {image.format} {image.size} {image.mode}")
            
            # Convert RGBA to RGB if needed (remove alpha channel)
            if image.mode == 'RGBA':
                logger.info("Converting RGBA to RGB")
                # Create white background
                rgb_image = Image.new('RGB', image.size, (255, 255, 255))
                # Paste image using alpha channel as mask
                rgb_image.paste(image, mask=image.split()[3])
                image = rgb_image
            elif image.mode != 'RGB':
                logger.info(f"Converting {image.mode} to RGB")
                image = image.convert('RGB')
            
            # Resize if too large, maintaining aspect ratio
            if image.width > self.MAX_IMAGE_SIZE or image.height > self.MAX_IMAGE_SIZE:
                original_size = image.size
                # Use thumbnail to maintain aspect ratio
                image.thumbnail((self.MAX_IMAGE_SIZE, self.MAX_IMAGE_SIZE), Image.Resampling.LANCZOS)
                logger.info(f"Resized image from {original_size} to {image.size}")
            
            return image
        
        except Exception as e:
            error_msg = f"Failed to preprocess image: {str(e)}"
            logger.error(error_msg, exc_info=True)
            raise ValueError(error_msg)
    
    def _encode_image_to_base64(self, image: Image.Image) -> str:
        """
        Encode PIL Image to base64 string.
        
        Args:
            image: PIL Image object
        
        Returns:
            Base64-encoded string of the image
        """
        buffer = BytesIO()
        image.save(buffer, format='PNG')
        buffer.seek(0)
        return base64.b64encode(buffer.read()).decode('utf-8')
    
    def _build_prompt(self, hairstyle_description: str) -> str:
        """
        Build optimized prompt for face preservation and quality.
        
        Constructs a prompt that emphasizes:
        - Face preservation (same person, same facial features)
        - Hairstyle description
        - Quality-enhancing keywords (photorealistic, high detail, etc.)
        
        Args:
            hairstyle_description: Description of the desired hairstyle
        
        Returns:
            Complete prompt string optimized for Stable Image Ultra
        """
        prompt = (
            f"professional portrait photograph, "
            f"{hairstyle_description}, "
            f"same person, same facial features, same face structure, "
            f"same gender, same skin tone, same eye color, "
            f"photorealistic, high detail, natural lighting, "
            f"8k uhd, sharp focus"
        )
        
        logger.info(f"Built prompt: {prompt}")
        return prompt
    
    def _build_negative_prompt(self) -> str:
        """
        Build negative prompt to avoid unwanted changes.
        
        Specifies what should NOT appear in the generated image:
        - Different person or face changes
        - Multiple people or faces
        - Low quality or distorted results
        - Non-photographic styles
        
        Returns:
            Negative prompt string with unwanted keywords
        """
        negative_prompt = (
            "different person, different face, face change, "
            "multiple people, multiple faces, "
            "blurry, low quality, distorted, "
            "cartoon, anime, drawing, painting, "
            "deformed, disfigured, bad anatomy"
        )
        
        logger.info(f"Built negative prompt: {negative_prompt}")
        return negative_prompt
    
    def try_on_hairstyle(
        self,
        user_image_bytes: bytes,
        hairstyle_description: str,
        style_strength: float = 0.35,
        user_session: str = "anonymous",
        hairstyle_id: str = "unknown"
    ) -> Optional[bytes]:
        """
        Apply hairstyle using Stable Image Ultra.
        
        Performs the following operations:
        1. Preprocess the user's image
        2. Build optimized prompts for face preservation
        3. Send HTTPS POST request to Ultra API endpoint
        4. Handle API response and extract generated image
        5. Return generated image as bytes
        6. Log usage for tracking and cost estimation
        
        Args:
            user_image_bytes: User's photo as bytes
            hairstyle_description: Description of desired hairstyle
            style_strength: How much to modify (0.3-0.5, default 0.35)
            user_session: Anonymized user session identifier (for tracking)
            hairstyle_id: ID of the hairstyle being tried on (for tracking)
        
        Returns:
            Generated image as bytes, or None if failed
        
        Raises:
            ValueError: If style_strength is outside valid range or image preprocessing fails
            AuthenticationError: If API key is invalid (401)
            InsufficientCreditsError: If account has insufficient credits (402)
            RateLimitError: If rate limit is exceeded (429)
            ValidationError: If request parameters are invalid (400)
            ServerError: If Stability AI service has issues (500, 503)
            TimeoutError: If request exceeds 60 seconds
        """
        # Track start time for processing time calculation
        start_time = time.time()
        success = False
        error_message = None
        result = None
        
        # Validate style strength parameter
        if not (0.3 <= style_strength <= 0.5):
            error_msg = "style_strength must be between 0.3 and 0.5"
            logger.error(f"Validation error: {error_msg}")
            raise ValueError(error_msg)
        
        try:
            logger.info(f"Starting try-on with hairstyle: {hairstyle_description}, strength: {style_strength}")
            
            # Step 1: Preprocess the image
            try:
                preprocessed_image = self._preprocess_image(user_image_bytes)
            except ValueError as e:
                logger.error(f"Image preprocessing failed: {str(e)}", exc_info=True)
                error_message = "ImagePreprocessingError"
                raise ValueError(f"Failed to process image: {str(e)}")
            
            # Step 2: Build prompts
            prompt = self._build_prompt(hairstyle_description)
            negative_prompt = self._build_negative_prompt()
            
            # Step 3: Prepare image for API (convert to bytes)
            image_buffer = BytesIO()
            preprocessed_image.save(image_buffer, format='PNG')
            image_buffer.seek(0)
            
            # Step 4: Set up HTTPS POST request to Ultra API endpoint
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Accept": "application/json"
            }
            
            # Prepare multipart form data
            files = {
                "image": ("image.png", image_buffer, "image/png")
            }
            
            data = {
                "prompt": prompt,
                "negative_prompt": negative_prompt,
                "strength": style_strength,  # Required when image is provided
                "output_format": "png",
                "aspect_ratio": "1:1"  # Maintain square aspect for consistency
            }
            
            logger.info(f"Sending request to Ultra API endpoint: {self.ultra_endpoint}")
            
            # Step 5: Send request with 60 second timeout
            try:
                response = requests.post(
                    self.ultra_endpoint,
                    headers=headers,
                    files=files,
                    data=data,
                    timeout=60
                )
            except requests.exceptions.Timeout:
                error_msg = "Request timed out after 60 seconds"
                logger.error(f"Timeout error: {error_msg}")
                error_message = "TimeoutError"
                raise TimeoutError("The AI service is taking too long to respond. Please try again in a moment.")
            except requests.exceptions.ConnectionError as e:
                error_msg = f"Connection error: {str(e)}"
                logger.error(error_msg, exc_info=True)
                error_message = "ConnectionError"
                raise ConnectionError("Unable to connect to the AI service. Please check your internet connection and try again.")
            except requests.exceptions.RequestException as e:
                error_msg = f"Request error: {str(e)}"
                logger.error(error_msg, exc_info=True)
                error_message = "RequestError"
                raise Exception("An error occurred while communicating with the AI service. Please try again.")
            
            # Step 6: Handle API response based on status code
            if response.status_code == 200:
                logger.info("API request successful")
                
                try:
                    # Parse JSON response
                    response_data = response.json()
                    
                    # Extract base64 image data
                    if "image" in response_data:
                        # Decode base64 image data
                        image_base64 = response_data["image"]
                        image_bytes = base64.b64decode(image_base64)
                        
                        logger.info(f"Successfully generated image, size: {len(image_bytes)} bytes")
                        success = True
                        result = image_bytes
                        return image_bytes
                    else:
                        error_msg = "Response missing 'image' field"
                        logger.error(f"Invalid response format: {error_msg}")
                        raise ValueError("Received invalid response from AI service")
                
                except (ValueError, KeyError) as e:
                    error_msg = f"Failed to parse API response: {str(e)}"
                    logger.error(error_msg, exc_info=True)
                    error_message = "ResponseParseError"
                    raise ValueError("Failed to process AI service response")
            
            # Handle authentication errors (401)
            elif response.status_code == 401:
                error_msg = f"Authentication failed: {response.text}"
                logger.error(error_msg)
                self.enabled = False
                error_message = "AuthenticationError"
                raise AuthenticationError("AI service authentication failed. Please contact support.")
            
            # Handle insufficient credits errors (402)
            elif response.status_code == 402:
                error_msg = f"Insufficient credits: {response.text}"
                logger.error(error_msg)
                error_message = "InsufficientCreditsError"
                raise InsufficientCreditsError("The AI service has insufficient credits. Please contact support.")
            
            # Handle validation errors (400)
            elif response.status_code == 400:
                error_msg = f"Validation error: {response.text}"
                logger.error(error_msg)
                try:
                    error_details = response.json()
                    error_detail = error_details.get('message', 'Invalid request parameters')
                except:
                    error_detail = 'Invalid request parameters'
                error_message = "ValidationError"
                raise ValidationError(f"Request validation failed: {error_detail}")
            
            # Handle rate limit errors (429)
            elif response.status_code == 429:
                error_msg = f"Rate limit exceeded: {response.text}"
                logger.error(error_msg)
                error_message = "RateLimitError"
                raise RateLimitError("Too many requests. Please wait a moment and try again.")
            
            # Handle server errors (500, 503)
            elif response.status_code in [500, 503]:
                error_msg = f"Server error {response.status_code}: {response.text}"
                logger.error(error_msg)
                
                # Implement retry logic for server errors
                logger.info("Attempting retry for server error...")
                try:
                    # Wait briefly before retry
                    time.sleep(2)
                    
                    # Retry the request once
                    retry_response = requests.post(
                        self.ultra_endpoint,
                        headers=headers,
                        files=files,
                        data=data,
                        timeout=60
                    )
                    
                    if retry_response.status_code == 200:
                        logger.info("Retry successful")
                        response_data = retry_response.json()
                        if "image" in response_data:
                            image_base64 = response_data["image"]
                            image_bytes = base64.b64decode(image_base64)
                            logger.info(f"Successfully generated image on retry, size: {len(image_bytes)} bytes")
                            return image_bytes
                    
                    logger.error(f"Retry failed with status {retry_response.status_code}")
                except Exception as retry_error:
                    logger.error(f"Retry attempt failed: {str(retry_error)}", exc_info=True)
                
                error_message = "ServerError"
                raise ServerError("The AI service is temporarily unavailable. Please try again in a few moments.")
            
            # Handle other unexpected status codes
            else:
                error_msg = f"Unexpected status code {response.status_code}: {response.text}"
                logger.error(error_msg)
                error_message = f"UnexpectedStatusCode_{response.status_code}"
                raise Exception(f"AI service returned unexpected status: {response.status_code}")
        
        except (AuthenticationError, InsufficientCreditsError, RateLimitError, 
                ValidationError, ServerError, TimeoutError, ConnectionError):
            # Re-raise custom errors without wrapping
            raise
        except ValueError as e:
            # Re-raise validation errors
            logger.error(f"Validation error in try_on_hairstyle: {str(e)}", exc_info=True)
            raise
        except Exception as e:
            # Catch-all for unexpected errors
            error_msg = f"Unexpected error in try_on_hairstyle: {str(e)}"
            logger.error(error_msg, exc_info=True)
            if not error_message:
                error_message = "UnexpectedError"
            raise Exception("An unexpected error occurred. Please try again.")
        finally:
            # Log API call regardless of success or failure
            processing_time = time.time() - start_time
            timestamp = datetime.utcnow().isoformat()
            
            self.usage_tracker.log_api_call(
                timestamp=timestamp,
                user_session=user_session,
                hairstyle_id=hairstyle_id,
                success=success,
                processing_time=processing_time,
                error=error_message
            )
    
    def generate_variations(
        self,
        user_image_bytes: bytes,
        hairstyle_description: str,
        num_variations: int = 4
    ) -> List[bytes]:
        """
        Generate multiple variations with different style strengths.
        
        Creates up to 4 variations of the hairstyle try-on using different
        style strength values (0.3, 0.35, 0.4, 0.45) to provide users with
        options to choose from.
        
        Args:
            user_image_bytes: User's photo as bytes
            hairstyle_description: Description of desired hairstyle
            num_variations: Number of variations to generate (1-4, default 4)
        
        Returns:
            List of generated images as bytes. May contain fewer than requested
            if some generations fail.
        
        Raises:
            ValueError: If num_variations is outside valid range (1-4)
        """
        # Validate num_variations parameter (must be at least 1)
        if num_variations < 1:
            error_msg = "num_variations must be at least 1"
            logger.error(f"Validation error: {error_msg}")
            raise ValueError(error_msg)
        
        # Limit to maximum of 4 variations
        if num_variations > 4:
            logger.info(f"Requested {num_variations} variations, limiting to maximum of 4")
        num_variations = min(num_variations, 4)
        
        # Define style strengths for variations
        style_strengths = [0.3, 0.35, 0.4, 0.45][:num_variations]
        
        logger.info(f"Generating {num_variations} variations with strengths: {style_strengths}")
        
        # Collect generated images
        variations = []
        
        # Generate each variation
        for i, strength in enumerate(style_strengths):
            try:
                logger.info(f"Generating variation {i+1}/{num_variations} with strength {strength}")
                
                # Call try_on_hairstyle for each variation
                result = self.try_on_hairstyle(
                    user_image_bytes=user_image_bytes,
                    hairstyle_description=hairstyle_description,
                    style_strength=strength
                )
                
                if result:
                    variations.append(result)
                    logger.info(f"Variation {i+1} generated successfully")
                else:
                    logger.warning(f"Variation {i+1} returned None")
            
            except Exception as e:
                # Log error but continue with other variations
                logger.error(f"Failed to generate variation {i+1} with strength {strength}: {str(e)}", exc_info=True)
                # Continue to next variation instead of failing completely
                continue
        
        logger.info(f"Successfully generated {len(variations)} out of {num_variations} requested variations")
        
        return variations
    
    def get_usage_stats(self, start_date: str = None, end_date: str = None) -> Dict:
        """
        Get API usage statistics.
        
        Args:
            start_date: Start date in YYYY-MM-DD format (optional)
            end_date: End date in YYYY-MM-DD format (optional)
        
        Returns:
            Dict with usage statistics including call counts and estimated costs
        """
        from datetime import date
        
        # Use today's date if not specified
        if not start_date:
            start_date = date.today().isoformat()
        if not end_date:
            end_date = date.today().isoformat()
        
        # Get daily stats for the date range
        daily_stats = self.usage_tracker.get_daily_stats(start_date)
        
        # Get cost estimate for the range
        cost_estimate = self.usage_tracker.get_cost_estimate(start_date, end_date)
        
        return {
            "start_date": start_date,
            "end_date": end_date,
            "daily_stats": daily_stats,
            "total_cost": cost_estimate
        }
    
    def check_api_status(self) -> Dict:
        """
        Check if Stability AI API is accessible and working.
        
        Returns:
            Dict with keys:
                - status: "ok" or "error"
                - enabled: bool indicating if service is available
                - message: descriptive status message
                - error_code: optional error code for specific issues
        """
        try:
            # Test API connectivity by checking account endpoint
            response = requests.get(
                f"{self.api_host}/v1/user/account",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Accept": "application/json"
                },
                timeout=10
            )
            
            if response.status_code == 200:
                logger.info("API status check successful")
                return {
                    "status": "ok",
                    "enabled": True,
                    "message": "Stable Image Ultra API is accessible"
                }
            elif response.status_code == 401:
                logger.error("API authentication failed - invalid API key")
                self.enabled = False
                return {
                    "status": "error",
                    "enabled": False,
                    "message": "API authentication failed - invalid API key",
                    "error_code": "AUTH_FAILED"
                }
            elif response.status_code == 402:
                logger.error("Insufficient credits")
                return {
                    "status": "error",
                    "enabled": False,
                    "message": "Insufficient credits",
                    "error_code": "INSUFFICIENT_CREDITS"
                }
            elif response.status_code == 429:
                logger.warning("Rate limit exceeded")
                return {
                    "status": "error",
                    "enabled": False,
                    "message": "Rate limit exceeded - please wait before retrying",
                    "error_code": "RATE_LIMIT"
                }
            elif response.status_code in [500, 503]:
                logger.error(f"Server error: {response.status_code}")
                return {
                    "status": "error",
                    "enabled": False,
                    "message": "AI service is temporarily unavailable",
                    "error_code": "SERVER_ERROR"
                }
            else:
                logger.warning(f"API status check returned {response.status_code}")
                return {
                    "status": "error",
                    "enabled": False,
                    "message": f"API returned status code {response.status_code}",
                    "error_code": "UNKNOWN_ERROR"
                }
        
        except requests.exceptions.Timeout:
            logger.error("API status check timed out")
            return {
                "status": "error",
                "enabled": False,
                "message": "API request timed out",
                "error_code": "TIMEOUT"
            }
        except requests.exceptions.ConnectionError as e:
            logger.error(f"Connection error during status check: {str(e)}", exc_info=True)
            return {
                "status": "error",
                "enabled": False,
                "message": "Unable to connect to AI service",
                "error_code": "CONNECTION_ERROR"
            }
        except Exception as e:
            logger.error(f"API status check failed: {str(e)}", exc_info=True)
            return {
                "status": "error",
                "enabled": False,
                "message": "API check failed",
                "error_code": "UNKNOWN_ERROR"
            }


# Singleton instance
_stable_image_ultra_service_instance = None


def get_stable_image_ultra_service() -> Optional[StableImageUltraService]:
    """
    Get singleton instance of StableImageUltraService.
    
    Returns:
        StableImageUltraService instance, or None if initialization fails.
    """
    global _stable_image_ultra_service_instance
    
    if _stable_image_ultra_service_instance is None:
        try:
            _stable_image_ultra_service_instance = StableImageUltraService()
            logger.info("Singleton instance created successfully")
        except ValueError as e:
            logger.error(f"Failed to create service instance: {str(e)}")
            return None
    
    return _stable_image_ultra_service_instance
