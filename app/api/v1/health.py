from . import blueprint
from flask import jsonify


@blueprint.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})
