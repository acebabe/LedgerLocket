from flask import Blueprint, request, jsonify, current_app
from .extensions import db
from .models import User, Wallet, Transaction, AuditLog
from datetime import datetime
import uuid

bp = Blueprint('routes', __name__)

@bp.route('/health')
def health():
    return jsonify({'status':'ok'})

@bp.route('/auth/register', methods=['POST'])
def register():
    data = request.get_json() or {}
    email = data.get('email')
    password = data.get('password')
    if not email or not password:
        return jsonify({'error':'missing fields'}), 400
    u = User(email=email)
    u.set_password(password)
    db.session.add(u)
    db.session.commit()
    # TODO: send verification email
    return jsonify({'id':u.id, 'email':u.email}), 201

@bp.route('/wallets/<address>/balance')
def wallet_balance(address):
    w = Wallet.query.filter_by(address=address).first()
    if not w:
        return jsonify({'address':address, 'balance':'0.0'})
    return jsonify({'address':w.address, 'balance':str(w.balance)})

@bp.route('/transactions/mint', methods=['POST'])
def mint():
    data = request.get_json() or {}
    to = data.get('to_address')
    amount = data.get('amount')
    memo = data.get('memo')
    if not to or not amount:
        return jsonify({'error':'missing fields'}), 400
    tx = Transaction(
        tx_ref=str(uuid.uuid4()),
        from_addr=None,
        to_addr=to,
        amount=amount,
        type='mint',
        status='completed',
        data={'memo': memo}
    )
    w = Wallet.query.filter_by(address=to).first()
    if not w:
        w = Wallet(address=to, balance=0)
        db.session.add(w)
    w.balance = (w.balance or 0) + float(amount)
    db.session.add(tx)
    # audit
    audit = AuditLog(actor_id=None, action='mint', object_type='transaction', object_id=tx.tx_ref, reason=memo or 'minted via API')
    db.session.add(audit)
    db.session.commit()
    return jsonify({'tx_ref':tx.tx_ref}), 201
