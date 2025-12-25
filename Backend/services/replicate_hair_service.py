"""
Replicate Hair Try-On Service

Uses Replicate API to generate hairstyle try-on images.
Supports multiple models for different quality/speed tradeoffs.

Setup:
1. Get API key: https://replicate.com/account/api-tokens
2. Set environment variable: REPLICATE_API_TOKEN=your_token

Pricing: Pay-per-use, varies by model
"""

import os
import logging
import replicate
from typing import Dict, Optional, List
import requests
from io import BytesIO
from PIL import Image
import base64
import time
from datetime import datetime

# Configure logging
logger = logging.getLogger('replicate_hair_service')
logger.setLevel(logging.INFO)

formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

file_handler = logging.FileHandler('replicate_hair_service.log')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)


class ReplicateHairService:
    """
    Service for applying hairstyles using Replicate API.
    
    Uses SDXL or other models for image-to-image generation
    with face preservation.
    """
    
    # Default model - Google Nano Banana Pro
    # This is a lightweight, fast model optimized for image editing
    DEFAULT_MODEL = "tencentarc/photomaker:ddfc2b08d209f9fa8c1eca692712918bd449f695dabb4a958da31802a9570fe4"
    
    def __init__(self, api_token: str = None):
        """
        Initialize Replicate service.
        
        Args:
            api_token: Replicate API token. If not provided, reads from
                      REPLICATE_API_TOKEN environment variable.
        
        Raises:
            ValueError: If API token is not provided and not in environment.
        """
        self.api_token = api_token or os.environ.get('REPLICATE_API_TOKEN')
        
        if not self.api_token:
            error_msg = (
                "REPLICATE_API_TOKEN not found in environment. "
                "Get your token from https://replicate.com/account/api-tokens"
            )
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        # Set the API token for replicate client
        os.environ['REPLICATE_API_TOKEN'] = self.api_token
        self.enabled = True
        
        logger.info("ReplicateHairService initialized successfully")
    
    def _build_prompt(self, hairstyle_description: str) -> str:
        """
        Build optimized prompt for face preservation and quality.
        
        Args:
            hairstyle_description: Description of the desired hairstyle
        
        Returns:
            Complete prompt string optimized for PhotoMaker
        """
        # PhotoMaker prompt format: "a photo of img, [description]"
        # img is a special token that represents the input face
        prompt = f"a photo of a person img with {hairstyle_description}, professional portrait, high quality"
        
        logger.info(f"Built prompt: {prompt}")
        return prompt
    
    def _build_negative_prompt(self) -> str:
        """
        Build negative prompt to avoid unwanted changes.
        
        Returns:
            Negative prompt string with unwanted keywords
        """
        negative_prompt = (
            "different person, different face, face change, "
            "multiple people, multiple faces, "
            "blurry, low quality, distorted, ugly, "
            "cartoon, anime, drawing, painting, "
            "deformed, disfigured, bad anatomy, "
            "watermark, signature, text"
        )
        
        logger.info(f"Built negative prompt: {negative_prompt}")
        return negative_prompt
    
    def _image_to_data_uri(self, image_bytes: bytes) -> str:
        """
        Convert image bytes to data URI for Replicate API.
        
        Args:
            image_bytes: Image data as bytes
        
        Returns:
            Data URI string
        """
        # Load and validate image
        image = Image.open(BytesIO(image_bytes))
        
        # Convert to RGB if needed
        if image.mode != 'RGB':
            logger.info(f"Converting {image.mode} to RGB")
            if image.mode == 'RGBA':
                rgb_image = Image.new('RGB', image.size, (255, 255, 255))
                rgb_image.paste(image, mask=image.split()[3])
                image = rgb_image
            else:
                image = image.convert('RGB')
        
        # Resize if too large (max 1024 for faster processing)
        max_size = 1024
        if image.width > max_size or image.height > max_size:
            original_size = image.size
            image.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
            logger.info(f"Resized image from {original_size} to {image.size}")
        
        # Convert to base64 data URI
        buffer = BytesIO()
        image.save(buffer, format='PNG')
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.read()).decode('utf-8')
        data_uri = f"data:image/png;base64,{image_base64}"
        
        return data_uri
    
    def try_on_hairstyle(
        self,
        user_image_bytes: bytes,
        hairstyle_description: str,
        style_strength: float = 0.35,
        user_session: str = "anonymous",
        hairstyle_id: str = "unknown"
    ) -> Optional[bytes]:
        """
        Apply hairstyle using Replicate API.
        
        Args:
            user_image_bytes: User's photo as bytes
            hairstyle_description: Description of desired hairstyle
            style_strength: How much to modify (0.0-1.0, default 0.35)
            user_session: User session identifier (for tracking)
            hairstyle_id: Hairstyle ID (for tracking)
        
        Returns:
            Generated image as bytes, or None if failed
        
        Raises:
            ValueError: If style_strength is outside valid range
            Exception: For API errors
        """
        start_time = time.time()
        
        # Validate style strength
        if not (0.0 <= style_strength <= 1.0):
            error_msg = "style_strength must be between 0.0 and 1.0"
            logger.error(f"Validation error: {error_msg}")
            raise ValueError(error_msg)
        
        try:
            logger.info(f"Starting try-on with hairstyle: {hairstyle_description}, strength: {style_strength}")
            
            # Prepare image as file object instead of base64
            # This is more efficient and PhotoMaker might handle it better
            image = Image.open(BytesIO(user_image_bytes))
            
            # Convert to RGB if needed
            if image.mode != 'RGB':
                logger.info(f"Converting {image.mode} to RGB")
                if image.mode == 'RGBA':
                    rgb_image = Image.new('RGB', image.size, (255, 255, 255))
                    rgb_image.paste(image, mask=image.split()[3])
                    image = rgb_image
                else:
                    image = image.convert('RGB')
            
            # Resize if too large
            max_size = 1024
            if image.width > max_size or image.height > max_size:
                original_size = image.size
                image.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
                logger.info(f"Resized image from {original_size} to {image.size}")
            
            # Convert to file-like object
            image_buffer = BytesIO()
            image.save(image_buffer, format='PNG')
            image_buffer.seek(0)
            
            # Build prompts
            prompt = self._build_prompt(hairstyle_description)
            negative_prompt = self._build_negative_prompt()
            
            # Run the model
            logger.info(f"Calling Replicate API with model: {self.DEFAULT_MODEL}")
            
            # Prepare input parameters for PhotoMaker
            # PhotoMaker requires specific parameter names
            input_params = {
                "input_image": image_buffer,  # Send as file object
                "prompt": prompt,
                "negative_prompt": negative_prompt,
                "num_steps": 20,
                "style_strength_ratio": 20,
                "num_outputs": 1,
                "guidance_scale": 5
            }
            
            # Log to verify image is being sent
            logger.info(f"Image buffer size: {len(image_buffer.getvalue())} bytes")
            logger.info(f"Prompt being sent: {prompt}")
            
            output = replicate.run(
                self.DEFAULT_MODEL,
                input=input_params
            )
            
            # Log the full output to debug
            logger.info(f"Full output from Replicate: {output}")
            logger.info(f"Output type: {type(output)}")
            
            # Handle different output formats
            result_url = None
            if output:
                # If output is a string (single URL)
                if isinstance(output, str):
                    result_url = output
                # If output is a list
                elif isinstance(output, list) and len(output) > 0:
                    result_url = output[0]
                # If output is an iterator/generator
                else:
                    try:
                        result_url = next(iter(output))
                    except (StopIteration, TypeError):
                        logger.error(f"Could not extract URL from output: {output}")
                        return None
                
                logger.info(f"Generated image URL: {result_url}")
                
                # Download the image
                response = requests.get(result_url, timeout=30)
                if response.status_code == 200:
                    image_bytes = response.content
                    logger.info(f"Successfully downloaded image, size: {len(image_bytes)} bytes")
                    
                    processing_time = time.time() - start_time
                    logger.info(f"Total processing time: {processing_time:.2f}s")
                    
                    return image_bytes
                else:
                    logger.error(f"Failed to download image: {response.status_code}")
                    return None
            else:
                logger.error("No output received from Replicate")
                return None
        
        except Exception as e:
            logger.error(f"Error in try_on_hairstyle: {str(e)}", exc_info=True)
            raise
    
    def generate_variations(
        self,
        user_image_bytes: bytes,
        hairstyle_description: str,
        num_variations: int = 4
    ) -> List[bytes]:
        """
        Generate multiple variations with different style strengths.
        
        Args:
            user_image_bytes: User's photo as bytes
            hairstyle_description: Description of desired hairstyle
            num_variations: Number of variations to generate (1-4)
        
        Returns:
            List of generated images as bytes
        """
        if num_variations < 1:
            error_msg = "num_variations must be at least 1"
            logger.error(f"Validation error: {error_msg}")
            raise ValueError(error_msg)
        
        num_variations = min(num_variations, 4)
        
        # Different strengths for variations (higher values for more change)
        style_strengths = [0.35, 0.45, 0.55, 0.65][:num_variations]
        
        logger.info(f"Generating {num_variations} variations with strengths: {style_strengths}")
        
        variations = []
        
        for i, strength in enumerate(style_strengths):
            try:
                logger.info(f"Generating variation {i+1}/{num_variations} with strength {strength}")
                
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
                logger.error(f"Failed to generate variation {i+1}: {str(e)}", exc_info=True)
                continue
        
        logger.info(f"Successfully generated {len(variations)} out of {num_variations} requested variations")
        
        return variations
    
    def check_api_status(self) -> Dict:
        """
        Check if Replicate API is accessible.
        
        Returns:
            Dict with status information
        """
        try:
            # Try to list models to verify API access
            replicate.models.list()
            
            logger.info("API status check successful")
            return {
                "status": "ok",
                "enabled": True,
                "message": "Replicate API is accessible"
            }
        
        except Exception as e:
            logger.error(f"API status check failed: {str(e)}", exc_info=True)
            return {
                "status": "error",
                "enabled": False,
                "message": f"API check failed: {str(e)}",
                "error_code": "API_ERROR"
            }


# Singleton instance
_replicate_service_instance = None


def get_replicate_hair_service() -> Optional[ReplicateHairService]:
    """
    Get singleton instance of ReplicateHairService.
    
    Returns:
        ReplicateHairService instance, or None if initialization fails.
    """
    global _replicate_service_instance
    
    if _replicate_service_instance is None:
        try:
            _replicate_service_instance = ReplicateHairService()
            logger.info("Singleton instance created successfully")
        except ValueError as e:
            logger.error(f"Failed to create service instance: {str(e)}")
            return None
    
    return _replicate_service_instance
