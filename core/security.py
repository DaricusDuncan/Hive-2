from datetime import datetime
from flask_jwt_extended import JWTManager
from flask_talisman import Talisman
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from models.token import TokenBlacklist
from core.database import db

jwt = JWTManager()
talisman = Talisman()
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["100 per hour"],
    storage_uri="memory://",
)

@jwt.token_in_blocklist_loader
def check_if_token_revoked(jwt_header, jwt_payload):
    jti = jwt_payload["jti"]
    token = TokenBlacklist.query.filter_by(jti=jti).first()
    return token is not None

@jwt.revoked_token_loader
def revoked_token_callback(jwt_header, jwt_payload):
    return {
        'message': 'The token has been revoked.',
        'error': 'token_revoked'
    }, 401

@jwt.expired_token_loader
def expired_token_callback(jwt_header, jwt_payload):
    return {
        'message': 'The token has expired.',
        'error': 'token_expired'
    }, 401
