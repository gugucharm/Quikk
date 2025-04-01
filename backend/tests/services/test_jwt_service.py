import pytest
import jwt
from datetime import datetime, timedelta
from app.Services.jwt_service import JWTService
from flask import Flask

@pytest.fixture
def app():
    app = Flask(__name__)
    app.config["JWT_KEY"] = "testsecretkey"
    return app


def test_generate_token_valid(app):
    with app.app_context():
        token = JWTService.generate_token(user_id=1, token_type="access", expires_in_minutes=15)
        decoded = jwt.decode(token, app.config["JWT_KEY"], algorithms=["HS256"])
        assert decoded["user_id"] == 1
        assert decoded["type"] == "access"
        assert "exp" in decoded


def test_generate_token_invalid_type(app):
    with app.app_context():
        with pytest.raises(ValueError):
            JWTService.generate_token(user_id=1, token_type="invalid", expires_in_minutes=15)


def test_generate_token_invalid_user_id(app):
    with app.app_context():
        with pytest.raises(ValueError):
            JWTService.generate_token(user_id="not_an_int", token_type="access", expires_in_minutes=15)


def test_generate_token_invalid_expiry(app):
    with app.app_context():
        with pytest.raises(ValueError):
            JWTService.generate_token(user_id=1, token_type="access", expires_in_minutes=0)


def test_decode_token_valid(app):
    with app.app_context():
        token = JWTService.generate_token(user_id=1, token_type="access", expires_in_minutes=1)
        payload = JWTService.decode_token(token)
        assert payload["user_id"] == 1
        assert payload["type"] == "access"


def test_decode_token_expired(app):
    with app.app_context():
        expired_token = jwt.encode({
            "user_id": 1,
            "type": "access",
            "exp": datetime.utcnow() - timedelta(minutes=1)
        }, app.config["JWT_KEY"], algorithm="HS256")

        result = JWTService.decode_token(expired_token)
        assert result["error"] == "Token has expired"


def test_decode_token_invalid_format(app):
    with app.app_context():
        result = JWTService.decode_token(12345)
        assert result["error"] == "Invalid token format"


def test_decode_token_invalid_signature(app):
    with app.app_context():
        invalid_token = jwt.encode({"some": "payload"}, "wrongkey", algorithm="HS256")
        result = JWTService.decode_token(invalid_token)
        assert result["error"] == "Invalid token"
