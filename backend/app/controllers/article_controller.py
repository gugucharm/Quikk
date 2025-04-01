from flask import Blueprint, request, jsonify
from app.Services.article_service import ArticleService
from app.Services.role_required import require_role

article_routes = Blueprint("article_routes", __name__)

@article_routes.route("/articles", methods=["GET"])
def get_articles():
    return ArticleService.get_all_articles()

@article_routes.route("/articles/<int:article_id>", methods=["GET"])
@require_role("admin")
def get_article(article_id):
    return ArticleService.get_article_by_id(article_id)

@article_routes.route("/articles/slug/<slug>", methods=["GET"])
def get_article_by_slug(slug):
    return ArticleService.get_article_by_slug(slug)

@article_routes.route("/articles", methods=["POST"])
@require_role("author")
def create_article():
    data = request.get_json()
    return ArticleService.create_article(data)

@article_routes.route("/articles/<int:article_id>", methods=["PUT"])
@require_role("author")
def update_article(article_id):
    data = request.get_json()
    return ArticleService.update_article(article_id, data)

@article_routes.route("/articles/<int:article_id>", methods=["DELETE"])
@require_role("admin")
def delete_article(article_id):
    return ArticleService.delete_article(article_id)
