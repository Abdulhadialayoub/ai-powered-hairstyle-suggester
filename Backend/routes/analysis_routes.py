"""Face analysis routes."""

from flask import request, current_app
from flask_restx import Namespace, Resource, fields
from werkzeug.datastructures import FileStorage
from services.face_analysis import (
    FaceAnalyzer,
    NoFaceDetectedError,
    MultipleFacesDetectedError,
    ImageProcessingError
)

ns_analysis = Namespace('analysis', description='Face shape analysis operations')

# Allowed file extensions
ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'webp'}

# Initialize face analyzer
face_analyzer = FaceAnalyzer()

# Models
measurements_model = ns_analysis.model('Measurements', {
    'face_length': fields.Float(description='Face length in pixels'),
    'face_width': fields.Float(description='Face width in pixels'),
    'forehead_width': fields.Float(description='Forehead width in pixels'),
    'jawline_width': fields.Float(description='Jawline width in pixels')
})

analysis_result_model = ns_analysis.model('AnalysisResult', {
    'success': fields.Boolean(description='Operation success status', example=True),
    'face_shape': fields.String(description='Detected face shape', example='oval'),
    'confidence': fields.Float(description='Confidence score (0-1)', example=0.87),
    'measurements': fields.Nested(measurements_model, description='Face measurements')
})

error_model = ns_analysis.model('Error', {
    'success': fields.Boolean(description='Operation success status', example=False),
    'error': fields.String(description='Error message'),
    'code': fields.String(description='Error code')
})


def allowed_file(filename):
    """Check if the file extension is allowed."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@ns_analysis.route('/analyze')
class FaceAnalysis(Resource):
    @ns_analysis.doc('analyze_face')
    @ns_analysis.expect(ns_analysis.parser()
                .add_argument('image', type=FileStorage, location='files', required=True,
                             help='Image file (JPEG, PNG, WebP, max 10MB)'))
    @ns_analysis.response(200, 'Success', analysis_result_model)
    @ns_analysis.response(400, 'Bad Request', error_model)
    def post(self):
        """Analyze uploaded image to detect face shape."""
        if 'image' not in request.files:
            return {'success': False, 'error': 'No image file provided', 'code': 'NO_IMAGE'}, 400
        
        file = request.files['image']
        
        if file.filename == '':
            return {'success': False, 'error': 'No image file selected', 'code': 'NO_IMAGE'}, 400
        
        if not allowed_file(file.filename):
            return {'success': False, 'error': 'Invalid file format', 'code': 'INVALID_FORMAT'}, 400
        
        try:
            image_data = file.read()
            
            if len(image_data) > 10 * 1024 * 1024:
                return {'success': False, 'error': 'Image file size exceeds 10MB limit', 'code': 'FILE_TOO_LARGE'}, 400
            
            # Hybrid Analysis: Rule-based + ML
            results = []
            
            # 1. Rule-based (Geometric) analysis
            geometric_result = face_analyzer.analyze_face_shape(image_data)
            results.append({
                'method': 'geometric',
                'face_shape': geometric_result['face_shape'],
                'confidence': geometric_result['confidence'],
                'measurements': geometric_result['measurements']
            })
            
            # 2. ML (CNN) analysis - if available
            try:
                from services.ml_face_analyzer import get_ml_face_analyzer, is_ml_model_available
                if is_ml_model_available():
                    ml_analyzer = get_ml_face_analyzer()
                    ml_result = ml_analyzer.analyze(image_data)
                    results.append({
                        'method': 'cnn',
                        'face_shape': ml_result['face_shape'],
                        'confidence': ml_result['confidence'],
                        'all_predictions': ml_result.get('all_predictions', {})
                    })
            except Exception as ml_error:
                current_app.logger.warning(f"ML analysis failed: {ml_error}")
            
            # Select best result
            best_result = max(results, key=lambda x: x['confidence'])
            
            return {
                'success': True,
                'face_shape': best_result['face_shape'],
                'confidence': best_result['confidence'],
                'method': best_result['method'],
                'measurements': geometric_result['measurements'],
                'all_results': results
            }, 200
        
        except NoFaceDetectedError:
            return {'success': False, 'error': 'No face detected in the image', 'code': 'NO_FACE'}, 400
        
        except MultipleFacesDetectedError:
            return {'success': False, 'error': 'Multiple faces detected', 'code': 'MULTIPLE_FACES'}, 400
        
        except ImageProcessingError as e:
            return {'success': False, 'error': 'Failed to process the image', 'code': 'PROCESSING_ERROR'}, 400
        
        except Exception as e:
            current_app.logger.error(f"Unexpected error in analyze_face: {str(e)}")
            return {'success': False, 'error': 'An unexpected error occurred', 'code': 'INTERNAL_ERROR'}, 500
