from enum import Enum
from functools import wraps
from flask import request, abort

class APIVersion(Enum):
    V1 = "v1"
    V2 = "v2"

def version_required(min_version: APIVersion):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Extract version from request path
            path_parts = request.path.split('/')
            try:
                current_version = next(part for part in path_parts if part.startswith('v'))
                if APIVersion(current_version).value < min_version.value:
                    abort(404)
            except (StopIteration, ValueError):
                abort(404)
            return f(*args, **kwargs)
        return decorated_function
    return decorator
