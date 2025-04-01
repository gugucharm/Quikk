from flask import Blueprint, request, jsonify
from config import Config
from app.Services.god_service import GodService
from app.Services.role_required import require_role

god_routes = Blueprint("god_routes", __name__)

@god_routes.route(Config.GOD_ROUTE, methods=["POST"])
@require_role("god")
def create_user_by_god():
    data = request.get_json()
    return GodService.create_user(data)

@god_routes.route(Config.GOD_ROUTE, methods=["PUT"])
@require_role("god")
def change_user_role_by_email():
    data = request.get_json()
    email = data.get("email")
    new_role = data.get("role")

    if not email or not new_role:
        return jsonify({"error": "Both email and role are required."}), 400

    response, status = GodService.change_user_role_by_email(email, new_role)
    return jsonify(response), status
