import click
from flask import current_app
from app import db
from app.models.user import User

def register_cli_commands(app):
    @app.cli.command("create-god")
    def create_god():
        """Creates the god user if not exists."""
        with app.app_context():
            god_email = "god@example.com"
            if not User.query.filter_by(email=god_email).first():
                god = User(name="God", email=god_email, role="god")
                god.set_password("supersecretgodpassword")
                db.session.add(god)
                db.session.commit()
                click.echo("✅ God user created.")
            else:
                click.echo("⚠️ God user already exists.")
