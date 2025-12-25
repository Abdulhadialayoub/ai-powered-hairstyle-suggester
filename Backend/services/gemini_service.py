"""
Gemini AI service for generating hairstyle recommendations and comments.

This module uses Google's Gemini API to generate personalized
comments and styling advice for hairstyles.

Setup:
1. Install: pip install google-generativeai
2. Get API key: https://makersuite.google.com/app/apikey
3. Set environment variable: GEMINI_API_KEY=your_key
"""

import os
import google.generativeai as genai
from typing import Optional
from dotenv import load_dotenv

load_dotenv()


class GeminiService:
    """Service for generating AI-powered hairstyle comments using Gemini."""
    
    def __init__(self, api_key: str = None):
        """
        Initialize Gemini service.
        
        Args:
            api_key: Gemini API key. If None, reads from environment.
        """
        self.api_key = api_key or os.environ.get('GEMINI_API_KEY')
        
        if not self.api_key:
            self.enabled = False
            return
        
        try:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-2.0-flash')
            self.enabled = True
        except Exception as e:
            print(f"Failed to initialize Gemini: {e}")
            self.enabled = False
    
    def generate_hairstyle_comment(
        self,
        hairstyle_name: str,
        face_shape: str,
        hairstyle_description: str = "",
        tags: list = None
    ) -> Optional[str]:
        """
        Generate a personalized comment about a hairstyle.
        
        Args:
            hairstyle_name: Name of the hairstyle
            face_shape: User's face shape
            hairstyle_description: Description of the hairstyle
            tags: List of style tags
        
        Returns:
            Generated comment or None if service is disabled
        """
        if not self.enabled:
            return None
        
        try:
            tags_str = ", ".join(tags) if tags else ""
            
            prompt = f"""You are a professional hairstylist. Generate a short, friendly, and personalized comment (2-3 sentences) about this hairstyle for someone with a {face_shape} face shape.

Hairstyle: {hairstyle_name}
Description: {hairstyle_description}
Style tags: {tags_str}

Keep it encouraging, specific, and mention why this style works well for their face shape. Use a warm, conversational tone."""

            response = self.model.generate_content(prompt)
            return response.text.strip()
        
        except Exception as e:
            print(f"Error generating comment: {e}")
            return None
    
    def generate_styling_tips(
        self,
        hairstyle_name: str,
        difficulty: str,
        tags: list = None
    ) -> Optional[str]:
        """
        Generate styling tips for a hairstyle.
        
        Args:
            hairstyle_name: Name of the hairstyle
            difficulty: Difficulty level (easy, medium, hard)
            tags: List of style tags
        
        Returns:
            Generated styling tips or None if service is disabled
        """
        if not self.enabled:
            return None
        
        try:
            tags_str = ", ".join(tags) if tags else ""
            
            prompt = f"""You are a professional hairstylist. Generate 3 quick styling tips for this hairstyle.

Hairstyle: {hairstyle_name}
Difficulty: {difficulty}
Style tags: {tags_str}

Keep each tip short (one sentence) and practical. Focus on techniques, products, or maintenance."""

            response = self.model.generate_content(prompt)
            return response.text.strip()
        
        except Exception as e:
            print(f"Error generating tips: {e}")
            return None
    
    def evaluate_hairstyle_result(
        self,
        hairstyle_name: str,
        face_shape: str,
        result_image_bytes: bytes = None
    ) -> Optional[str]:
        """
        Evaluate an AI-generated hairstyle result and provide feedback.
        
        Args:
            hairstyle_name: Name of the hairstyle
            face_shape: User's face shape
            result_image_bytes: Optional image bytes of the result
        
        Returns:
            AI evaluation comment or None if service is disabled
        """
        if not self.enabled:
            return None
        
        try:
            prompt = f"""You are a professional hairstylist reviewing an AI-generated hairstyle preview.

Hairstyle: {hairstyle_name}
Face Shape: {face_shape}

Provide a brief, encouraging evaluation (2-3 sentences) covering:
1. Does this hairstyle suit the {face_shape} face shape?
2. What are the key benefits of this style?
3. Any quick styling advice?

Keep it positive, specific, and helpful. Use a warm, professional tone."""

            # If image is provided, use vision model
            if result_image_bytes:
                import PIL.Image
                from io import BytesIO
                
                image = PIL.Image.open(BytesIO(result_image_bytes))
                vision_model = genai.GenerativeModel('gemini-2.0-flash-exp')
                
                prompt = f"""You are a professional hairstylist reviewing this AI-generated hairstyle preview.

Hairstyle: {hairstyle_name}
Face Shape: {face_shape}

Looking at this image, provide a brief evaluation (2-3 sentences):
1. Does this hairstyle complement the face shape and features?
2. What works well about this style?
3. Any quick styling or maintenance tips?

Be encouraging, specific, and professional."""
                
                response = vision_model.generate_content([prompt, image])
            else:
                response = self.model.generate_content(prompt)
            
            return response.text.strip()
        
        except Exception as e:
            print(f"Error evaluating hairstyle: {e}")
            return None
    
    def check_status(self) -> dict:
        """
        Check if Gemini service is available.
        
        Returns:
            Status dictionary
        """
        return {
            'enabled': self.enabled,
            'model': 'gemini-2.0-flash-exp' if self.enabled else None
        }


# Singleton instance
_gemini_instance = None


def get_gemini_service() -> GeminiService:
    """
    Get the singleton Gemini service instance.
    
    Returns:
        GeminiService instance
    """
    global _gemini_instance
    if _gemini_instance is None:
        _gemini_instance = GeminiService()
    return _gemini_instance


def is_gemini_enabled() -> bool:
    """
    Check if Gemini service is enabled.
    
    Returns:
        True if enabled, False otherwise
    """
    service = get_gemini_service()
    return service.enabled
