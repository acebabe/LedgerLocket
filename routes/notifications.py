from flask import Blueprint, jsonify, request
from flask_socketio import emit, join_room

from app import socketio

bp = Blueprint("notifications", __name__)


@socketio.on("subscribe_wallet")
def handle_sub(data):
    address = (data or {}).get("address")
    if not address:
        return
    join_room(f"wallet:{address}")
    emit("subscribed", {"address": address})


@bp.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})
