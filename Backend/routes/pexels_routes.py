"""Pexels image search routes."""

from flask import request
from flask_restx import Namespace, Resource
from services.pexels_service import search_hairstyle_images

ns_pexels = Namespace('pexels', description='Pexels image search')


@ns_pexels.route('/search')
class PexelsSearch(Resource):
    @ns_pexels.doc('search_pexels',
             params={
                 'query': {'description': 'Search query (e.g., "undercut")', 'required': True},
                 'per_page': {'description': 'Number of results (1-15)', 'default': 5}
             })
    def get(self):
        """Search for hairstyle images on Pexels."""
        query = request.args.get('query', '')
        per_page = min(int(request.args.get('per_page', 5)), 15)
        
        if not query:
            return {'success': False, 'error': 'Query is required'}, 400
        
        images = search_hairstyle_images(query, per_page)
        
        return {'success': True, 'count': len(images), 'images': images}, 200
