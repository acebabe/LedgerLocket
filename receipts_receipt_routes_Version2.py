from flask import Blueprint, send_file, abort
from models import Transaction
from jinja2 import Template
from playwright.sync_api import sync_playwright
from io import BytesIO

bp = Blueprint("receipts", __name__)

RECEIPT_HTML_TEMPLATE = """
<!doctype html>
<html>
<head><meta charset="utf-8"/>
<style>
  body { font-family: Arial, sans-serif; background:#f7fafc; padding:24px; }
  .card { width:720px; margin:0 auto; background:#fff; padding:24px; border-radius:10px; }
  .brand { font-weight:700; color:#0f172a; }
  .amount { font-size:28px; font-weight:700; margin-top:12px; }
  .meta { color:#64748b; margin-top:8px; font-size:13px; }
  .badge { display:inline-block; padding:6px 8px; background:#f1f5f9; border-radius:8px; }
</style></head>
<body>
  <div class="card">
    <div class="brand">LedgerLocket</div>
    <div class="badge">Non-withdrawable</div>
    <h1>Credit received</h1>
    <div class="amount">{{ amount }} LCK</div>
    <div class="meta">To: {{ to_address }}<br/>From: {{ from_address or "Platform" }}<br/>Date: {{ timestamp }}</div>
    <div style="margin-top:14px">{{ memo }}</div>
    <div style="margin-top:18px;color:#94a3b8;font-size:12px">Transaction ref: {{ tx_ref }}</div>
  </div>
</body>
</html>
"""

@bp.route("/transactions/<tx_ref>/screenshot.png")
def transaction_screenshot(tx_ref):
    tx = Transaction.query.filter_by(tx_ref=tx_ref).first()
    if not tx:
        return abort(404)
    html = Template(RECEIPT_HTML_TEMPLATE).render(
        amount=str(tx.amount),
        to_address=tx.to_address,
        from_address=tx.from_address,
        timestamp=tx.created_at.strftime("%Y-%m-%d %H:%M:%S UTC"),
        memo=tx.data.get("memo",""),
        tx_ref=tx.tx_ref
    )
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=["--no-sandbox"])
        page = browser.new_page(viewport={"width":900,"height":600})
        page.set_content(html, wait_until="networkidle")
        png = page.screenshot(full_page=True)
        browser.close()
    return send_file(BytesIO(png), mimetype="image/png", download_name=f"receipt_{tx_ref}.png")