from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required, get_jwt_identity
from core.database import db
from models.user import User
from api.schemas import user_schema, users_schema

api_ns = Namespace('api', description='API operations')

@api_ns.route('/users')
class UserList(Resource):
    @jwt_required()
    @api_ns.doc(security='Bearer')
    def get(self):
        users = User.query.all()
        return users_schema.dump(users)

@api_ns.route('/users/<int:id>')
class UserResource(Resource):
    @jwt_required()
    @api_ns.doc(security='Bearer')
    def get(self, id):
        user = User.query.get_or_404(id)
        return user_schema.dump(user)

@api_ns.route('/profile')
class UserProfile(Resource):
    @jwt_required()
    @api_ns.doc(security='Bearer')
    def get(self):
        user_id = get_jwt_identity()
        user = User.query.get_or_404(user_id)
        return user_schema.dump(user)
