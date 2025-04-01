import jwt
import datetime
from flask import current_app

class JWTService:
    @staticmethod
    def generate_token(user_id, token_type="access", expires_in_minutes=15, role="user"):
        if token_type not in ("access", "refresh"):
            raise ValueError("Invalid token type. Must be 'access' or 'refresh'.")

        if not isinstance(user_id, int):
            raise ValueError("User ID must be an integer.")

        if not isinstance(expires_in_minutes, int) or expires_in_minutes <= 0:
            raise ValueError("expires_in_minutes must be a positive integer.")

        payload = {
        "user_id": user_id,
        "type": token_type,
        "role": role,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=expires_in_minutes)
        }

        return jwt.encode(payload, current_app.config["JWT_KEY"], algorithm="HS256")

    @staticmethod
    def decode_token(token):
        if not isinstance(token, str) or not token.strip():
            return {"error": "Invalid token format"}

        try:
            return jwt.decode(token, current_app.config["JWT_KEY"], algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            return {"error": "Token has expired"}
        except jwt.InvalidTokenError:
            return {"error": "Invalid token"}
