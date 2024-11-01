from flask import Flask
from flask_restx import Api
from flask_cors import CORS
from core.config import Config
from core.database import db
from core.security import jwt, talisman, limiter
from api.auth import auth_ns
from api.resources import api_ns

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize CORS
    CORS(app)

    # Initialize extensions
    db.init_app(app)
    jwt.init_app(app)
    
    # Configure Talisman with relaxed CSP for Swagger UI
    csp = {
        'default-src': "'self'",
        'img-src': "'self' data:",
        'script-src': "'self' 'unsafe-inline' 'unsafe-eval'",
        'style-src': "'self' 'unsafe-inline'",
    }
    talisman.init_app(app, content_security_policy=csp, force_https=False)
    limiter.init_app(app)

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
        doc='/',  # Swagger UI at root URL
        prefix='/api/v1'  # Add version prefix to all routes
    )

    # Register namespaces
    api.add_namespace(auth_ns)  # Will be prefixed with /api/v1
    api.add_namespace(api_ns)   # Will be prefixed with /api/v1

    # Create database tables
    with app.app_context():
        db.create_all()

    return app

app = create_app()
