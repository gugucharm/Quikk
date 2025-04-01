import pytest
from flask import Flask
from app import db
from app.models.article import Article
from app.Services.article_service import ArticleService

@pytest.fixture
def app():
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.init_app(app)
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()


def test_create_article_success(app):
    with app.app_context():
        data = {
            "title": "Breaking News",
            "content": "Something big happened in crypto!",
            "author": "Admin",
            "tags": ["Crypto", "Bitcoin"]
        }
        response, status = ArticleService.create_article(data)
        assert status == 201
        assert response.json["title"] == "Breaking News"


def test_create_article_missing_fields(app):
    with app.app_context():
        data = {"title": "No Content"}  # content missing
        response, status = ArticleService.create_article(data)
        assert status == 400
        assert "error" in response.json


def test_create_article_invalid_tags(app):
    with app.app_context():
        data = {
            "title": "Bad Tags",
            "content": "Wrong tag format",
            "tags": 12345  # Invalid
        }
        response, status = ArticleService.create_article(data)
        assert status == 400
        assert response.json["error"] == "Tags must be a string or list."


def test_get_article_by_id(app):
    with app.app_context():
        data = {
            "title": "Get Me",
            "content": "Find this",
            "author": "Test"
        }
        response, status = ArticleService.create_article(data)
        assert status == 201

        article_id = response.json["id"]
        fetched = ArticleService.get_article_by_id(article_id)
        assert fetched.json["title"] == "Get Me"


def test_update_article(app):
    with app.app_context():
        data = {
            "title": "Old",
            "content": "Old content"
        }
        created, _ = ArticleService.create_article(data)
        article_id = created.json["id"]

        update_data = {"title": "Updated", "tags": ["edited"]}
        response = ArticleService.update_article(article_id, update_data)
        assert response.json["title"] == "Updated"
        assert "edited" in response.json["tags"]


def test_delete_article(app):
    with app.app_context():
        data = {
            "title": "Delete Me",
            "content": "Soon gone"
        }
        created, _ = ArticleService.create_article(data)
        article_id = created.json["id"]

        response = ArticleService.delete_article(article_id)
        assert response.json["message"] == "Article deleted."
        assert Article.query.get(article_id) is None


def test_get_article_by_slug(app):
    with app.app_context():
        data = {
            "title": "Crypto Moon Shot",
            "content": "Going to the moon!",
            "author": "SpaceBro"
        }
        created, _ = ArticleService.create_article(data)
        slug = created.json["slug"]

        response = ArticleService.get_article_by_slug(slug)
        assert response.json["title"] == data["title"]
        assert response.json["slug"] == slug


def test_slug_generation_collision(app):
    with app.app_context():
        ArticleService.create_article({
            "title": "Bitcoin",
            "content": "BTC surge",
        })
        ArticleService.create_article({
            "title": "Bitcoin",
            "content": "BTC update",
        })

        articles = Article.query.all()
        slugs = [a.slug for a in articles]
        assert len(set(slugs)) == len(slugs)

def test_create_article_with_string_tags(app):
    with app.app_context():
        data = {
            "title": "String Tags",
            "content": "Comma separated tags",
            "tags": "tag1,tag2"
        }
        response, status = ArticleService.create_article(data)
        assert status == 201
        assert response.json["tags"] == ["tag1", "tag2"]

def test_update_article_no_title(app):
    with app.app_context():
        data = {
            "title": "Original Title",
            "content": "Initial content"
        }
        created, _ = ArticleService.create_article(data)
        article_id = created.json["id"]
        old_slug = created.json["slug"]

        update_data = {"content": "Updated only"}
        updated = ArticleService.update_article(article_id, update_data)
        assert updated.json["content"] == "Updated only"
        assert updated.json["slug"] == old_slug  # slug unchanged

def test_get_all_articles(app):
    with app.app_context():
        ArticleService.create_article({"title": "Old", "content": "1"})
        ArticleService.create_article({"title": "New", "content": "2"})
        response = ArticleService.get_all_articles()
        titles = [a["title"] for a in response.json]
        assert titles == ["New", "Old"]
