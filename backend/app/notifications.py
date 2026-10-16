from flask import Blueprint, request, jsonify
from flask_socketio import emit, join_room, leave_room
from .extensions import socketio

bp = Blueprint('notifications', __name__)

@bp.route('/subscribe', methods=['POST'])
def subscribe():
    data = request.get_json() or {}
    address = data.get('address')
    if not address:
        return jsonify({'error':'missing address'}), 400
    # In production, use authentication and socket.io join on connection
    return jsonify({'status':'subscribed', 'room': f'wallet:{address}'})

# socketio events
@socketio.on('connect')
def handle_connect():
    print('client connected')

@socketio.on('join_wallet')
def on_join(data):
    address = data.get('address')
    if address:
        room = f'wallet:{address}'
        join_room(room)
        emit('joined', {'room':room})

@socketio.on('leave_wallet')
def on_leave(data):
    address = data.get('address')
    if address:
        room = f'wallet:{address}'
        leave_room(room)
        emit('left', {'room':room})
