from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required, get_jwt_identity
from core.database import db
from models.user import User
from models.role import Role
from api.schemas import user_schema, users_schema
from core.rbac import role_required, admin_required

api_ns = Namespace('api', description='API operations')

role_model = api_ns.model('Role', {
    'name': fields.String(required=True),
    'description': fields.String(required=False)
})

@api_ns.route('/users')
class UserList(Resource):
    @jwt_required()
    @admin_required
    @api_ns.doc(security='Bearer')
    def get(self):
        users = User.query.all()
        return users_schema.dump(users)

@api_ns.route('/users/<int:id>')
class UserResource(Resource):
    @jwt_required()
    @role_required('admin', 'moderator')
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

@api_ns.route('/roles')
class RoleList(Resource):
    @jwt_required()
    @admin_required
    @api_ns.doc(security='Bearer')
    @api_ns.expect(role_model, validate=True)
    def post(self):
        """Create a new role (Admin only)"""
        data = api_ns.payload
        if Role.query.filter_by(name=data['name']).first():
            return {'message': 'Role already exists'}, 400

        role = Role(name=data['name'], description=data.get('description', ''))
        db.session.add(role)
        db.session.commit()

        return {'message': 'Role created successfully'}, 201

    @jwt_required()
    @admin_required
    @api_ns.doc(security='Bearer')
    def get(self):
        """Get all roles (Admin only)"""
        roles = Role.query.all()
        return [{'id': role.id, 'name': role.name, 'description': role.description} 
                for role in roles]
