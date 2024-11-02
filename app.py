from flask import Flask, url_for, send_from_directory
from flask_restx import Api
from flask_cors import CORS
from core.config import Config
from core.database import db
from core.security import jwt, talisman, limiter
from api.auth import auth_ns
from api.resources import api_ns
from api.github import github_ns
from models.user import User
from models.role import Role

def create_app():
    app = Flask(__name__, static_url_path='/static')
    app.config.from_object(Config)

    # Initialize CORS
    CORS(app)

    # Initialize extensions
    db.init_app(app)
    jwt.init_app(app)
    
    # Configure Talisman with relaxed CSP for Swagger UI
    csp = {
        'default-src': ["'self'"],
        'img-src': ["'self'", 'data:', 'https:'],
        'script-src': ["'self'", "'unsafe-inline'", "'unsafe-eval'"],
        'style-src': ["'self'", "'unsafe-inline'"],
        'connect-src': ["'self'", 'https:', 'http:'],
        'font-src': ["'self'", 'data:'],
    }
    talisman.init_app(app, content_security_policy=csp, force_https=False)
    limiter.init_app(app)

    # User loader for JWT
    @jwt.user_lookup_loader
    def user_lookup_callback(_jwt_header, jwt_data):
        identity = jwt_data["sub"]
        return User.query.filter_by(id=identity).one_or_none()

    # Serve static files
    @app.route('/static/<path:path>')
    def send_static(path):
        return send_from_directory('static', path)

    @app.route('/swaggerui/<path:filename>')
    def serve_swagger_ui(filename):
        return send_from_directory('static/swagger-ui', filename)

    # Initialize API with Swagger
    authorizations = {
        'Bearer': {
            'type': 'apiKey',
            'in': 'header',
            'name': 'Authorization'
        }
    }

    api = Api(
        app,
        version=Config.API_VERSION,
        title=Config.API_TITLE,
        description=Config.API_DESCRIPTION,
        authorizations=authorizations,
        security='Bearer',
        doc='/',
        prefix='/api/v1'  # Default version prefix
    )

    # Register namespaces
    api.add_namespace(auth_ns)
    api.add_namespace(api_ns)
    api.add_namespace(github_ns)

    # Create database tables and default roles
    with app.app_context():
        db.create_all()
        
        # Create default roles if they don't exist
        default_roles = [
            ('admin', 'Administrator with full access'),
            ('moderator', 'Moderator with limited administrative access'),
            ('user', 'Regular user with basic access')
        ]
        
        for role_name, description in default_roles:
            if not Role.query.filter_by(name=role_name).first():
                role = Role(name=role_name, description=description)
                db.session.add(role)
        
        db.session.commit()

    return app

app = create_app()
