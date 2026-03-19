import uuid
from datetime import datetime, timezone

def _gen_uuid():
    return str(uuid.uuid4())

class MatchResult:
    def __init__(self, match_id=None, resume_id="", jd_id="", relevance_score=0.0,
                 shortlist_label=None, matched_skills=None, missing_skills=None, created_at=None):
        self.match_id = match_id or _gen_uuid()
        self.resume_id = resume_id
        self.jd_id = jd_id
        self.relevance_score = float(relevance_score)
        self.shortlist_label = shortlist_label
        self.matched_skills = matched_skills
        self.missing_skills = missing_skills
        if created_at is None:
            self.created_at = datetime.now(timezone.utc)
        elif isinstance(created_at, str):
            self.created_at = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
        else:
            self.created_at = created_at

    def matched_skills_list(self):
        if self.matched_skills:
            return [s.strip() for s in self.matched_skills.split(",") if s.strip()]
        return []

    def missing_skills_list(self):
        if self.missing_skills:
            return [s.strip() for s in self.missing_skills.split(",") if s.strip()]
        return []

    def to_dict(self):
        return {
            "match_id": self.match_id,
            "resume_id": self.resume_id,
            "jd_id": self.jd_id,
            "relevance_score": self.relevance_score,
            "shortlist_label": self.shortlist_label,
            "matched_skills": self.matched_skills,
            "missing_skills": self.missing_skills,
            "created_at": self.created_at.isoformat() if hasattr(self.created_at, "isoformat") else self.created_at
        }

    @staticmethod
    def from_dict(data):
        return MatchResult(
            match_id=data.get("match_id"),
            resume_id=data.get("resume_id", ""),
            jd_id=data.get("jd_id", ""),
            relevance_score=data.get("relevance_score", 0.0),
            shortlist_label=data.get("shortlist_label"),
            matched_skills=data.get("matched_skills"),
            missing_skills=data.get("missing_skills"),
            created_at=data.get("created_at")
        )

    def save(self):
        from app import db
        db.collection("match_results").document(self.match_id).set(self.to_dict())

    def delete(self):
        from app import db
        db.collection("match_results").document(self.match_id).delete()

    @staticmethod
    def get(match_id):
        from app import db
        doc = db.collection("match_results").document(match_id).get()
        if doc.exists:
            return MatchResult.from_dict(doc.to_dict())
        return None

    @staticmethod
    def query_by_jd(jd_id):
        from app import db
        docs = db.collection("match_results").where("jd_id", "==", jd_id).stream()
        matches = [MatchResult.from_dict(doc.to_dict()) for doc in docs]
        matches.sort(key=lambda x: x.relevance_score, reverse=True)
        return matches

    @staticmethod
    def query_by_resume(resume_id):
        from app import db
        docs = db.collection("match_results").where("resume_id", "==", resume_id).stream()
        return [MatchResult.from_dict(doc.to_dict()) for doc in docs]

    @staticmethod
    def get_all():
        from app import db
        docs = db.collection("match_results").stream()
        return [MatchResult.from_dict(doc.to_dict()) for doc in docs]

    # Helper property to mimic SQLAlchemy relations in templates
    @property
    def resume(self):
        from app.models.resume import Resume
        return Resume.get(self.resume_id)

    @property
    def job_description(self):
        from app.models.job import JobDescription
        return JobDescription.get(self.jd_id)

    def __repr__(self):
        return f"<Match score={self.relevance_score}>"
