import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "change-this-in-production-please")
    
    
    
    # file uploads
    UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
    MAX_CONTENT_LENGTH = 10 * 1024 * 1024   # 10 MB
    ALLOWED_EXTENSIONS = {"pdf", "doc", "docx", "txt"}
    
    # wtf forms (csrf protection)
    WTF_CSRF_ENABLED = True
    
    # server
    PORT  = int(os.environ.get("PORT", 5000))
    DEBUG = os.environ.get("FLASK_ENV", "development") == "development"

    # security configurations
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    # SESSION_COOKIE_SECURE = True  # Enable this in production with HTTPS
    CORS_HEADERS = 'Content-Type'

    # email (optional, won't crash if not set)
    MAIL_SERVER   = os.environ.get("MAIL_SERVER", "")
    MAIL_PORT     = int(os.environ.get("MAIL_PORT", 587))
    MAIL_USE_TLS  = os.environ.get("MAIL_USE_TLS", "true").lower() == "true"
    MAIL_USERNAME = os.environ.get("MAIL_USERNAME", "")
    MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD", "")


class TestConfig(Config):
    TESTING = True
    WTF_CSRF_ENABLED = False   # makes testing forms easier
    SECRET_KEY = "test-secret"
