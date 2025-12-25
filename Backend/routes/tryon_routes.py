"""AI hairstyle try-on routes."""

import os
import uuid
from flask import request, session, current_app, send_file
from flask_restx import Namespace, Resource, fields
from werkzeug.datastructures import FileStorage
from services.stable_image_ultra_service import get_stable_image_ultra_service
from services.replicate_hair_service import get_replicate_hair_service
from services.database import get_database

ns_tryon = Namespace('try-on', description='AI hairstyle try-on operations')

hairstyle_db = get_database()
ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'webp'}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def is_ultra_service_enabled():
    ultra_service = get_stable_image_ultra_service()
    return ultra_service is not None and ultra_service.enabled


def is_replicate_service_enabled():
    replicate_service = get_replicate_hair_service()
    return replicate_service is not None and replicate_service.enabled


# Models
tryon_result_model = ns_tryon.model('TryOnResult', {
    'success': fields.Boolean(description='Operation success status'),
    'result_url': fields.String(description='URL of the result image'),
    'hairstyle_id': fields.String(description='Hairstyle ID'),
    'hairstyle_name': fields.String(description='Hairstyle name')
})


@ns_tryon.route('')
class TryOn(Resource):
    @ns_tryon.doc('try_on_hairstyle')
    @ns_tryon.expect(ns_tryon.parser()
                .add_argument('image', type=FileStorage, location='files', required=True)
                .add_argument('hairstyle_id', type=str, location='form')
                .add_argument('hairstyle_name', type=str, location='form')
                .add_argument('quality', type=str, location='form', default='high'))
    @ns_tryon.response(200, 'Success', tryon_result_model)
    @ns_tryon.response(503, 'Service Unavailable')
    def post(self):
        """Apply a hairstyle to user's photo using AI."""
        use_replicate = is_replicate_service_enabled()
        use_ultra = is_ultra_service_enabled()
        
        if not use_replicate and not use_ultra:
            return {'success': False, 'error': 'AI try-on feature is not enabled', 'code': 'FEATURE_DISABLED'}, 503
        
        if 'image' not in request.files:
            return {'success': False, 'error': 'No image file provided', 'code': 'NO_IMAGE'}, 400
        
        file = request.files['image']
        hairstyle_id = request.form.get('hairstyle_id')
        hairstyle_name = request.form.get('hairstyle_name')
        
        if not hairstyle_id and not hairstyle_name:
            return {'success': False, 'error': 'hairstyle_id or hairstyle_name is required', 'code': 'MISSING_PARAMETER'}, 400
        
        if file.filename == '' or not allowed_file(file.filename):
            return {'success': False, 'error': 'Invalid file', 'code': 'INVALID_FORMAT'}, 400
        
        try:
            image_data = file.read()
            
            if hairstyle_name:
                description = hairstyle_name
            else:
                hairstyle = hairstyle_db.get_hairstyle_by_id(hairstyle_id)
                if not hairstyle:
                    return {'success': False, 'error': 'Hairstyle not found', 'code': 'NOT_FOUND'}, 404
                tags = ', '.join(hairstyle.get('tags', []))
                description = f"{hairstyle['name']}, {tags}"
            
            user_session = session.get('user_session_id', 'anonymous')
            
            if use_replicate:
                replicate_service = get_replicate_hair_service()
                result_image = replicate_service.try_on_hairstyle(
                    user_image_bytes=image_data,
                    hairstyle_description=description,
                    style_strength=0.35,
                    user_session=user_session,
                    hairstyle_id=hairstyle_id or 'custom'
                )
            else:
                ultra_service = get_stable_image_ultra_service()
                result_image = ultra_service.try_on_hairstyle(
                    user_image_bytes=image_data,
                    hairstyle_description=description,
                    style_strength=0.35,
                    user_session=user_session,
                    hairstyle_id=hairstyle_id or 'custom'
                )
            
            if result_image:
                result_filename = f"tryon_{hairstyle_id or 'custom'}_{uuid.uuid4().hex[:8]}.jpg"
                upload_folder = current_app.config['UPLOAD_FOLDER']
                result_path = os.path.join(upload_folder, result_filename)
                
                with open(result_path, 'wb') as f:
                    f.write(result_image)
                
                # Get AI evaluation
                ai_evaluation = None
                try:
                    from services.gemini_service import get_gemini_service
                    gemini = get_gemini_service()
                    if gemini.enabled:
                        face_shape = session.get('face_shape', 'unknown')
                        ai_evaluation = gemini.evaluate_hairstyle_result(
                            hairstyle_name=description,
                            face_shape=face_shape,
                            result_image_bytes=result_image
                        )
                except Exception as e:
                    current_app.logger.warning(f"Failed to get Gemini evaluation: {e}")
                
                response_data = {
                    'success': True,
                    'result_url': f'/uploads/{result_filename}',
                    'hairstyle_id': hairstyle_id,
                    'hairstyle_name': description
                }
                
                if ai_evaluation:
                    response_data['ai_evaluation'] = ai_evaluation
                
                return response_data, 200
            else:
                return {'success': False, 'error': 'Failed to generate try-on image', 'code': 'GENERATION_FAILED'}, 500
        
        except ValueError as e:
            return {'success': False, 'error': str(e), 'code': 'VALIDATION_ERROR'}, 400
        
        except Exception as e:
            current_app.logger.error(f"Try-on error: {str(e)}")
            return {'success': False, 'error': 'An error occurred during try-on', 'code': 'INTERNAL_ERROR'}, 500


