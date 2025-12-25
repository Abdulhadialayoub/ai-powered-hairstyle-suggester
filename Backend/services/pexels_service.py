"""
Pexels API service for fetching hairstyle images.
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

PEXELS_API_KEY = os.getenv('PEXELS_API_KEY')
PEXELS_BASE_URL = 'https://api.pexels.com/v1'


def search_hairstyle_images(query: str, per_page: int = 5) -> list:
    """
    Search for hairstyle images on Pexels.
    
    Args:
        query: Search term (e.g., "undercut hairstyle men")
        per_page: Number of results to return
    
    Returns:
        List of image URLs
    """
    if not PEXELS_API_KEY:
        print("Warning: PEXELS_API_KEY not set")
        return []
    
    headers = {
        'Authorization': PEXELS_API_KEY
    }
    
    params = {
        'query': f"{query} men hairstyle",
        'per_page': per_page,
        'orientation': 'portrait'
    }
    
    try:
        response = requests.get(
            f"{PEXELS_BASE_URL}/search",
            headers=headers,
            params=params,
            timeout=10
        )
        response.raise_for_status()
        data = response.json()
        
        images = []
        for photo in data.get('photos', []):
            images.append({
                'id': photo['id'],
                'url': photo['src']['medium'],
                'large_url': photo['src']['large'],
                'photographer': photo['photographer'],
                'alt': photo.get('alt', query)
            })
        
        return images
    
    except Exception as e:
        print(f"Pexels API error: {e}")
        return []


def get_random_portrait(query: str = "man portrait") -> str:
    """
    Get a random portrait image URL.
    
    Args:
        query: Search term
    
    Returns:
        Image URL or empty string
    """
    images = search_hairstyle_images(query, per_page=15)
    if images:
        import random
        return random.choice(images)['url']
    return ""
