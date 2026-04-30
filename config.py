"""
config.py
Application configuration classes for Flask.

Config:     Used for development and production.
TestConfig: Used by pytest with CSRF disabled and a fixed secret key.
"""

import os
from dotenv import load_dotenv

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"))


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "change-this-in-production-please")
    
    
    
    # File upload settings
    UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024   # 5 MB Strict Limit
    ALLOWED_EXTENSIONS = {"pdf", "docx", "txt"}
    
    # wtf forms (csrf protection)
    WTF_CSRF_ENABLED = True
    
    # server
    PORT  = int(os.environ.get("PORT", 5000))
    DEBUG = os.environ.get("FLASK_ENV", "development") == "development"

    # Firebase integration mapping
    # Note: Using dotenv internally
    FIREBASE_API_KEY = os.environ.get("FIREBASE_API_KEY", "")
    FIREBASE_AUTH_DOMAIN = os.environ.get("FIREBASE_AUTH_DOMAIN", "resume-matcher-e022f.firebaseapp.com")
    FIREBASE_PROJECT_ID = os.environ.get("FIREBASE_PROJECT_ID", "resume-matcher-e022f")
    FIREBASE_STORAGE_BUCKET = os.environ.get("FIREBASE_STORAGE_BUCKET", "resume-matcher-e022f.firebasestorage.app")
    FIREBASE_MESSAGING_SENDER_ID = os.environ.get("FIREBASE_MESSAGING_SENDER_ID", "338795102474")
    FIREBASE_APP_ID = os.environ.get("FIREBASE_APP_ID", "1:338795102474:web:83979f5dbdad2942f9faf3")
    FIREBASE_MEASUREMENT_ID = os.environ.get("FIREBASE_MEASUREMENT_ID", "G-S53PY3YNVR")
    GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")

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
