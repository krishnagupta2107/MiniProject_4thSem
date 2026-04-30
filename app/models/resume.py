"""
models/resume.py
Firestore data model for uploaded candidate resumes.

Stores parsed resume data including extracted skills, experience, education,
and candidate contact details. Each document belongs to one user account.
"""

import uuid
from datetime import datetime, timezone

def _gen_uuid():
    return str(uuid.uuid4())

class Resume:
    """
    Represents a parsed resume uploaded by a recruiter or candidate.

    Attributes:
        resume_id (str):          Unique Firestore document ID.
        user_id (str):            ID of the user who uploaded this resume.
        filename (str):           Original uploaded file name.
        file_path (str):          Server-side path where the file is stored.
        raw_text (str):           Full extracted plain text from the document.
        extracted_skills (str):   Comma-separated list of detected skills.
        experience_years (float): Total years of experience detected.
        education_level (str):    Highest qualification (e.g. 'Bachelors', 'Masters').
        candidate_name (str):     Detected candidate name from the resume.
        candidate_email (str):    Detected email address.
        candidate_phone (str):    Detected phone number.
        candidate_links (list):   Detected LinkedIn/GitHub profile URLs.
        candidate_companies (list): Detected company names from NER.
        uploaded_at (datetime):   UTC timestamp of upload.
    """
    def __init__(self, resume_id=None, user_id="", filename="", file_path="", raw_text=None,
                 extracted_skills=None, experience_years=0.0, education_level=None,
                 candidate_name=None, candidate_email=None, candidate_phone=None,
                 candidate_links=None, candidate_companies=None, uploaded_at=None):
        self.resume_id = resume_id or _gen_uuid()
        self.user_id = user_id
        self.filename = filename
        self.file_path = file_path or ""
        self.raw_text = raw_text
        self.extracted_skills = extracted_skills
        self.experience_years = experience_years
        self.education_level = education_level
        self.candidate_name = candidate_name
        self.candidate_email = candidate_email
        self.candidate_phone = candidate_phone
        self.candidate_links = candidate_links or []
        self.candidate_companies = candidate_companies or []
        if uploaded_at is None:
            self.uploaded_at = datetime.now(timezone.utc)
        elif isinstance(uploaded_at, str):
            self.uploaded_at = datetime.fromisoformat(uploaded_at.replace("Z", "+00:00"))
        else:
            self.uploaded_at = uploaded_at

    def skills_list(self) -> list:
        """Return the extracted_skills CSV string as a cleaned Python list."""
        if self.extracted_skills:
            return [s.strip() for s in self.extracted_skills.split(",") if s.strip()]
        return []

    def to_dict(self) -> dict:
        """Serialize the Resume to a Firestore-compatible dictionary."""
        return {
            "resume_id": self.resume_id,
            "user_id": self.user_id,
            "filename": self.filename,
            "file_path": self.file_path,
            "raw_text": self.raw_text,
            "extracted_skills": self.extracted_skills,
            "experience_years": self.experience_years,
            "education_level": self.education_level,
            "candidate_name": self.candidate_name,
            "candidate_email": self.candidate_email,
            "candidate_phone": self.candidate_phone,
            "candidate_links": self.candidate_links,
            "candidate_companies": self.candidate_companies,
            "uploaded_at": self.uploaded_at.isoformat() if hasattr(self.uploaded_at, "isoformat") else self.uploaded_at
        }

    @staticmethod
    def from_dict(data: dict) -> "Resume":
        """Deserialize a Firestore document dict into a Resume instance."""
        return Resume(
            resume_id=data.get("resume_id"),
            user_id=data.get("user_id", ""),
            filename=data.get("filename", ""),
            file_path=data.get("file_path", ""),
            raw_text=data.get("raw_text"),
            extracted_skills=data.get("extracted_skills"),
            experience_years=data.get("experience_years", 0.0),
            education_level=data.get("education_level"),
            candidate_name=data.get("candidate_name"),
            candidate_email=data.get("candidate_email"),
            candidate_phone=data.get("candidate_phone"),
            candidate_links=data.get("candidate_links", []),
            candidate_companies=data.get("candidate_companies", []),
            uploaded_at=data.get("uploaded_at")
        )

    def save(self) -> None:
        """Persist this Resume document to Firestore (upsert by resume_id)."""
        from app import db
        db.collection("resumes").document(self.resume_id).set(self.to_dict())

    def delete(self) -> None:
        """Permanently delete this Resume and its Firestore document."""
        from app import db
        db.collection("resumes").document(self.resume_id).delete()

    @staticmethod
    def get(resume_id: str) -> "Resume | None":
        """Fetch a single Resume by Firestore document ID. Returns None if not found."""
        from app import db
        doc = db.collection("resumes").document(resume_id).get()
        if doc.exists:
            return Resume.from_dict(doc.to_dict())
        return None

    @staticmethod
    def query_by_user(user_id: str) -> list:
        """Return all Resumes uploaded by the given user, sorted newest first."""
        from app import db
        docs = db.collection("resumes").where("user_id", "==", user_id).stream()
        resumes = [Resume.from_dict(doc.to_dict()) for doc in docs]
        resumes.sort(key=lambda x: x.uploaded_at, reverse=True)
        return resumes

    @staticmethod
    def get_all() -> list:
        """Return all Resume documents in Firestore (admin use only)."""
        from app import db
        docs = db.collection("resumes").stream()
        return [Resume.from_dict(doc.to_dict()) for doc in docs]

    def __repr__(self):
        return f"<Resume {self.filename}>"
