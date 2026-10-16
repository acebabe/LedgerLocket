"""Flask API key permission decorator for LedgerLocket

Security-minded implementation notes:
- API keys are loaded from an environment variable (API_KEYS_JSON) or from a
  JSON file path (API_KEYS_FILE). This avoids committing keys in source.
- Stored keys should be treated as secrets. In production store them hashed in
  a database and compare hashes with constant-time checks.
- This example uses hmac.compare_digest for constant-time comparison and
  places key metadata in flask.g (not on the request object).

Environment options:
- API_KEYS_JSON: JSON string like '{"token_xxx": {"permissions": [...], ...}}'
- API_KEYS_FILE: path to a JSON file with the same structure

If neither is provided, the middleware will reject all requests (safe default).

Do NOT commit real API keys. Use a secret manager or DB in production.
"""

import os
import json
import hmac
from functools import wraps
from flask import request, jsonify, g


def _load_api_keys():
    """Load API keys from environment or file.

    Returns a dict mapping raw_api_key -> metadata.
    """
    data = None
    json_str = os.environ.get("API_KEYS_JSON")
    file_path = os.environ.get("API_KEYS_FILE")

    if json_str:
        try:
            data = json.loads(json_str)
        except json.JSONDecodeError:
            raise RuntimeError("API_KEYS_JSON is not valid JSON")
    elif file_path:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception as e:
            raise RuntimeError(f"Failed to load API_KEYS_FILE: {e}")

    if not isinstance(data, dict):
        return {}

    return data


# Load keys at import time. In long-running processes you may prefer a
# refreshable/cacheable approach or a DB-backed lookup.
API_KEYS = _load_api_keys()


def _find_key_data(provided_key: str):
    """Find key metadata using constant-time comparison.

    Returns the metadata dict if found, otherwise None.
    """
    for stored_key, meta in API_KEYS.items():
        try:
            if hmac.compare_digest(provided_key, stored_key):
                return meta
        except Exception:
            # In case of unexpected types, skip this key
            continue
    return None


def require_permission(required_permission: str):
    """Decorator to require an API key and the given permission.

    Sets flask.g.api_key_data to the key metadata on success.
    """

    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            auth_header = request.headers.get("Authorization") or request.headers.get("authorization")
            if not auth_header:
                return jsonify({"error": "API key required"}), 401

            parts = auth_header.split()
            if len(parts) != 2 or parts[0].lower() != "bearer":
                return jsonify({"error": "Malformed Authorization header. Use: Bearer <API_KEY>"}), 401

            api_key = parts[1]

            key_data = _find_key_data(api_key)
            if not key_data:
                return jsonify({"error": "Invalid API key"}), 401

            permissions = key_data.get("permissions", [])
            has_permission = ("*:*" in permissions) or (required_permission in permissions)

            if not has_permission:
                return jsonify({
                    "error": "Insufficient permissions",
                    "required": required_permission,
                    "granted": permissions,
                }), 403

            # Attach metadata to flask.g rather than request
            g.api_key_data = key_data
            return f(*args, **kwargs)

        return decorated_function

    return decorator


# Usage example (Flask):
# from flask import Flask
# app = Flask(__name__)
#
# @app.route('/users')
# @require_permission('users:read')
# def get_users():
#     return jsonify({'users': []})
#
# @app.route('/users', methods=['POST'])
# @require_permission('users:write')
# def create_user():
#     return jsonify({'message': 'User created'})
