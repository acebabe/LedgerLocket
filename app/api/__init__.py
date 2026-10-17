from flask import Blueprint

api_bp = Blueprint("api", __name__)

from app.api.v1 import blueprint as v1_blueprint

api_bp.register_blueprint(v1_blueprint, url_prefix="/v1")
