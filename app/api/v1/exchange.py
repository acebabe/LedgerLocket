from . import blueprint
from flask import jsonify, request
from app.services.exchange_service import CoinbaseAdapter


@blueprint.route("/exchange/coinbase/ping", methods=["GET"])
def coinbase_ping():
    return jsonify(CoinbaseAdapter().ping())


@blueprint.route("/exchange/coinbase/deposit", methods=["POST"])
def coinbase_deposit():
    data = request.get_json() or {}
    currency = data.get("currency", "USD")
    amount = data.get("amount", 0)
    return jsonify(CoinbaseAdapter().create_deposit(currency, amount))
