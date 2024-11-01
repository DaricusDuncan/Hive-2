from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import create_access_token, create_refresh_token
from core.database import db
from models.user import User
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
