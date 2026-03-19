"""
routes/auth.py
Login, register, logout routes.
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from flask import current_app
from itsdangerous import URLSafeTimedSerializer

from app.models.user import User

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))

    if request.method == "POST":
        email    = request.form.get("email", "").strip().lower()
        name     = request.form.get("full_name", "").strip()
        password = request.form.get("password", "")
        confirm  = request.form.get("confirm_password", "")

        # basic validation
        error = None
        if not email or not name or not password:
            error = "All fields are required."
        elif "@" not in email or "." not in email.split("@")[-1]:
            error = "Please enter a valid email address."
        elif len(password) < 6:
            error = "Password must be at least 6 characters."
        elif password != confirm:
            error = "Passwords do not match."
        elif User.query_by_email(email):
            error = "That email is already registered."

        if error:
            flash(error, "danger")
        else:
            user = User(email=email, full_name=name)
            user.set_password(password)
            user.save()
            flash("Account created! You can now log in.", "success")
            return redirect(url_for("auth.login"))

    return render_template("auth/register.html")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))

    if request.method == "POST":
        email    = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        user     = User.query_by_email(email)

        if user and user.check_password(password):
            login_user(user)
            flash(f"Welcome back, {user.full_name}!", "success")
            next_page = request.args.get("next")
            return redirect(next_page or url_for("main.dashboard"))

        flash("Incorrect email or password.", "danger")

    return render_template("auth/login.html")


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("main.index"))


def get_reset_token(user_id):
    s = URLSafeTimedSerializer(current_app.config["SECRET_KEY"])
    return s.dumps({"user_id": user_id})

def verify_reset_token(token, expires_sec=1800):
    s = URLSafeTimedSerializer(current_app.config["SECRET_KEY"])
    try:
        user_id = s.loads(token, max_age=expires_sec)["user_id"]
    except:
        return None
    return User.get(user_id)

@auth_bp.route("/reset-password", methods=["GET", "POST"])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        user = User.query_by_email(email)
        if user:
            token = get_reset_token(user.user_id)
            reset_url = url_for("auth.reset_token", token=token, _external=True)
            # Mock email sending by flashing the link
            flash(f"Mock Email Sent! Reset Link: {reset_url}", "info")
        else:
            flash("If an account exists for that email, a reset link has been sent.", "info")
        return redirect(url_for("auth.login"))
    return render_template("auth/reset_request.html")

@auth_bp.route("/reset-password/<token>", methods=["GET", "POST"])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))
    user = verify_reset_token(token)
    if user is None:
        flash("That is an invalid or expired token.", "warning")
        return redirect(url_for("auth.reset_request"))
    if request.method == "POST":
        password = request.form.get("password", "")
        if password:
            user.set_password(password)
            user.save()
            flash("Your password has been updated! You are now able to log in.", "success")
            return redirect(url_for("auth.login"))
        else:
            flash("Password cannot be empty.", "danger")
    return render_template("auth/reset_password.html", token=token)

@auth_bp.route("/google", methods=["POST"])
def google_auth():
    from firebase_admin import auth as fb_auth
    import secrets

    data = request.get_json()
    token = data.get("token")
    if not token:
        return {"success": False, "error": "No token provided"}, 400

    try:
        decoded_token = fb_auth.verify_id_token(token)
        email = decoded_token.get("email")
        name = decoded_token.get("name", "Google User")

        if not email:
            return {"success": False, "error": "No email included in Google payload"}, 400

        user = User.query_by_email(email)
        if not user:
            # Create user on the fly since they authenticated via Google
            user = User(email=email, full_name=name)
            user.set_password(secrets.token_urlsafe(32))
            user.save()

        login_user(user)
        return {"success": True, "redirect": url_for("main.dashboard")}

    except Exception as e:
        return {"success": False, "error": str(e)}, 401
