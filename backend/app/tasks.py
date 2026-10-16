from .celery_app import init_celery, celery
from .app import create_app

app = create_app()
celery = init_celery(app)

@celery.task
def send_notification_task(wallet_address, event_type, payload):
    # Import here to avoid circular imports
    from .models import Notification
    from .extensions import db, socketio
    n = Notification(wallet_address=wallet_address, type=event_type, payload=payload)
    db.session.add(n)
    db.session.commit()
    # emit via socketio
    room = f"wallet:{wallet_address}"
    socketio.emit('notification', {'type':event_type, 'payload':payload}, room=room)

@celery.task
def generate_receipt_task(tx_ref):
    # Renders receipt PNG using Playwright (similar to receipts endpoint)
    from .models import Transaction
    from .receipts import RECEIPT_HTML_TEMPLATE
    from jinja2 import Template
    from playwright.sync_api import sync_playwright
    from io import BytesIO
    tx = Transaction.query.filter_by(tx_ref=tx_ref).first()
    if not tx:
        return None
    html = Template(RECEIPT_HTML_TEMPLATE).render(
        amount=str(tx.amount),
        to_address=tx.to_addr,
        from_address=tx.from_addr,
        timestamp=tx.created_at.strftime('%Y-%m-%d %H:%M:%S UTC'),
        memo=(tx.data or {}).get('memo',''),
        tx_ref=tx.tx_ref
    )
    with sync_playwright() as p:
        browser = p.chromium.launch(args=['--no-sandbox'])
        page = browser.new_page(viewport={'width':900,'height':600})
        page.set_content(html, wait_until='networkidle')
        png = page.screenshot(full_page=True)
        browser.close()
    # store png to UPLOAD_FOLDER
    from flask import current_app
    path = f"{current_app.config.get('UPLOAD_FOLDER')}/receipt_{tx_ref}.png"
    with open(path, 'wb') as f:
        f.write(png)
    return path
