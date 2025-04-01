from app import db
from app.models.user import User
from werkzeug.security import generate_password_hash
import re

class GodService:
    @staticmethod
    def create_user(data):
        email = data.get("email", "").strip().lower()
        password = data.get("password", "").strip()
        name = data.get("name", "").strip()
        role = data.get("role", "user").strip().lower()

        if not email or not password or not name:
            return {"error": "Name, email, and password are required."}, 400

        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            return {"error": "Invalid email format."}, 400

        if not re.match(r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[\W_]).{8,}$", password):
            return {"error": "Password must be at least 8 characters long and include uppercase, lowercase, number, and special character."}, 400

        if role not in ["user", "author", "admin", "god"]:
            return {"error": "Invalid role."}, 400

        if User.query.filter_by(email=email).first():
            return {"error": "Email already exists."}, 400

        user = User(name=name, email=email, role=role)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        return {"message": "User created", "user": user.to_dict()}, 201
    
    @staticmethod
    def change_user_role_by_email(email, new_role):
        if new_role not in ["user", "author", "admin", "god"]:
            return {"error": "Invalid role specified."}, 400

        user = User.query.filter_by(email=email.strip().lower()).first()
        if not user:
            return {"error": "User not found."}, 404

        user.role = new_role
        db.session.commit()
        return {"message": f"User {user.email} role updated to {new_role}."}, 200
