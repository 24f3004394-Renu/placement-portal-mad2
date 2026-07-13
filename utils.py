from functools import wraps
from flask import abort
from flask_jwt_extended import verify_jwt_in_request, get_jwt, get_jwt_identity


def role_required(role):
    
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            verify_jwt_in_request()
            user_role = get_jwt().get('role')
            if user_role != role:
                abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def get_current_user():
    
    from models import Admin, Company, Student
    role = get_jwt().get('role')
    uid = int(get_jwt_identity())
    model = {'admin': Admin, 'company': Company, 'student': Student}.get(role)
    return model.query.get(uid) if model else None