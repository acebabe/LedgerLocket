from flask import Blueprint, request, jsonify, current_app
from .extensions import db
from .models import Transaction, Wallet, AuditLog
import uuid

bp = Blueprint('routes', __name__)

@bp.route('/health')
def health():
    return jsonify({'status':'ok'})

@bp.route('/wallets/<address>/balance')
def wallet_balance(address):
    w = Wallet.query.filter_by(address=address).first()
    if not w:
        return jsonify({'address':address, 'balance':'0.0'})
    return jsonify({'address':w.address, 'balance':str(w.balance)})

@bp.route('/wallets/me')
def wallets_me():
    # placeholder: in real app derive from auth
    return jsonify({'wallets':[]})

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
    w.balance = (float(w.balance) if w.balance else 0) + float(amount)
    db.session.add(tx)
    audit = AuditLog(actor_id=None, action='mint', object_type='transaction', object_id=tx.tx_ref, reason=memo or 'minted via API')
    db.session.add(audit)
    db.session.commit()
    # enqueue notification (if celery running)
    try:
        from .tasks import send_notification_task
        send_notification_task.delay(to, 'credit', {'amount':str(amount), 'tx_ref':tx.tx_ref})
    except Exception:
        current_app.logger.exception('Failed to enqueue notification')
    return jsonify({'tx_ref':tx.tx_ref}), 201
