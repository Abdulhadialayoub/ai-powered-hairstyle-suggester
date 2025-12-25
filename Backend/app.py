"""
AI Hairstyle Suggester API

Main Flask application entry point.
All routes are organized in the routes/ package.
"""

from flask import Flask, send_file
from flask_cors import CORS
import os

app = Flask(__name__)

# Enable CORS for frontend development
CORS(app, resources={
    r"/api/*": {
        "origins": "http://localhost:3000",
        "supports_credentials": True
    }
})

# Configuration
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # 10MB max file size
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['RESTX_MASK_SWAGGER'] = False

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Initialize API with all routes
from routes import init_api
api = init_api(app)


# Static file serving
@app.route('/uploads/<filename>')
def serve_upload(filename):
    """Serve uploaded/generated files."""
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if os.path.exists(filepath):
        return send_file(filepath, mimetype='image/jpeg')
    else:
        return {'success': False, 'error': 'File not found'}, 404


@app.route('/api/health')
def health_check():
    """Health check endpoint."""
    return {
        'status': 'healthy',
        'message': 'AI Hairstyle Suggester API is running'
    }, 200


@app.errorhandler(413)
def request_entity_too_large(error):
    """Handle file size exceeding MAX_CONTENT_LENGTH."""
    return {
        'success': False,
        'error': 'Image file size exceeds 10MB limit',
        'code': 'FILE_TOO_LARGE'
    }, 413


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
