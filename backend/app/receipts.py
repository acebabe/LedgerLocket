from flask import Blueprint, render_template_string, abort, send_file
from .models import Transaction
from jinja2 import Template
from io import BytesIO
from playwright.sync_api import sync_playwright

bp = Blueprint('receipts', __name__)

RECEIPT_HTML_TEMPLATE = """
<!doctype html>
<html>
<head>
  <meta charset="utf-8" />
  <style>
    body { font-family: Arial, sans-serif; background: #f7fafc; color: #0f172a; padding: 24px; }
    .card { width: 720px; margin: 0 auto; background: #fff; border-radius: 12px; padding: 24px; box-shadow: 0 8px 30px rgba(2,6,23,0.08); }
    .brand { display:flex; align-items:center; gap:12px; }
    .logo { width:48px; height:48px; border-radius:8px; background:linear-gradient(135deg,#6366f1,#06b6d4); display:inline-block; }
    h1 { margin: 0 0 8px 0; font-size:18px; }
    .amount { font-size: 28px; font-weight:700; margin-top: 12px; }
    .meta { color: #475569; margin-top: 8px; font-size:13px; }
    .footer { margin-top: 20px; color: #94a3b8; font-size:12px; }
    .badge { display:inline-block; padding:6px 8px; background:#f1f5f9; border-radius:8px; font-weight:600; color:#334155; font-size:12px; }
  </style>
</head>
<body>
  <div class="card">
    <div class="brand">
      <div class="logo"></div>
      <div>
        <div style="font-weight:700">LedgerLocket</div>
        <div style="font-size:12px;color:#64748b">Non-withdrawable credit receipt</div>
      </div>
      <div style="margin-left:auto"><span class="badge">Non-withdrawable</span></div>
    </div>

    <h1>Credit received</h1>
    <div class="amount">{{ amount }} LCK</div>
    <div class="meta">To: {{ to_address }}<br/>From: {{ from_address or "Platform" }}<br/>Date: {{ timestamp }}</div>
    <div style="margin-top:14px">{{ memo }}</div>

    <div class="footer">Transaction ref: {{ tx_ref }} &nbsp; • &nbsp; View on LedgerLocket</div>
  </div>
</body>
</html>
"""

@bp.route('/transactions/<tx_ref>/screenshot.png')
def transaction_screenshot(tx_ref):
    tx = Transaction.query.filter_by(tx_ref=tx_ref).first()
    if not tx:
        return abort(404)

    html = Template(RECEIPT_HTML_TEMPLATE).render(
        amount=str(tx.amount),
        to_address=tx.to_addr,
        from_address=tx.from_addr,
        timestamp=tx.created_at.strftime('%Y-%m-%d %H:%M:%S UTC'),
        memo=(tx.data or {}).get('memo',''),
        tx_ref=tx.tx_ref
    )

    # Run Playwright to render PNG
    with sync_playwright() as p:
        browser = p.chromium.launch(args=['--no-sandbox'])
        page = browser.new_page(viewport={'width':900,'height':600})
        page.set_content(html, wait_until='networkidle')
        png = page.screenshot(full_page=True)
        browser.close()

    return send_file(BytesIO(png), mimetype='image/png', download_name=f'receipt_{tx_ref}.png')
