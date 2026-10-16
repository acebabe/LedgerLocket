"""Example Flask OAuth integration for LedgerLocket.

This file is a template only. It intentionally fails fast when required
configuration is missing instead of using hard-coded, production-like secrets.

Required environment variables:
- FLASK_SECRET_KEY
- OAUTH_CLIENT_ID
- OAUTH_CLIENT_SECRET
- OAUTH_AUTH_URL
- OAUTH_TOKEN_URL
- OAUTH_REDIRECT_URI
- OAUTH_SCOPE

Production notes:
- Use HTTPS-only cookies and set Secure/HttpOnly/SameSite appropriately.
- Store refresh tokens server-side and rotate them safely.
- Validate ID token or profile responses before trusting user identity.
"""

import os
import secrets
from urllib.parse import urlencode

import requests
from flask import Flask, redirect, request, session, url_for


app = Flask(__name__)

if not os.environ.get("FLASK_SECRET_KEY"):
    raise RuntimeError("FLASK_SECRET_KEY must be set before starting the app")

app.config["SECRET_KEY"] = os.environ["FLASK_SECRET_KEY"]
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
app.config["SESSION_COOKIE_SECURE"] = True


def get_oauth_config():
    required = [
        "OAUTH_CLIENT_ID",
        "OAUTH_CLIENT_SECRET",
        "OAUTH_AUTH_URL",
        "OAUTH_TOKEN_URL",
        "OAUTH_REDIRECT_URI",
        "OAUTH_SCOPE",
    ]
    missing = [name for name in required if not os.environ.get(name)]
    if missing:
        raise RuntimeError(
            "Missing OAuth configuration: " + ", ".join(missing)
        )

    return {
        "client_id": os.environ["OAUTH_CLIENT_ID"],
        "client_secret": os.environ["OAUTH_CLIENT_SECRET"],
        "auth_url": os.environ["OAUTH_AUTH_URL"],
        "token_url": os.environ["OAUTH_TOKEN_URL"],
        "redirect_uri": os.environ["OAUTH_REDIRECT_URI"],
        "scope": os.environ["OAUTH_SCOPE"],
    }


OAUTH_CONFIG = get_oauth_config()


@app.route("/login")
def login():
    state = secrets.token_urlsafe(32)
    session["oauth_state"] = state

    params = {
        "response_type": "code",
        "client_id": OAUTH_CONFIG["client_id"],
        "redirect_uri": OAUTH_CONFIG["redirect_uri"],
        "scope": OAUTH_CONFIG["scope"],
        "state": state,
    }

    auth_url = f"{OAUTH_CONFIG['auth_url']}?{urlencode(params)}"
    return redirect(auth_url)


@app.route("/callback")
def callback():
    expected_state = session.get("oauth_state")
    received_state = request.args.get("state")
    if expected_state is None or received_state != expected_state:
        return "Invalid state parameter", 400

    auth_code = request.args.get("code")
    if not auth_code:
        return "Missing authorization code", 400

    token_data = {
        "grant_type": "authorization_code",
        "code": auth_code,
        "client_id": OAUTH_CONFIG["client_id"],
        "client_secret": OAUTH_CONFIG["client_secret"],
        "redirect_uri": OAUTH_CONFIG["redirect_uri"],
    }

    try:
        response = requests.post(OAUTH_CONFIG["token_url"], data=token_data, timeout=10)
        response.raise_for_status()
        tokens = response.json()
    except (requests.RequestException, ValueError):
        return "Token exchange failed", 400

    session["access_token"] = tokens.get("access_token")
    session["refresh_token"] = tokens.get("refresh_token")
    return redirect(url_for("profile"))


@app.route("/profile")
def profile():
    access_token = session.get("access_token")
    if not access_token:
        return redirect(url_for("login"))

    headers = {"Authorization": f"Bearer {access_token}"}
    try:
        response = requests.get("https://api.provider.com/user/profile", headers=headers, timeout=10)
        response.raise_for_status()
        user_data = response.json()
    except (requests.RequestException, ValueError):
        return refresh_and_retry()

    return f"Welcome, {user_data.get('name', 'User')}!"


def refresh_and_retry():
    refresh_token = session.get("refresh_token")
    if not refresh_token:
        return redirect(url_for("login"))

    token_data = {
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
        "client_id": OAUTH_CONFIG["client_id"],
        "client_secret": OAUTH_CONFIG["client_secret"],
    }

    try:
        response = requests.post(OAUTH_CONFIG["token_url"], data=token_data, timeout=10)
        response.raise_for_status()
        tokens = response.json()
    except (requests.RequestException, ValueError):
        return redirect(url_for("login"))

    session["access_token"] = tokens.get("access_token")
    if tokens.get("refresh_token"):
        session["refresh_token"] = tokens.get("refresh_token")
    return redirect(url_for("profile"))


if __name__ == "__main__":
    app.run(debug=True)
