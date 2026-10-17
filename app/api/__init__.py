from flask import Blueprint

api_bp = Blueprint('api', __name__)

# import and register v1
from app.api.v1 import router as v1_router

api_bp.register_blueprint(v1_router.blueprint, url_prefix='/v1')
