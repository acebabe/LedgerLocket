# Example real-data seed script for demo admin/user and wallet flows
from datetime import datetime

from app_factory import create_app
from models import db, User, Wallet, Transaction, Integration

app = create_app()

with app.app_context():
    db.create_all()

    if not User.query.filter_by(email="admin@ledgerlocket.local").first():
        admin = User(email="admin@ledgerlocket.local", roles=["admin"])
        admin.set_password("AdminPass123!")
        db.session.add(admin)

    if not User.query.filter_by(email="alice@example.com").first():
        u = User(email="alice@example.com", roles=["user"])
        u.set_password("password")
        db.session.add(u)
        db.session.flush()
        w = Wallet(address="0xAliceWallet", user_id=u.id, balance=100)
        db.session.add(w)
        tx = Transaction(
            tx_ref="demo-tx-001",
            to_address=w.address,
            amount=100,
            type="mint",
            data={"memo": "Initial demo credit"},
        )
        db.session.add(tx)

    if not Integration.query.filter_by(exchange_name="coinbase-sandbox").first():
        db.session.add(Integration(exchange_name="coinbase-sandbox", credentials_encrypted="stubbed", status="linked"))

    db.session.commit()
    print("Demo data seeded")
