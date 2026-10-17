from flask import Blueprint

blueprint = Blueprint('v1', __name__)

from . import health, auth, wallets, notifications  # noqa: E402,F401
