"""Authentication routes."""

from flask import request, session
from flask_restx import Namespace, Resource, fields
from services.auth_service import get_auth_service

ns_auth = Namespace('auth', description='Authentication operations')

# Models
register_model = ns_auth.model('Register', {
    'username': fields.String(required=True, description='Username (min 3 characters)', example='john_doe'),
    'email': fields.String(required=True, description='Email address', example='john@example.com'),
    'password': fields.String(required=True, description='Password (min 6 characters)', example='password123')
})

login_model = ns_auth.model('Login', {
    'username': fields.String(required=True, description='Username', example='john_doe'),
    'password': fields.String(required=True, description='Password', example='password123')
})

auth_response_model = ns_auth.model('AuthResponse', {
    'success': fields.Boolean(description='Operation success status'),
    'message': fields.String(description='Response message'),
    'username': fields.String(description='Username'),
    'email': fields.String(description='Email address'),
    'session_token': fields.String(description='Session token')
})


@ns_auth.route('/register')
class Register(Resource):
    @ns_auth.doc('register_user')
    @ns_auth.expect(register_model)
    @ns_auth.response(200, 'Success', auth_response_model)
    @ns_auth.response(400, 'Bad Request')
    def post(self):
        """Register a new user."""
        data = request.get_json()
        
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        
        auth_service = get_auth_service()
        result = auth_service.register(username, email, password)
        
        if result['success']:
            return result, 200
        else:
            return result, 400


@ns_auth.route('/login')
class Login(Resource):
    @ns_auth.doc('login_user')
    @ns_auth.expect(login_model)
    @ns_auth.response(200, 'Success', auth_response_model)
    @ns_auth.response(401, 'Unauthorized')
    def post(self):
        """Login user."""
        data = request.get_json()
        
        username = data.get('username')
        password = data.get('password')
        
        auth_service = get_auth_service()
        result = auth_service.login(username, password)
        
        if result['success']:
            session['username'] = username
            session['session_token'] = result['session_token']
            return result, 200
        else:
            return result, 401


@ns_auth.route('/logout')
class Logout(Resource):
    @ns_auth.doc('logout_user')
    @ns_auth.response(200, 'Success')
    def post(self):
        """Logout user."""
        session_token = session.get('session_token')
        
        if session_token:
            auth_service = get_auth_service()
            auth_service.logout(session_token)
        
        session.clear()
        
        return {'success': True, 'message': 'Logged out successfully'}, 200


@ns_auth.route('/me')
class CurrentUser(Resource):
    @ns_auth.doc('get_current_user')
    @ns_auth.response(200, 'Success')
    @ns_auth.response(401, 'Unauthorized')
    def get(self):
        """Get current user information."""
        username = session.get('username')
        
        if not username:
            return {'success': False, 'error': 'Not authenticated'}, 401
        
        auth_service = get_auth_service()
        user_info = auth_service.get_user_info(username)
        
        if user_info:
            return {'success': True, 'user': user_info}, 200
        else:
            return {'success': False, 'error': 'User not found'}, 404
