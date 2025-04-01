import pytest
from flask import Flask, request
from app import db
from app.models import User
from app.Services.auth_service import AuthService
from app.Services.jwt_service import JWTService

@pytest.fixture
def app():
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["JWT_KEY"] = "testkey"
    db.init_app(app)
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

def test_register_user_success(app):
    with app.app_context():
        data = {
            "name": "Test User",
            "email": "test@example.com",
            "password": "StrongP@ssw0rd"
        }
        response, status = AuthService.register_user(data)
        assert status == 201
        assert "user" in response

def test_register_user_missing_fields(app):
    with app.app_context():
        data = {"email": "test@example.com"}  # Missing password and name
        response, status = AuthService.register_user(data)
        assert status == 400
        assert "error" in response

def test_register_user_weak_password(app):
    with app.app_context():
        data = {
            "name": "Weak",
            "email": "weak@example.com",
            "password": "weak"
        }
        response, status = AuthService.register_user(data)
        assert status == 400
        assert "Password must be at least" in response["error"]

def test_login_user_success(app):
    with app.app_context():
        user = User(name="Test", email="login@example.com", role="user")
        user.set_password("StrongP@ssw0rd")
        db.session.add(user)
        db.session.commit()

        data = {"email": "login@example.com", "password": "StrongP@ssw0rd"}
        response, status = AuthService.login_user(data)
        assert status == 200
        assert "access_token" in response
        assert "refresh_token" in response

def test_login_user_wrong_credentials(app):
    with app.app_context():
        data = {"email": "nonexistent@example.com", "password": "wrongpass"}
        response, status = AuthService.login_user(data)
        assert status == 401
        assert response["error"] == "Invalid credentials"

def test_login_user_inactive(app):
    with app.app_context():
        user = User(name="Inactive", email="inactive@example.com", active=False)
        user.set_password("StrongP@ssw0rd")
        db.session.add(user)
        db.session.commit()

        data = {"email": "inactive@example.com", "password": "StrongP@ssw0rd"}
        response, status = AuthService.login_user(data)
        assert status == 403
        assert response["error"] == "Account is deactivated"

def test_refresh_token_success(app):
    with app.app_context():
        token = JWTService.generate_token(user_id=1, token_type="refresh", expires_in_minutes=10)
        data = {"refresh_token": token}
        response, status = AuthService.refresh_token(data)
        assert status == 200
        assert "access_token" in response

def test_refresh_token_invalid_type(app):
    with app.app_context():
        token = JWTService.generate_token(user_id=1, token_type="access", expires_in_minutes=10)
        data = {"refresh_token": token}
        response, status = AuthService.refresh_token(data)
        assert status == 401
        assert response["error"] == "Invalid token type"

def test_refresh_token_missing(app):
    with app.app_context():
        data = {}
        response, status = AuthService.refresh_token(data)
        assert status == 400
        assert response["error"] == "Missing refresh token"

def test_soft_deactivate_self(app):
    with app.app_context():
        user = User(name="Self", email="self@example.com", role="user")
        user.set_password("StrongP@ssw0rd")
        db.session.add(user)
        db.session.commit()

        token = JWTService.generate_token(user.id, token_type="access", role="user")

        class DummyRequest:
            def __init__(self):
                self.headers = {"Authorization": f"Bearer {token}"}
            def get_json(self):
                return {}

        response, status = AuthService.soft_deactivate(DummyRequest())
        assert status == 200
        assert response["message"] == f"User {user.email} has been deactivated"

def test_soft_deactivate_admin_can_deactivate_anyone(app):
    with app.app_context():
        target = User(name="Target", email="target@example.com")
        admin = User(name="Admin", email="admin@example.com", role="admin")
        target.set_password("StrongP@ssw0rd")
        admin.set_password("StrongP@ssw0rd")
        db.session.add_all([target, admin])
        db.session.commit()

        token = JWTService.generate_token(admin.id, token_type="access", role="admin")

        class DummyRequest:
            def __init__(self):
                self.headers = {"Authorization": f"Bearer {token}"}
            def get_json(self):
                return {"user_id": target.id}

        response, status = AuthService.soft_deactivate(DummyRequest())
        assert status == 200
        assert response["message"] == f"User {target.email} has been deactivated"

def test_user_cannot_deactivate_others(app):
    with app.app_context():
        user1 = User(name="User1", email="u1@example.com")
        user2 = User(name="User2", email="u2@example.com")
        user1.set_password("StrongP@ssw0rd")
        user2.set_password("StrongP@ssw0rd")
        db.session.add_all([user1, user2])
        db.session.commit()

        token = JWTService.generate_token(user1.id, token_type="access", role="user")

        class DummyRequest:
            def __init__(self):
                self.headers = {"Authorization": f"Bearer {token}"}
            def get_json(self):
                return {"user_id": user2.id}

        response, status = AuthService.soft_deactivate(DummyRequest())
        assert status == 403
        assert response["error"] == "Unauthorized to deactivate other users"

