"""Example Flask OAuth integration for LedgerLocket

WARNING: This file is an example. DO NOT commit real client secrets or production session keys.
Set the following environment variables before running:
- FLASK_SECRET_KEY
- OAUTH_CLIENT_ID
- OAUTH_CLIENT_SECRET
- OAUTH_AUTH_URL
- OAUTH_TOKEN_URL
- OAUTH_REDIRECT_URI
- OAUTH_SCOPE

This example uses the "authorization code" flow and shows basic token exchange
and refresh logic. Integrate and harden for production: validate tokens, store
refresh tokens securely, use HTTPS, set cookie flags (Secure, HttpOnly, SameSite),
and add error handling and logging.
"""

from flask import Flask, request, session, redirect, url_for
import requests
import secrets
import os
from urllib.parse import urlencode

app = Flask(__name__)
# Use an environment-provided secret key in production. Falling back to a
# generated key only for local testing.
app.secret_key = os.environ.get('FLASK_SECRET_KEY') or secrets.token_urlsafe(32)

# OAuth configuration - pull from environment variables. Do NOT commit secrets.
OAUTH_CONFIG = {
    'client_id': os.environ.get('OAUTH_CLIENT_ID', 'client_123456'),
    'client_secret': os.environ.get('OAUTH_CLIENT_SECRET', 'changeme'),
    'auth_url': os.environ.get('OAUTH_AUTH_URL', 'https://oauth.provider.com/authorize'),
    'token_url': os.environ.get('OAUTH_TOKEN_URL', 'https://oauth.provider.com/token'),
    'redirect_uri': os.environ.get('OAUTH_REDIRECT_URI', 'https://example.com/callback'),
    'scope': os.environ.get('OAUTH_SCOPE', 'read:profile read:email')
}


@app.route('/login')
def login():
    # Generate state for CSRF protection
    state = secrets.token_urlsafe(32)
    session['oauth_state'] = state

    # Build authorization URL
    params = {
        'response_type': 'code',
        'client_id': OAUTH_CONFIG['client_id'],
        'redirect_uri': OAUTH_CONFIG['redirect_uri'],
        'scope': OAUTH_CONFIG['scope'],
        'state': state
    }

    auth_url = f"{OAUTH_CONFIG['auth_url']}?{urlencode(params)}"
    return redirect(auth_url)


@app.route('/callback')
def callback():
    # Verify state parameter
    if request.args.get('state') != session.get('oauth_state'):
        return 'Invalid state parameter', 400

    # Get authorization code
    auth_code = request.args.get('code')
    if not auth_code:
        return 'Missing authorization code', 400

    # Exchange code for tokens
    token_data = {
        'grant_type': 'authorization_code',
        'code': auth_code,
        'client_id': OAUTH_CONFIG['client_id'],
        'client_secret': OAUTH_CONFIG['client_secret'],
        'redirect_uri': OAUTH_CONFIG['redirect_uri']
    }

    response = requests.post(OAUTH_CONFIG['token_url'], data=token_data)

    if response.status_code == 200:
        tokens = response.json()
        session['access_token'] = tokens.get('access_token')
        session['refresh_token'] = tokens.get('refresh_token')
        return redirect(url_for('profile'))
    else:
        return 'Token exchange failed', 400


@app.route('/profile')
def profile():
    access_token = session.get('access_token')
    if not access_token:
        return redirect(url_for('login'))

    # Make API request with access token
    headers = {'Authorization': f"Bearer {access_token}"}
    response = requests.get('https://api.provider.com/user/profile', headers=headers)

    if response.status_code == 200:
        user_data = response.json()
        return f"Welcome, {user_data.get('name', 'User')}!"
    else:
        # Token might be expired, try refresh
        return refresh_and_retry()


def refresh_and_retry():
    refresh_token = session.get('refresh_token')
    if not refresh_token:
        return redirect(url_for('login'))

    # Refresh access token
    token_data = {
        'grant_type': 'refresh_token',
        'refresh_token': refresh_token,
        'client_id': OAUTH_CONFIG['client_id'],
        'client_secret': OAUTH_CONFIG['client_secret']
    }

    response = requests.post(OAUTH_CONFIG['token_url'], data=token_data)

    if response.status_code == 200:
        tokens = response.json()
        session['access_token'] = tokens.get('access_token')
        # Optionally update stored refresh token if rotated
        if tokens.get('refresh_token'):
            session['refresh_token'] = tokens.get('refresh_token')
        return redirect(url_for('profile'))
    else:
        return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(debug=True)
