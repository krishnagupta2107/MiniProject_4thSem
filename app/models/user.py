import uuid
from datetime import datetime, timezone
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

def _gen_uuid():
    return str(uuid.uuid4())

class User(UserMixin):
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

    def get_id(self):
        return self.user_id

    def set_password(self, raw_password: str):
        self.password = generate_password_hash(raw_password)

    def check_password(self, raw_password: str) -> bool:
        return check_password_hash(self.password, raw_password)

    def is_admin(self) -> bool:
        return self.role == "admin"

    def to_dict(self):
        return {
            "user_id": self.user_id,
            "email": self.email,
            "password": self.password,
            "full_name": self.full_name,
            "role": self.role,
            "created_at": self.created_at.isoformat() if hasattr(self.created_at, "isoformat") else self.created_at
        }

    @staticmethod
    def from_dict(data):
        return User(
            user_id=data.get("user_id"),
            email=data.get("email", ""),
            password=data.get("password", ""),
            full_name=data.get("full_name", ""),
            role=data.get("role", "recruiter"),
            created_at=data.get("created_at")
        )

    def save(self):
        from app import db
        db.collection("users").document(self.user_id).set(self.to_dict())

    def delete(self):
        from app import db
        db.collection("users").document(self.user_id).delete()

    @staticmethod
    def query_by_email(email):
        from app import db
        docs = db.collection("users").where("email", "==", email).limit(1).stream()
        for doc in docs:
            return User.from_dict(doc.to_dict())
        return None

    @staticmethod
    def get(user_id):
        from app import db
        doc = db.collection("users").document(user_id).get()
        if doc.exists:
            return User.from_dict(doc.to_dict())
        return None

    @staticmethod
    def get_all():
        from app import db
        docs = db.collection("users").stream()
        return [User.from_dict(doc.to_dict()) for doc in docs]

    def __repr__(self):
        return f"<User {self.email}>"

from app import login_manager

@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)
