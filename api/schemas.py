from marshmallow import Schema, fields, validate

class UserSchema(Schema):
    id = fields.Int(dump_only=True)
    username = fields.Str(required=True, validate=validate.Length(min=3, max=64))
    email = fields.Email(required=True)
    password = fields.Str(required=True, load_only=True, validate=validate.Length(min=8))
    created_at = fields.DateTime(dump_only=True)
    is_active = fields.Bool(dump_only=True)

class AuthSchema(Schema):
    username = fields.Str(required=True)
    password = fields.Str(required=True)

user_schema = UserSchema()
users_schema = UserSchema(many=True)
auth_schema = AuthSchema()
