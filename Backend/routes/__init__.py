"""
Routes package for AI Hairstyle Suggester API.

This package contains all API endpoint blueprints organized by functionality.
"""

from flask_restx import Api

# Import all route blueprints
from .auth_routes import ns_auth
from .analysis_routes import ns_analysis
from .recommendations_routes import ns_recommendations
from .favorites_routes import ns_favorites
from .tryon_routes import ns_tryon
from .ai_routes import ns_ai
from .pexels_routes import ns_pexels
from .ml_routes import ns_ml


def init_api(app):
    """Initialize Flask-RESTX API with all namespaces."""
    api = Api(
        app,
        version='1.0',
        title='AI Hairstyle Suggester API',
        description='API for analyzing face shapes and recommending hairstyles',
        doc='/api/docs',
        prefix='/api'
    )
    
    # Register all namespaces
    api.add_namespace(ns_auth)
    api.add_namespace(ns_analysis)
    api.add_namespace(ns_recommendations)
    api.add_namespace(ns_favorites)
    api.add_namespace(ns_tryon)
    api.add_namespace(ns_ai)
    api.add_namespace(ns_pexels)
    api.add_namespace(ns_ml)
    
    return api
