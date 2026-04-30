"""
helpers.py
Shared utility decorators and functions used across Flask routes.

Includes:
- rate_limit: Per-IP request throttling decorator
- admin_required: RBAC decorator restricting access to admin users
"""

from functools import wraps
from time import time

from flask import request, flash, redirect, url_for, jsonify
from flask_login import current_user


# In-memory rate limit store: { "bucket:ip": [timestamp, ...] }
_rate_store: dict = {}


def rate_limit(bucket: str, limit: int = 10, window: int = 60):
    """
    Decorator factory that enforces a per-IP request rate limit.

    Args:
        bucket (str): Unique name for this rate limit category (e.g. 'upload_resume').
        limit  (int): Maximum number of requests allowed within the time window.
        window (int): Rolling time window in seconds (default: 60s).

    Returns:
        Flask response with HTTP 429 (JSON) or a flashed warning redirect
        if the limit is exceeded; otherwise executes the wrapped route function.

    Example:
        @rate_limit("upload_resume", limit=5, window=60)
        def upload_resume():
            ...
    """
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            ip  = request.remote_addr or "anon"
            key = f"{bucket}:{ip}"
            now = time()

            # Keep only hits within the current window
            hits = [t for t in _rate_store.get(key, []) if now - t < window]
            if len(hits) >= limit:
                if request.is_json:
                    return jsonify({"error": "too many requests"}), 429
                flash("Too many requests, slow down a bit!", "warning")
                return redirect(request.referrer or url_for("main.index"))

            hits.append(now)
            _rate_store[key] = hits
            return fn(*args, **kwargs)
        return wrapper
    return decorator


def admin_required(fn):
    """
    Route decorator that restricts access to authenticated admin users only.

    Redirects non-admin or unauthenticated users to the dashboard with an error flash.
    Must be placed after @login_required in the decorator chain.

    Example:
        @admin_bp.route("/admin")
        @login_required
        @admin_required
        def admin_dashboard():
            ...
    """
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin():
            flash("Admin access only.", "danger")
            return redirect(url_for("main.dashboard"))
        return fn(*args, **kwargs)
    return wrapper
