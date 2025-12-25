"""Favorites management routes."""

from flask import request, session, current_app
from flask_restx import Namespace, Resource, fields
from services.user_database import get_user_database
from services.database import get_database

ns_favorites = Namespace('favorites', description='Favorite hairstyles management')

user_db = get_user_database()
hairstyle_db = get_database()

# Models
favorite_input_model = ns_favorites.model('FavoriteInput', {
    'hairstyle_id': fields.String(required=True, description='Hairstyle ID'),
    'hairstyle_name': fields.String(required=True, description='Hairstyle name'),
    'face_shape': fields.String(required=False, description='Face shape'),
    'image_url': fields.String(required=False, description='Image URL')
})


@ns_favorites.route('')
class Favorites(Resource):
    @ns_favorites.doc('get_favorites')
    @ns_favorites.response(200, 'Success')
    @ns_favorites.response(401, 'Unauthorized')
    def get(self):
        """Get user's favorite hairstyles."""
        username = session.get('username')
        if not username:
            return {'success': False, 'error': 'Not authenticated'}, 401
        
        session_id = username
        
        try:
            favorites = user_db.get_favorites(session_id)
            
            enriched_favorites = []
            for fav in favorites:
                hairstyle = hairstyle_db.get_hairstyle_by_id(fav['hairstyle_id'])
                
                if not hairstyle:
                    hairstyle = {
                        'id': fav['hairstyle_id'],
                        'name': fav['hairstyle_name'],
                        'description': 'Custom hairstyle created by AI',
                        'tags': ['custom', 'ai-generated'],
                        'image_url': fav.get('image_url') or 'https://via.placeholder.com/400x500/667eea/ffffff?text=Custom+Hairstyle',
                        'face_shapes': [fav.get('face_shape', 'all')],
                        'difficulty': 'medium'
                    }
                
                enriched_favorites.append({
                    'favorite_id': fav['id'],
                    'created_at': fav['created_at'],
                    'hairstyle': hairstyle
                })
            
            return {'success': True, 'count': len(enriched_favorites), 'favorites': enriched_favorites}, 200
        
        except Exception as e:
            current_app.logger.error(f"Error getting favorites: {str(e)}")
            return {'success': False, 'error': 'Failed to retrieve favorites', 'code': 'FAVORITE_ERROR'}, 500
    
    @ns_favorites.doc('add_favorite')
    @ns_favorites.expect(favorite_input_model)
    @ns_favorites.response(201, 'Created')
    @ns_favorites.response(401, 'Unauthorized')
    @ns_favorites.response(409, 'Already Exists')
    def post(self):
        """Add a hairstyle to user's favorites."""
        username = session.get('username')
        if not username:
            return {'success': False, 'error': 'Not authenticated'}, 401
        
        session_id = username
        data = request.get_json()
        
        if not data:
            return {'success': False, 'error': 'Request body is required', 'code': 'MISSING_BODY'}, 400
        
        hairstyle_id = data.get('hairstyle_id')
        hairstyle_name = data.get('hairstyle_name')
        
        if not hairstyle_id or not hairstyle_name:
            return {'success': False, 'error': 'hairstyle_id and hairstyle_name are required', 'code': 'MISSING_PARAMETERS'}, 400
        
        face_shape = data.get('face_shape')
        image_url = data.get('image_url')
        
        try:
            added = user_db.add_favorite(session_id, hairstyle_id, hairstyle_name, face_shape, image_url)
            
            if added:
                return {'success': True, 'message': 'Hairstyle added to favorites'}, 201
            else:
                return {'success': False, 'error': 'Hairstyle already in favorites', 'code': 'ALREADY_EXISTS'}, 409
        
        except Exception as e:
            current_app.logger.error(f"Error adding favorite: {str(e)}")
            return {'success': False, 'error': 'Failed to add favorite', 'code': 'FAVORITE_ERROR'}, 500


@ns_favorites.route('/<string:hairstyle_id>')
class FavoriteItem(Resource):
    @ns_favorites.doc('remove_favorite')
    @ns_favorites.response(200, 'Success')
    @ns_favorites.response(401, 'Unauthorized')
    @ns_favorites.response(404, 'Not Found')
    def delete(self, hairstyle_id):
        """Remove a hairstyle from user's favorites."""
        username = session.get('username')
        if not username:
            return {'success': False, 'error': 'Not authenticated'}, 401
        
        session_id = username
        
        try:
            removed = user_db.remove_favorite(session_id, hairstyle_id)
            
            if removed:
                return {'success': True, 'message': 'Hairstyle removed from favorites'}, 200
            else:
                return {'success': False, 'error': 'Hairstyle not found in favorites', 'code': 'NOT_FOUND'}, 404
        
        except Exception as e:
            current_app.logger.error(f"Error removing favorite: {str(e)}")
            return {'success': False, 'error': 'Failed to remove favorite', 'code': 'FAVORITE_ERROR'}, 500


@ns_favorites.route('/check/<string:hairstyle_id>')
class FavoriteCheck(Resource):
    @ns_favorites.doc('check_favorite')
    def get(self, hairstyle_id):
        """Check if a hairstyle is in user's favorites."""
        username = session.get('username')
        if not username:
            return {'success': True, 'is_favorite': False}, 200
        
        session_id = username
        
        try:
            is_fav = user_db.is_favorite(session_id, hairstyle_id)
            return {'success': True, 'is_favorite': is_fav}, 200
        
        except Exception as e:
            current_app.logger.error(f"Error checking favorite: {str(e)}")
            return {'success': False, 'error': 'Failed to check favorite status', 'code': 'FAVORITE_ERROR'}, 500
