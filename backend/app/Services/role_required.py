from functools import wraps
from flask import request, jsonify
from app.Services.jwt_service import JWTService

ROLE_TIERS = {
    "user": 1,
    "author": 2,
    "admin": 3,
    "god": 4
}

def require_role(min_role):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            auth_header = request.headers.get("Authorization")
            if not auth_header:
                return jsonify({"error": "Missing Authorization header"}), 401

            token = auth_header.split(" ")[-1]
            payload = JWTService.decode_token(token)
            if "error" in payload:
                return jsonify(payload), 401

            user_role = payload.get("role", "user")
            if ROLE_TIERS.get(user_role, 0) < ROLE_TIERS[min_role]:
                return jsonify({"error": "Insufficient privileges"}), 403

            return f(*args, **kwargs)
        return wrapper
    return decorator
