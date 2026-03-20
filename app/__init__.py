import os
from flask import Flask
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from flask_cors import CORS

import firebase_admin
from firebase_admin import credentials, firestore

from config import Config

# baaki sab load karte hai
db = None
login_manager = LoginManager()
csrf = CSRFProtect()


def create_app(config_class=Config):
    app = Flask(__name__, template_folder="../templates", static_folder="../static")
    app.config.from_object(config_class)

    # folder bana lo warna path error aayega
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
    os.makedirs(os.path.join(os.path.dirname(__file__), "..", "instance"), exist_ok=True)

    global db
    if not firebase_admin._apps:
        # production key check krlo
        firebase_json_str = os.environ.get("FIREBASE_JSON")
        if firebase_json_str:
            import json
            cred_dict = json.loads(firebase_json_str)
            cred = credentials.Certificate(cred_dict)
        else:
            # local key try maro
            cred = credentials.Certificate(os.path.join(os.path.dirname(__file__), "..", "resume-checker-key.json"))
        firebase_admin.initialize_app(cred)
    db = firestore.client()

    # extension chalu
    csrf.init_app(app)
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    login_manager.init_app(app)
    login_manager.login_view = "auth.login"
    login_manager.login_message = "Please log in first."
    login_manager.login_message_category = "warning"

    # blueprints dalo
    from app.routes.auth    import auth_bp
    from app.routes.main    import main_bp
    from app.routes.resume  import resume_bp
    from app.routes.job     import job_bp
    from app.routes.match   import match_bp
    from app.routes.admin   import admin_bp
    from app.routes.api     import api_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(resume_bp)
    app.register_blueprint(job_bp)
    app.register_blueprint(match_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(api_bp, url_prefix="/api")

    with app.app_context():
        _seed_demo_accounts()

    @app.after_request
    def add_security_headers(response):
        response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'SAMEORIGIN'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        # csp policy cdn allow karne ke liye
        csp = (
    "default-src 'self'; "
    "connect-src 'self' https://*.firebaseio.com wss://*.firebaseio.com "
        "https://*.googleapis.com https://*.google-analytics.com "
        "https://identitytoolkit.googleapis.com "
        "https://securetoken.googleapis.com; "
    "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com https://fonts.googleapis.com; "
    "script-src 'self' 'unsafe-inline' "
        "https://cdn.jsdelivr.net https://cdnjs.cloudflare.com "
        "https://www.gstatic.com https://*.googleapis.com "
        "https://apis.google.com https://*.google.com "
        "https://*.firebaseapp.com https://www.googletagmanager.com; "
    "frame-src 'self' "
        "https://*.firebaseapp.com "
        "https://accounts.google.com "
        "https://resume-matcher-e022f.firebaseapp.com; "
    "font-src 'self' https://cdnjs.cloudflare.com https://fonts.gstatic.com; "
    "img-src 'self' data: https://*.googleusercontent.com;"
)
        response.headers['Content-Security-Policy'] = csp
        return response

    return app


def _seed_demo_accounts():
    """Create demo recruiter and admin accounts if they don't exist yet in Firestore."""
    from app.models.user import User

    users_ref = db.collection('users')
    
    if not list(users_ref.where('email', '==', 'recruiter@demo.com').limit(1).stream()):
        u = User(email="recruiter@demo.com", full_name="Demo Recruiter")
        u.set_password("demo123")
        users_ref.document(u.user_id).set(u.to_dict())

    if not list(users_ref.where('email', '==', 'admin@demo.com').limit(1).stream()):
        u = User(email="admin@demo.com", full_name="Demo Admin", role="admin")
        u.set_password("admin123")
        users_ref.document(u.user_id).set(u.to_dict())
