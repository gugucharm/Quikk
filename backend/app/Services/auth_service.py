from app import db
from app.models import User
from app.Services.jwt_service import JWTService
from werkzeug.security import generate_password_hash
import re

class AuthService:
    @staticmethod
    def register_user(data):
        email = data.get("email", "").strip().lower()
        password = data.get("password", "").strip()
        name = data.get("name", "").strip()

        if not email or not password:
            return {"error": "Email and password required"}, 400

        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            return {"error": "Invalid email format"}, 400

        if not re.match(r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[\W_]).{8,}$", password):
            return {"error": "Password must be at least 8 characters long and include uppercase, lowercase, number, and special character."}, 400

        if not name:
            return {"error": "Name is required"}, 400

        if User.query.filter_by(email=email).first():
            return {"error": "Email already registered"}, 400

        user = User(name=name, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        return {"message": "User registered", "user": user.to_dict()}, 201

    @staticmethod
    def login_user(data):
        email = data.get("email", "").strip().lower()
        password = data.get("password", "").strip()

        if not email or not password:
            return {"error": "Email and password required"}, 400

        user = User.query.filter_by(email=email).first()

        if not user:
            return {"error": "Invalid credentials"}, 401

        if not user.active:
            return {"error": "Account is deactivated"}, 403

        if user.check_password(password):
            access_token = JWTService.generate_token(user.id, token_type="access", expires_in_minutes=15, role=user.role)
            refresh_token = JWTService.generate_token(user.id, token_type="refresh", expires_in_minutes=60 * 24 * 7)
            return {
                "access_token": access_token,
                "refresh_token": refresh_token
            }, 200

        return {"error": "Invalid credentials"}, 401


    @staticmethod
    def refresh_token(data):
        token = data.get("refresh_token")
        if not token:
            return {"error": "Missing refresh token"}, 400

        payload = JWTService.decode_token(token)
        if "error" in payload:
            return payload, 401

        if payload.get("type") != "refresh":
            return {"error": "Invalid token type"}, 401

        new_access_token = JWTService.generate_token(payload["user_id"], token_type="access", expires_in_minutes=15)
        return {"access_token": new_access_token}, 200
    
    @staticmethod
    def soft_deactivate(request):
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return {"error": "Missing or invalid token"}, 401

        token = auth_header.split(" ")[1]
        payload = JWTService.decode_token(token)
        if "error" in payload:
            return payload, 401

        requester_id = payload.get("user_id")
        requester_role = payload.get("role")

        data = request.get_json() or {}
        target_id = data.get("user_id") or requester_id

        if requester_role == "user" and target_id != requester_id:
            return {"error": "Unauthorized to deactivate other users"}, 403

        user = User.query.get(target_id)
        if not user or not user.active:
            return {"error": "User not found or already inactive"}, 404

        user.active = False
        db.session.commit()
        return {"message": f"User {user.email} has been deactivated"}, 200

