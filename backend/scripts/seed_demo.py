#!/usr/bin/env python

"""
Seed demo data into the LedgerLocket database.
Run: docker-compose exec web python scripts/seed_demo.py
"""

from app import create_app
from app.extensions import db
from app.models import User, Wallet, Transaction, AuditLog

app = create_app()

with app.app_context():
    db.create_all()
    if not User.query.filter_by(email='admin@ledgerlocket.local').first():
        admin = User(email='admin@ledgerlocket.local')
        admin.set_password('AdminPass123!')
        admin.roles = ['admin']
        db.session.add(admin)

    if not User.query.filter_by(email='alice@example.com').first():
        u = User(email='alice@example.com')
        u.set_password('password')
        db.session.add(u)
        db.session.flush()
        w = Wallet(address='0xAliceWallet', user_id=u.id, balance=100)
        db.session.add(w)
        tx = Transaction(tx_ref='demo-tx-1', to_addr=w.address, amount=100, type='mint', status='completed', data={'memo':'Initial demo credit'})
        db.session.add(tx)

    db.session.commit()
    print('Seeded demo data')
