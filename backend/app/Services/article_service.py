from app import db
from app.models.article import Article
from flask import jsonify
from datetime import datetime
import re

class ArticleService:
    @staticmethod
    def get_all_articles():
        articles = Article.query.order_by(Article.published_at.desc()).all()
        return jsonify([a.to_dict() for a in articles])

    @staticmethod
    def get_article_by_id(article_id):
        article = Article.query.get_or_404(article_id)
        return jsonify(article.to_dict())

    @staticmethod
    def get_article_by_slug(slug):
        article = Article.query.filter_by(slug=slug).first_or_404()
        return jsonify(article.to_dict())

    @staticmethod
    def create_article(data):
        title = str(data.get("title", "")).strip()
        content = str(data.get("content", "")).strip()
        author = str(data.get("author", "Anonymous")).strip()
        tags = data.get("tags", "")

        if not title or not content:
            return jsonify({"error": "Title and content are required."}), 400

        if not isinstance(tags, (str, list)):
            return jsonify({"error": "Tags must be a string or list."}), 400

        tag_string = ",".join(tags) if isinstance(tags, list) else str(tags).strip()
        slug = ArticleService.generate_slug(title)

        article = Article(
            title=title,
            content=content,
            author=author,
            tags=tag_string,
            slug=slug
        )
        db.session.add(article)
        db.session.commit()
        return jsonify(article.to_dict()), 201

    @staticmethod
    def update_article(article_id, data):
        article = Article.query.get_or_404(article_id)

        title = data.get("title")
        content = data.get("content")
        author = data.get("author")
        tags = data.get("tags")

        if title:
            article.title = str(title).strip()
            article.slug = ArticleService.generate_slug(title)
        if content:
            article.content = str(content).strip()
        if author:
            article.author = str(author).strip()
        if tags:
            article.tags = ",".join(tags) if isinstance(tags, list) else str(tags).strip()

        db.session.commit()
        return jsonify(article.to_dict())

    @staticmethod
    def delete_article(article_id):
        article = Article.query.get_or_404(article_id)
        db.session.delete(article)
        db.session.commit()
        return jsonify({"message": "Article deleted."})

    @staticmethod
    def generate_slug(title):
        slug = re.sub(r"[^a-zA-Z0-9]+", "-", title.strip().lower())
        slug = slug.strip("-")
        base_slug = slug
        counter = 1
        while Article.query.filter_by(slug=slug).first():
            slug = f"{base_slug}-{counter}"
            counter += 1
        return slug