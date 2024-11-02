import os
from datetime import timedelta

class BaseConfig:
    # Flask settings
    SECRET_KEY = os.environ.get('FLASK_SECRET_KEY', 'a-very-secure-secret-key')
    DEBUG = False

    # Database settings
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_recycle": 300,
        "pool_pre_ping": True,
    }

    # JWT settings
    JWT_SECRET_KEY = SECRET_KEY
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)

    # API settings
    API_TITLE = 'Secure REST API'
    API_VERSIONS = ['v1', 'v2']
    API_DEFAULT_VERSION = 'v1'
    API_VERSION = '2.0'
    API_DESCRIPTION = '''A secure REST API with JWT authentication
    
    Available versions:
    - v1: Basic API functionality
    - v2: Enhanced API with additional user information'''

    # Rate limiting
    RATELIMIT_DEFAULT = "100/hour"
    RATELIMIT_STORAGE_URL = "memory://"
    
    # Ollama settings
    OLLAMA_API_URL = os.environ.get('OLLAMA_API_URL', 'http://localhost:11434')
    OLLAMA_MODEL = os.environ.get('OLLAMA_MODEL', 'llama2')

class TestConfig(BaseConfig):
    TESTING = True
    DEBUG = False
    
    # Use test database configuration
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    
    # Shorter token expiration for testing
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=5)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(minutes=10)
    
    # Disable rate limiting for tests
    RATELIMIT_ENABLED = False
    
    # Test-specific database settings
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
        "pool_size": 5,
        "max_overflow": 0,
        "pool_timeout": 30,
        "echo": True,
        "isolation_level": "READ COMMITTED"
    }
    
    # Preserve SQLAlchemy sessions for testing
    PRESERVE_CONTEXT_ON_EXCEPTION = False

Config = TestConfig if os.environ.get('FLASK_TESTING') else BaseConfig
