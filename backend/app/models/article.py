from datetime import datetime
from app import db

class Article(db.Model):
    __tablename__ = 'articles'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    author = db.Column(db.String(100))
    published_at = db.Column(db.DateTime, default=datetime.utcnow)
    tags = db.Column(db.String(200))  # optional: comma-separated
    slug = db.Column(db.String(255), unique=True, nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "content": self.content,
            "author": self.author,
            "tags": self.tags.split(",") if self.tags else [],
            "published_at": self.published_at.isoformat(),
            "slug": self.slug
        }
