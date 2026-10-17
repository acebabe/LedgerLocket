from . import blueprint
from flask import request, jsonify, current_app
from web3 import Web3
from decimal import Decimal
from app.services.wallet_service import WalletService
from app.services.notification_service import NotificationService
from app.extensions import db
from app.models.transaction import Transaction


def require_api_key(req):
    header = req.headers.get('X-API-Key')
    expected = current_app.config.get('TEST_API_KEY')
    return expected and header == expected


@blueprint.route('/wallets/send-test-coin', methods=['POST'])
def send_test_coin():
    if not require_api_key(request):
        return jsonify({'error': 'Unauthorized'}), 401

    data = request.get_json() or {}
    to_address = (data.get('to') or '').strip()
    amount = data.get('amount')
    chain_id = int(data.get('chain_id') or current_app.config.get('DEFAULT_CHAIN_ID'))
    note = data.get('note')

    if chain_id not in current_app.config.get('ALLOWED_CHAIN_IDS', []):
        return jsonify({'error':'chain_not_allowed'}), 400

    if not Web3.is_address(to_address):
        return jsonify({'error':'invalid_address'}), 400

    try:
        amount_dec = Decimal(str(amount))
    except Exception:
        return jsonify({'error':'invalid_amount'}), 400

    if amount_dec <= 0 or amount_dec > Decimal(str(current_app.config.get('TEST_MAX_AMOUNT_ETHER',0.1))):
        return jsonify({'error':'amount_out_of_bounds'}), 400

    ws = WalletService(current_app)
    result = ws.send_native_token(to_address, amount_dec, chain_id)

    tx = Transaction(tx_hash=result.get('tx_hash'), from_address=result.get('from'), to_address=to_address, amount=float(amount_dec), chain_id=chain_id, status=result.get('status'), note=note)
    db.session.add(tx)
    db.session.commit()

    ns = NotificationService(current_app)
    ns.notify_address(to_address, f"You received {amount_dec} test ETH (chain {chain_id})", tx_id=tx.id, email=None)

    return jsonify({'status': result.get('status'), 'tx_hash': result.get('tx_hash')}), 200
