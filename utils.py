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

def _cache():
    from extensions import cache
    return cache


def cache_version(entity):
    v = _cache().get(f'{entity}:ver')
    if v is None:
        v = 1
        _cache().set(f'{entity}:ver', v, timeout=0)  
    return v


def bump_cache_version(entity):
    _cache().set(f'{entity}:ver', cache_version(entity) + 1, timeout=0)


def search_cache_get(entity, query):
    return _cache().get(f'admin:{entity}:search:{query}:v{cache_version(entity)}')


def search_cache_set(entity, query, payload):
    _cache().set(f'admin:{entity}:search:{query}:v{cache_version(entity)}', payload)