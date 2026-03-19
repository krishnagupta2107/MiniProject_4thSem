import uuid
from datetime import datetime, timezone

def _gen_uuid():
    return str(uuid.uuid4())

class Resume:
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
        if self.extracted_skills:
            return [s.strip() for s in self.extracted_skills.split(",") if s.strip()]
        return []

    def to_dict(self):
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
    def from_dict(data):
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

    def save(self):
        from app import db
        db.collection("resumes").document(self.resume_id).set(self.to_dict())

    def delete(self):
        from app import db
        db.collection("resumes").document(self.resume_id).delete()

    @staticmethod
    def get(resume_id):
        from app import db
        doc = db.collection("resumes").document(resume_id).get()
        if doc.exists:
            return Resume.from_dict(doc.to_dict())
        return None

    @staticmethod
    def query_by_user(user_id):
        from app import db
        docs = db.collection("resumes").where("user_id", "==", user_id).stream()
        resumes = [Resume.from_dict(doc.to_dict()) for doc in docs]
        resumes.sort(key=lambda x: x.uploaded_at, reverse=True)
        return resumes

    @staticmethod
    def get_all():
        from app import db
        docs = db.collection("resumes").stream()
        return [Resume.from_dict(doc.to_dict()) for doc in docs]

    def __repr__(self):
        return f"<Resume {self.filename}>"
