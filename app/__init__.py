"""
Application factory and app-level setup.
"""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from config import Config

database = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()

def create_app(config_class=Config):
    """
    Application factory to create Flask app.
    """
    app = Flask(__name__)
    app.config.from_object(config_class)

    database.init_app(app)
    migrate.init_app(app, database)

    login_manager.init_app(app)
    login_manager.login_view = "auth.login"

    from app.main import main_blueprint, auth_blueprint
    app.register_blueprint(main_blueprint)
    app.register_blueprint(auth_blueprint)

    return app

@login_manager.user_loader
def load_user(user_id):
    from app.models import User
    return User.query.get(int(user_id))