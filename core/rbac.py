from functools import wraps
from flask import jsonify
from flask_jwt_extended import get_current_user, verify_jwt_in_request

def role_required(*role_names):
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            try:
                verify_jwt_in_request()
                user = get_current_user()
                
                if not user or not user.has_any_role(role_names):
                    return jsonify({"msg": "Insufficient permissions"}), 403
                return fn(*args, **kwargs)
            except Exception:
                return jsonify({"msg": "Insufficient permissions"}), 403
        return decorator
    return wrapper

def admin_required(fn):
    return role_required('admin')(fn)