@ns_tryon.route('/variations')
class TryOnVariations(Resource):
    @ns_tryon.doc('try_on_variations')
    @ns_tryon.expect(ns_tryon.parser()
                .add_argument('image', type=FileStorage, location='files', required=True)
                .add_argument('hairstyle_id', type=str, location='form', required=True)
                .add_argument('num_variations', type=int, location='form', default=4))
    def post(self):
        """Generate multiple variations of a hairstyle try-on."""
        use_replicate = is_replicate_service_enabled()
        use_ultra = is_ultra_service_enabled()
        
        if not use_replicate and not use_ultra:
            return {'success': False, 'error': 'AI try-on feature is not enabled', 'code': 'FEATURE_DISABLED'}, 503
        
        if 'image' not in request.files:
            return {'success': False, 'error': 'No image file provided', 'code': 'NO_IMAGE'}, 400
        
        file = request.files['image']
        hairstyle_id = request.form.get('hairstyle_id')
        
        try:
            num_variations = int(request.form.get('num_variations', 4))
        except ValueError:
            num_variations = 4
        
        if num_variations < 1 or num_variations > 4:
            return {'success': False, 'error': 'num_variations must be between 1 and 4', 'code': 'INVALID_PARAMETER'}, 400
        
        if not hairstyle_id:
            return {'success': False, 'error': 'hairstyle_id is required', 'code': 'MISSING_PARAMETER'}, 400
        
        if file.filename == '' or not allowed_file(file.filename):
            return {'success': False, 'error': 'Invalid file', 'code': 'INVALID_FORMAT'}, 400
        
        try:
            hairstyle = hairstyle_db.get_hairstyle_by_id(hairstyle_id)
            if not hairstyle:
                return {'success': False, 'error': 'Hairstyle not found', 'code': 'NOT_FOUND'}, 404
            
            image_data = file.read()
            tags = ', '.join(hairstyle.get('tags', []))
            description = f"{hairstyle['name']}, {tags}"
            
            if use_replicate:
                replicate_service = get_replicate_hair_service()
                variation_images = replicate_service.generate_variations(
                    user_image_bytes=image_data,
                    hairstyle_description=description,
                    num_variations=num_variations
                )
            else:
                ultra_service = get_stable_image_ultra_service()
                variation_images = ultra_service.generate_variations(
                    user_image_bytes=image_data,
                    hairstyle_description=description,
                    num_variations=num_variations
                )
            
            if not variation_images:
                return {'success': False, 'error': 'Failed to generate variations', 'code': 'GENERATION_FAILED'}, 500
            
            upload_folder = current_app.config['UPLOAD_FOLDER']
            result_urls = []
            for i, variation_image in enumerate(variation_images):
                result_filename = f"tryon_{hairstyle_id}_var{i+1}_{uuid.uuid4().hex[:8]}.jpg"
                result_path = os.path.join(upload_folder, result_filename)
                
                with open(result_path, 'wb') as f:
                    f.write(variation_image)
                
                result_urls.append(f'/uploads/{result_filename}')
            
            return {
                'success': True,
                'result_urls': result_urls,
                'count': len(result_urls),
                'hairstyle_id': hairstyle_id,
                'hairstyle_name': hairstyle['name']
            }, 200
        
        except Exception as e:
            current_app.logger.error(f"Variations error: {str(e)}")
            return {'success': False, 'error': 'An error occurred', 'code': 'INTERNAL_ERROR'}, 500


@ns_tryon.route('/status')
class TryOnStatus(Resource):
    @ns_tryon.doc('try_on_status')
    def get(self):
        """Check if AI try-on feature is available."""
        if is_replicate_service_enabled():
            replicate_service = get_replicate_hair_service()
            status = replicate_service.check_api_status()
            return {'success': True, 'enabled': status.get('enabled', False), 'service': 'replicate', 'status': status.get('status', 'unknown')}, 200
        elif is_ultra_service_enabled():
            ultra_service = get_stable_image_ultra_service()
            status = ultra_service.check_api_status()
            return {'success': True, 'enabled': status.get('enabled', False), 'service': 'stability-ultra', 'status': status.get('status', 'unknown')}, 200
        else:
            return {'success': True, 'enabled': False, 'service': 'none', 'message': 'AI try-on feature is not configured'}, 200
