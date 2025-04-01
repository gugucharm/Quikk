from flask import Blueprint, request, jsonify
from app.Services.auth_service import AuthService

auth_routes = Blueprint("auth_routes", __name__)

@auth_routes.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    response, status = AuthService.register_user(data)
    return jsonify(response), status

@auth_routes.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    response, status = AuthService.login_user(data)
    return jsonify(response), status

@auth_routes.route("/refresh", methods=["POST"])
def refresh():
    data = request.get_json()
    response, status = AuthService.refresh_token(data)
    return jsonify(response), status

@auth_routes.route("/deactivate", methods=["PUT"])
def deactivate_account():
    response, status = AuthService.soft_deactivate(request)
    return jsonify(response), status