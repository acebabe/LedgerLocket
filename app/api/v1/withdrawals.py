from . import blueprint
from flask import request, jsonify
from app.extensions import db
from app.models.wallet import Wallet
from app.models.ledger_account import LedgerAccount
from app.models.transaction import Transaction
from app.services.ledger_service import LedgerService
from app.services.audit_service import AuditService


def _user_from_token(header_value):
    if not header_value:
        return None
    token = header_value.split()[-1]
    if token.startswith('token-'):
        try:
            return int(token.split('-',1)[1])
        except Exception:
            return None
    return None


@blueprint.route('/withdrawals/request', methods=['POST'])
def request_withdrawal():
    auth = request.headers.get('Authorization')
    user_id = _user_from_token(auth)
    if not user_id:
        return jsonify({'error':'unauthenticated'}), 401
    data = request.get_json() or {}
    to_address = (data.get('to') or '').strip()
    amount = float(data.get('amount') or 0)

    # find wallets for user
    wallets = Wallet.query.filter_by(user_id=user_id).all()
    addresses = [w.address for w in wallets]
    # check whether any ledger account associated with user's addresses have locked funds
    for addr in addresses:
        locked = LedgerService.get_locked_balance(addr)
        if locked > 0:
            # record audit
            AuditService.record(actor=f'user:{user_id}', action='withdrawal_attempt_locked', payload={'address': addr, 'locked': locked})
            return jsonify({'error':'withdrawal_blocked_locked_funds', 'locked': locked}), 403
    # If no locked funds, proceed to create withdrawal request record
    # For demo we simply reject because credits are non-withdrawable by design
    AuditService.record(actor=f'user:{user_id}', action='withdrawal_attempt', payload={'addresses': addresses, 'requested_amount': amount})
    return jsonify({'error':'withdrawals_disabled', 'message':'Credits are non-withdrawable in this system'}), 403
