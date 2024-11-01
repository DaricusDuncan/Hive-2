from datetime import datetime, timezone
from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import (
    create_access_token, create_refresh_token, get_jwt_identity,
    jwt_required, get_jwt, current_user
)
from core.database import db
from models.user import User
from models.token import TokenBlacklist
from api.schemas import user_schema, auth_schema
from core.security import limiter

auth_ns = Namespace('auth', description='Authentication operations')

login_model = auth_ns.model('Login', {
    'username': fields.String(required=True),
    'password': fields.String(required=True)
})

register_model = auth_ns.model('Register', {
    'username': fields.String(required=True),
    'email': fields.String(required=True),
    'password': fields.String(required=True)
})

@auth_ns.route('/register')
class Register(Resource):
    @limiter.limit("5/minute")
    @auth_ns.expect(register_model)
    @auth_ns.doc(responses={201: 'Success', 400: 'Validation Error'})
    def post(self):
        data = auth_ns.payload
        if User.query.filter_by(username=data['username']).first():
            return {'message': 'Username already exists'}, 400
        
        if User.query.filter_by(email=data['email']).first():
            return {'message': 'Email already exists'}, 400

        user = User()
        user.username = data['username']
        user.email = data['email']
        user.set_password(data['password'])

        db.session.add(user)
        db.session.commit()

        return user_schema.dump(user), 201

@auth_ns.route('/login')
class Login(Resource):
    @limiter.limit("10/minute")
    @auth_ns.expect(login_model)
    @auth_ns.doc(responses={200: 'Success', 401: 'Unauthorized'})
    def post(self):
        data = auth_ns.payload
        user = User.query.filter_by(username=data['username']).first()

        if not user or not user.check_password(data['password']):
            return {'message': 'Invalid credentials'}, 401

        access_token = create_access_token(identity=user.id)
        refresh_token = create_refresh_token(identity=user.id)

        return {
            'access_token': access_token,
            'refresh_token': refresh_token
        }, 200

@auth_ns.route('/refresh')
class TokenRefresh(Resource):
    @jwt_required(refresh=True)
    @auth_ns.doc(responses={200: 'Success', 401: 'Unauthorized'})
    def post(self):
        current_user_id = get_jwt_identity()
        access_token = create_access_token(identity=current_user_id)
        return {'access_token': access_token}, 200

@auth_ns.route('/logout')
class Logout(Resource):
    @jwt_required()
    @auth_ns.doc(responses={200: 'Success'})
    def post(self):
        token = get_jwt()
        jti = token["jti"]
        ttype = "access"
        now = datetime.now(timezone.utc)
        
        # Store the revoked token in the blacklist
        db_token = TokenBlacklist(
            jti=jti,
            token_type=ttype,
            user_id=get_jwt_identity(),
            expires_at=datetime.fromtimestamp(token["exp"], timezone.utc)
        )
        db.session.add(db_token)
        db.session.commit()
        
        return {'message': 'Token revoked successfully'}, 200

@auth_ns.route('/logout-refresh')
class LogoutRefresh(Resource):
    @jwt_required(refresh=True)
    @auth_ns.doc(responses={200: 'Success'})
    def post(self):
        token = get_jwt()
        jti = token["jti"]
        ttype = "refresh"
        now = datetime.now(timezone.utc)
        
        # Store the revoked refresh token in the blacklist
        db_token = TokenBlacklist(
            jti=jti,
            token_type=ttype,
            user_id=get_jwt_identity(),
            expires_at=datetime.fromtimestamp(token["exp"], timezone.utc)
        )
        db.session.add(db_token)
        db.session.commit()
        
        return {'message': 'Refresh token revoked successfully'}, 200
