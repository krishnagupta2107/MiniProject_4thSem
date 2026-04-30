"""
models/job.py
Firestore data model for Job Descriptions.

Each JobDescription document stores the raw JD text, extracted required skills
(as a comma-separated string), experience requirements, and metadata.
"""

import uuid
from datetime import datetime, timezone

def _gen_uuid() -> str:
    """Generate a new unique identifier for Firestore document IDs."""
    return str(uuid.uuid4())

class JobDescription:
    """
    Represents a job posting with required skills and metadata.

    Attributes:
        jd_id (str):           Unique Firestore document ID.
        user_id (str):         ID of the recruiter who created the posting.
        title (str):           Job title (e.g. 'Senior Backend Developer').
        company (str|None):    Company name.
        location (str|None):   Job location or 'Remote'.
        raw_text (str):        The full job description text as pasted by the user.
        required_skills (str): Comma-separated extracted skill names.
        experience_req (str):  Human-readable experience requirement (e.g. '3+ yrs').
        created_at (datetime): UTC timestamp of when the JD was saved.
    """
    def __init__(self, jd_id=None, user_id="", title="", company=None, location=None,
                 raw_text="", required_skills=None, experience_req=None, created_at=None):
        self.jd_id = jd_id or _gen_uuid()
        self.user_id = user_id
        self.title = title
        self.company = company
        self.location = location
        self.raw_text = raw_text
        self.required_skills = required_skills
        self.experience_req = experience_req
        if created_at is None:
            self.created_at = datetime.now(timezone.utc)
        elif isinstance(created_at, str):
            self.created_at = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
        else:
            self.created_at = created_at

    def skills_list(self) -> list:
        """Return the required_skills CSV string as a cleaned Python list."""
        if self.required_skills:
            return [s.strip() for s in self.required_skills.split(",") if s.strip()]
        return []
    
    def to_dict(self) -> dict:
        """Serialize the JobDescription to a Firestore-compatible dictionary."""
        return {
            "jd_id": self.jd_id,
            "user_id": self.user_id,
            "title": self.title,
            "company": self.company,
            "location": self.location,
            "raw_text": self.raw_text,
            "required_skills": self.required_skills,
            "experience_req": self.experience_req,
            "created_at": self.created_at.isoformat() if hasattr(self.created_at, "isoformat") else self.created_at
        }

    @staticmethod
    def from_dict(data: dict) -> "JobDescription":
        """Deserialize a Firestore document dict into a JobDescription instance."""
        return JobDescription(
            jd_id=data.get("jd_id"),
            user_id=data.get("user_id", ""),
            title=data.get("title", ""),
            company=data.get("company"),
            location=data.get("location"),
            raw_text=data.get("raw_text", ""),
            required_skills=data.get("required_skills"),
            experience_req=data.get("experience_req"),
            created_at=data.get("created_at")
        )

    def save(self):
        """Persist this JobDescription document to Firestore (upsert by jd_id)."""
        from app import db
        db.collection("job_descriptions").document(self.jd_id).set(self.to_dict())

    def delete(self):
        """Permanently delete this JobDescription from Firestore."""
        from app import db
        db.collection("job_descriptions").document(self.jd_id).delete()

    @staticmethod
    def get(jd_id: str) -> "JobDescription | None":
        """Fetch a single JobDescription by its document ID. Returns None if not found."""
        from app import db
        doc = db.collection("job_descriptions").document(jd_id).get()
        if doc.exists:
            return JobDescription.from_dict(doc.to_dict())
        return None

    @staticmethod
    def query_by_user(user_id: str) -> list:
        """Return all JobDescriptions created by the given user, sorted newest first."""
        from app import db
        docs = db.collection("job_descriptions").where("user_id", "==", user_id).stream()
        jds = [JobDescription.from_dict(doc.to_dict()) for doc in docs]
        jds.sort(key=lambda x: x.created_at, reverse=True)
        return jds

    @staticmethod
    def get_all() -> list:
        """Return all JobDescription documents in Firestore (admin use only)."""
        from app import db
        docs = db.collection("job_descriptions").stream()
        return [JobDescription.from_dict(doc.to_dict()) for doc in docs]
        
    def __repr__(self):
        return f"<JD {self.title}>"
