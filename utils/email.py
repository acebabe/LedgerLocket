from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

import os


def send_verification_email(to_email: str, token: str):
    api_key = os.getenv("SENDGRID_API_KEY")
    if not api_key:
        print(f"[email] verification link: {os.getenv('APP_URL', 'http://localhost:3000')}/verify?token={token}")
        return True
    message = Mail(
        from_email=os.getenv("FROM_EMAIL", "no-reply@ledgerlocket.local"),
        to_emails=to_email,
        subject="Verify your LedgerLocket account",
        html_content=f"<p>Verify your account: <a href='{os.getenv('APP_URL', 'http://localhost:3000')}/verify?token={token}'>Click here</a></p>",
    )
    try:
        sg = SendGridAPIClient(api_key)
        sg.send(message)
        return True
    except Exception:
        return False


def send_password_reset_email(to_email: str, token: str):
    api_key = os.getenv("SENDGRID_API_KEY")
    if not api_key:
        print(f"[email] reset link: {os.getenv('APP_URL', 'http://localhost:3000')}/reset-password?token={token}")
        return True
    message = Mail(
        from_email=os.getenv("FROM_EMAIL", "no-reply@ledgerlocket.local"),
        to_emails=to_email,
        subject="Reset your LedgerLocket password",
        html_content=f"<p>Reset your password: <a href='{os.getenv('APP_URL', 'http://localhost:3000')}/reset-password?token={token}'>Click here</a></p>",
    )
    try:
        sg = SendGridAPIClient(api_key)
        sg.send(message)
        return True
    except Exception:
        return False
