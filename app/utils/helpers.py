"""
helpers.py
Small utility functions used across routes.
"""

from functools import wraps
from time import time

from flask import request, flash, redirect, url_for, jsonify
from flask_login import current_user


# sasta rate limiter
# prod mein kon hi use karega ye lol

_rate_store: dict = {}


def rate_limit(bucket: str, limit: int = 10, window: int = 60):
    """Decorator that limits requests per IP."""
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            ip  = request.remote_addr or "anon"
            key = f"{bucket}:{ip}"
            now = time()

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


# admin roko

def admin_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin():
            flash("Admin access only.", "danger")
            return redirect(url_for("main.dashboard"))
        return fn(*args, **kwargs)
    return wrapper
