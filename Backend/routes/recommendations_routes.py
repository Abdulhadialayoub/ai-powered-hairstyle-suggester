"""Hairstyle recommendations routes."""

from flask import request, current_app
from flask_restx import Namespace, Resource, fields
from services.recommendation_engine import get_recommendation_engine

ns_recommendations = Namespace('recommendations', description='Hairstyle recommendation operations')

recommendation_engine = get_recommendation_engine()

# Models
hairstyle_model = ns_recommendations.model('Hairstyle', {
    'id': fields.String(description='Hairstyle ID'),
    'name': fields.String(description='Hairstyle name'),
    'description': fields.String(description='Hairstyle description'),
    'suitable_face_shapes': fields.List(fields.String, description='Suitable face shapes'),
    'image_url': fields.String(description='Image URL'),
    'difficulty': fields.String(description='Styling difficulty'),
    'popularity': fields.Integer(description='Popularity score'),
    'tags': fields.List(fields.String, description='Style tags'),
    'reason': fields.String(description='Why this style suits the face shape')
})

recommendations_response_model = ns_recommendations.model('RecommendationsResponse', {
    'success': fields.Boolean(description='Operation success status'),
    'face_shape': fields.String(description='Face shape'),
    'count': fields.Integer(description='Number of recommendations'),
    'recommendations': fields.List(fields.Nested(hairstyle_model))
})


@ns_recommendations.route('')
class Recommendations(Resource):
    @ns_recommendations.doc('get_recommendations',
             params={
                 'face_shape': {'description': 'Face shape (oval, round, square, heart, diamond)', 'required': True},
                 'limit': {'description': 'Maximum number of recommendations (1-20)', 'default': 5},
                 'sort_by': {'description': 'Sort by popularity or difficulty', 'default': 'popularity'}
             })
    @ns_recommendations.response(200, 'Success', recommendations_response_model)
    @ns_recommendations.response(400, 'Bad Request')
    def get(self):
        """Get hairstyle recommendations for a specific face shape."""
        face_shape = request.args.get('face_shape')
        
        if not face_shape:
            return {'success': False, 'error': 'face_shape parameter is required', 'code': 'MISSING_PARAMETER'}, 400
        
        valid_face_shapes = ['oval', 'round', 'square', 'heart', 'diamond']
        if face_shape.lower() not in valid_face_shapes:
            return {'success': False, 'error': f'Invalid face_shape. Must be one of: {", ".join(valid_face_shapes)}', 'code': 'INVALID_FACE_SHAPE'}, 400
        
        try:
            limit = int(request.args.get('limit', 5))
            if limit < 1 or limit > 20:
                limit = 5
        except ValueError:
            limit = 5
        
        sort_by = request.args.get('sort_by', 'popularity')
        if sort_by not in ['popularity', 'difficulty']:
            sort_by = 'popularity'
        
        try:
            recommendations = recommendation_engine.get_recommendations(
                face_shape=face_shape,
                limit=limit,
                sort_by=sort_by,
                include_explanations=True
            )
            
            return {
                'success': True,
                'face_shape': face_shape,
                'count': len(recommendations),
                'recommendations': recommendations
            }, 200
        
        except Exception as e:
            current_app.logger.error(f"Error in get_recommendations: {str(e)}")
            return {'success': False, 'error': 'Failed to retrieve recommendations', 'code': 'RECOMMENDATION_ERROR'}, 500
