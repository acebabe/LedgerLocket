from . import blueprint
from flask import jsonify
from app.models.ledger_account import LedgerAccount
from app.models.ledger_entry import LedgerEntry


@blueprint.route("/ledger/balance/<address>", methods=["GET"])
def get_balance(address):
    acct = LedgerAccount.query.filter_by(owner_address=address).first()
    if not acct:
        return jsonify({"address": address, "balance": 0.0, "locked_balance": 0.0})
    return jsonify({
        "address": address,
        "balance": float(acct.balance or 0.0),
        "locked_balance": float(acct.locked_balance or 0.0),
    })


@blueprint.route("/ledger/entries/<address>", methods=["GET"])
def list_entries(address):
    acct = LedgerAccount.query.filter_by(owner_address=address).first()
    if not acct:
        return jsonify([])
    entries = LedgerEntry.query.filter_by(account_id=acct.id).order_by(LedgerEntry.created_at.desc()).limit(200).all()
    return jsonify([{
        "id": e.id,
        "delta": float(e.delta),
        "balance_after": float(e.balance_after),
        "reason": e.reason,
        "locked": bool(e.locked),
        "created_at": e.created_at.isoformat() if e.created_at else None,
    } for e in entries])
