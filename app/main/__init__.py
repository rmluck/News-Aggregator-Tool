from flask import Blueprint

main_blueprint = Blueprint("main", __name__)
auth_blueprint = Blueprint("auth", __name__)

from app.main import routes