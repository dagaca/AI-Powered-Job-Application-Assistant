"""
Handles API Key authentication for API security.
"""

import os
from flask import request, jsonify
from functools import wraps
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
API_KEY = os.getenv("API_KEY")

def api_key_required(f):
    """
    Decorator to enforce API Key authentication on secured endpoints.

    Usage:
        - Apply `@api_key_required` to Flask routes that require authentication.
        - The client must include the `X-API-KEY` header in requests.

    Returns:
        - 401 Unauthorized if API Key is missing or invalid.
        - The wrapped function if authentication is successful.
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        api_key = request.headers.get("X-API-KEY")

        if not api_key:
            return jsonify({"error": "Missing API Key"}), 401

        if api_key != API_KEY:
            return jsonify({"error": "Invalid API Key"}), 401

        return f(*args, **kwargs)

    return decorated
