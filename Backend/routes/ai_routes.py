"""AI-powered features routes (Gemini)."""

from flask import request, current_app
from flask_restx import Namespace, Resource, fields
from services.gemini_service import get_gemini_service, is_gemini_enabled
from services.stable_image_ultra_service import get_stable_image_ultra_service
from services.replicate_hair_service import get_replicate_hair_service

ns_ai = Namespace('ai', description='AI-powered features (Gemini)')


def is_ai_tryon_enabled():
    ultra_service = get_stable_image_ultra_service()
    replicate_service = get_replicate_hair_service()
    return (ultra_service is not None and ultra_service.enabled) or \
           (replicate_service is not None and replicate_service.enabled)


# Models
comment_input_model = ns_ai.model('CommentInput', {
    'hairstyle_name': fields.String(required=True, description='Hairstyle name'),
    'face_shape': fields.String(required=True, description='Face shape'),
    'hairstyle_description': fields.String(required=False, description='Hairstyle description'),
    'tags': fields.List(fields.String, required=False, description='Style tags')
})

comment_response_model = ns_ai.model('CommentResponse', {
    'success': fields.Boolean(description='Operation success'),
    'comment': fields.String(description='Generated comment'),
    'enabled': fields.Boolean(description='Whether Gemini is enabled')
})


@ns_ai.route('/comment')
class AIComment(Resource):
    @ns_ai.doc('generate_comment')
    @ns_ai.expect(comment_input_model)
    @ns_ai.response(200, 'Success', comment_response_model)
    @ns_ai.response(503, 'Service Unavailable')
    def post(self):
        """Generate AI-powered personalized comment for a hairstyle."""
        if not is_gemini_enabled():
            return {
                'success': False,
                'enabled': False,
                'comment': None,
                'message': 'Gemini AI is not configured. Set GEMINI_API_KEY to enable.'
            }, 503
        
        data = request.get_json()
        if not data:
            return {'success': False, 'error': 'Request body is required', 'code': 'MISSING_BODY'}, 400
        
        hairstyle_name = data.get('hairstyle_name')
        face_shape = data.get('face_shape')
        
        if not hairstyle_name or not face_shape:
            return {'success': False, 'error': 'hairstyle_name and face_shape are required', 'code': 'MISSING_PARAMETERS'}, 400
        
        try:
            gemini = get_gemini_service()
            comment = gemini.generate_hairstyle_comment(
                hairstyle_name=hairstyle_name,
                face_shape=face_shape,
                hairstyle_description=data.get('hairstyle_description', ''),
                tags=data.get('tags', [])
            )
            
            return {'success': True, 'enabled': True, 'comment': comment}, 200
        
        except Exception as e:
            current_app.logger.error(f"Error generating comment: {str(e)}")
            return {'success': False, 'error': 'Failed to generate comment', 'code': 'GENERATION_ERROR'}, 500


@ns_ai.route('/status')
class AIStatus(Resource):
    @ns_ai.doc('ai_status')
    def get(self):
        """Check AI services status (Gemini and Try-On)."""
        gemini = get_gemini_service()
        gemini_status = gemini.check_status()
        
        return {
            'success': True,
            'gemini': gemini_status,
            'try_on': {'enabled': is_ai_tryon_enabled()}
        }, 200
