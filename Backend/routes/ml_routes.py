"""ML-based face analysis routes."""

from flask import request, current_app
from flask_restx import Namespace, Resource
from werkzeug.datastructures import FileStorage

ns_ml = Namespace('ml', description='ML-based face analysis')

ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'webp'}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@ns_ml.route('/analyze')
class MLFaceAnalysis(Resource):
    @ns_ml.doc('ml_analyze_face')
    @ns_ml.expect(ns_ml.parser()
                .add_argument('image', type=FileStorage, location='files', required=True,
                             help='Image file (JPEG, PNG, WebP)'))
    def post(self):
        """Analyze face shape using trained CNN model."""
        try:
            from services.ml_face_analyzer import get_ml_face_analyzer, is_ml_model_available
            
            if not is_ml_model_available():
                return {
                    'success': False,
                    'error': 'ML model not available. Please train the model first.',
                    'code': 'MODEL_NOT_AVAILABLE'
                }, 503
            
            if 'image' not in request.files:
                return {'success': False, 'error': 'No image file provided', 'code': 'NO_IMAGE'}, 400
            
            file = request.files['image']
            if file.filename == '' or not allowed_file(file.filename):
                return {'success': False, 'error': 'Invalid file', 'code': 'INVALID_FILE'}, 400
            
            image_data = file.read()
            
            ml_analyzer = get_ml_face_analyzer()
            result = ml_analyzer.analyze(image_data)
            
            return {
                'success': True,
                'face_shape': result['face_shape'],
                'confidence': result['confidence'],
                'all_predictions': result['all_predictions'],
                'method': 'cnn'
            }, 200
            
        except Exception as e:
            current_app.logger.error(f"ML analysis error: {str(e)}")
            return {'success': False, 'error': str(e), 'code': 'ML_ERROR'}, 500


@ns_ml.route('/status')
class MLStatus(Resource):
    @ns_ml.doc('ml_status')
    def get(self):
        """Check ML model status."""
        try:
            from services.ml_face_analyzer import is_ml_model_available
            
            return {
                'success': True,
                'ml_available': is_ml_model_available(),
                'model_info': {
                    'type': 'CNN',
                    'dataset': 'Kaggle Face Shape Dataset',
                    'classes': ['heart', 'oblong', 'oval', 'round', 'square']
                }
            }, 200
        except Exception as e:
            return {'success': False, 'ml_available': False, 'error': str(e)}, 200
