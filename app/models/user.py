"""
models/user.py
Firestore data model for user accounts.

Handles password hashing, Flask-Login integration, and role-based access.
All user data is stored in the 'users' Firestore collection.
"""

import uuid
from datetime import datetime, timezone
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

def _gen_uuid():
    return str(uuid.uuid4())

class User(UserMixin):
    """
    Represents an authenticated user of the HireMatch platform.

    Attributes:
        user_id (str):     Unique Firestore document ID (also Flask-Login user_id).
        email (str):       User's email address (unique identifier for login).
        password (str):    Werkzeug-hashed password string. Never stored in plaintext.
        full_name (str):   Display name of the user.
        role (str):        Access role — 'recruiter' (default) or 'admin'.
        created_at (datetime): UTC timestamp when the account was created.
    """
    def __init__(self, user_id=None, email="", password="", full_name="", role="recruiter", created_at=None):
        self.user_id = user_id or _gen_uuid()
        self.email = email
        self.password = password
        self.full_name = full_name
        self.role = role
        if created_at is None:
            self.created_at = datetime.now(timezone.utc)
        elif isinstance(created_at, str):
            self.created_at = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
        else:
            self.created_at = created_at

    def get_id(self) -> str:
        """Return the user's unique ID — required by Flask-Login."""
        return self.user_id

    def set_password(self, raw_password: str) -> None:
        """Hash and store a plaintext password using Werkzeug's PBKDF2 hasher."""
        self.password = generate_password_hash(raw_password)

    def check_password(self, raw_password: str) -> bool:
        """Verify a plaintext password against the stored hash. Returns True on match."""
        return check_password_hash(self.password, raw_password)

    def is_admin(self) -> bool:
        """Return True if this user has the 'admin' role."""
        return self.role == "admin"

    def to_dict(self) -> dict:
        """Serialize the User to a Firestore-compatible dictionary."""
        return {
            "user_id": self.user_id,
            "email": self.email,
            "password": self.password,
            "full_name": self.full_name,
            "role": self.role,
            "created_at": self.created_at.isoformat() if hasattr(self.created_at, "isoformat") else self.created_at
        }

    @staticmethod
    def from_dict(data: dict) -> "User":
        """Deserialize a Firestore document dict into a User instance."""
        return User(
            user_id=data.get("user_id"),
            email=data.get("email", ""),
            password=data.get("password", ""),
            full_name=data.get("full_name", ""),
            role=data.get("role", "recruiter"),
            created_at=data.get("created_at")
        )

    def save(self) -> None:
        """Persist this User document to Firestore (upsert by user_id)."""
        from app import db
        db.collection("users").document(self.user_id).set(self.to_dict())

    def delete(self) -> None:
        """Permanently delete this User from Firestore."""
        from app import db
        db.collection("users").document(self.user_id).delete()

    @staticmethod
    def query_by_email(email: str) -> "User | None":
        """Look up a user by their email address. Returns None if not found."""
        from app import db
        docs = db.collection("users").where("email", "==", email).limit(1).stream()
        for doc in docs:
            return User.from_dict(doc.to_dict())
        return None

    @staticmethod
    def get(user_id: str) -> "User | None":
        """Fetch a single User by Firestore document ID. Returns None if not found."""
        from app import db
        doc = db.collection("users").document(user_id).get()
        if doc.exists:
            return User.from_dict(doc.to_dict())
        return None

    @staticmethod
    def get_all() -> list:
        """Return all User documents in Firestore (admin use only)."""
        from app import db
        docs = db.collection("users").stream()
        return [User.from_dict(doc.to_dict()) for doc in docs]

    def __repr__(self):
        return f"<User {self.email}>"

from app import login_manager

@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)
