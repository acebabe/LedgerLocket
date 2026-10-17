from flask import Blueprint, request
from flask_socketio import emit, join_room
from app import socketio

bp = Blueprint("notifications", __name__)

# Socket events
@socketio.on("subscribe_wallet")
def handle_sub(data):
    # data = {"address": "0xabc..."}
    address = data.get("address")
    if not address:
        return
    join_room(f"wallet:{address}")
    emit("subscribed", {"address": address})