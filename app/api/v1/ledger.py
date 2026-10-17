from . import blueprint
from flask import request, jsonify
from app.services.ledger_service import LedgerService


@blueprint.route('/ledger/balance', methods=['GET'])
def get_balance():
    address = request.args.get('address')
    if not address:
        return jsonify({'error': 'address_required'}), 400
    bal = LedgerService.get_balance(address)
    locked = LedgerService.get_locked_balance(address)
    return jsonify({'address': address, 'balance': bal, 'locked': locked}), 200
