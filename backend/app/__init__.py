from flask import Flask
from config import Config
from app.extensions import db, migrate
from app.models.user import User
from app.cli.commands import register_cli_commands

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)

    from app.controllers.auth_controller import auth_routes
    from app.controllers.article_controller import article_routes
    from app.controllers.god_controller import god_routes

    app.register_blueprint(auth_routes)
    app.register_blueprint(article_routes)
    app.register_blueprint(god_routes)

    register_cli_commands(app)

    return app
