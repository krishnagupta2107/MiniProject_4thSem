"""
models/match.py
Firestore data model for MatchResult documents.

Stores the output of a single resume-to-job scoring run, including the
relevance score, shortlist label, matched/missing skills, and AI feedback.
"""

import uuid
from datetime import datetime, timezone

def _gen_uuid() -> str:
    """Generate a new unique identifier for Firestore document IDs."""
    return str(uuid.uuid4())

class MatchResult:
    """
    Represents the result of matching a single resume against a job description.

    Attributes:
        match_id (str):         Unique Firestore document ID.
        resume_id (str):        Foreign key to the Resume document.
        jd_id (str):            Foreign key to the JobDescription document.
        relevance_score (float):Computed score from 0 to 100.
        shortlist_label (str):  One of 'Shortlisted', 'Maybe', or 'Rejected'.
        matched_skills (str):   CSV of skills found in both resume and JD.
        missing_skills (str):   CSV of required skills absent from the resume.
        feedback (str):         HTML-formatted actionable improvement suggestions.
        created_at (datetime):  UTC timestamp of when the match was computed.
    """
    def __init__(self, match_id=None, resume_id="", jd_id="", relevance_score=0.0,
                 shortlist_label=None, matched_skills=None, missing_skills=None, created_at=None, feedback=None):
        self.match_id = match_id or _gen_uuid()
        self.resume_id = resume_id
        self.jd_id = jd_id
        self.relevance_score = float(relevance_score)
        self.shortlist_label = shortlist_label
        self.matched_skills = matched_skills
        self.missing_skills = missing_skills
        self.feedback = feedback
        if created_at is None:
            self.created_at = datetime.now(timezone.utc)
        elif isinstance(created_at, str):
            self.created_at = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
        else:
            self.created_at = created_at

    def matched_skills_list(self) -> list:
        """Return matched_skills CSV string as a cleaned Python list."""
        if self.matched_skills:
            return [s.strip() for s in self.matched_skills.split(",") if s.strip()]
        return []

    def missing_skills_list(self) -> list:
        """Return missing_skills CSV string as a cleaned Python list."""
        if self.missing_skills:
            return [s.strip() for s in self.missing_skills.split(",") if s.strip()]
        return []

    def to_dict(self) -> dict:
        """Serialize the MatchResult to a Firestore-compatible dictionary."""
        return {
            "match_id": self.match_id,
            "resume_id": self.resume_id,
            "jd_id": self.jd_id,
            "relevance_score": self.relevance_score,
            "shortlist_label": self.shortlist_label,
            "matched_skills": self.matched_skills,
            "missing_skills": self.missing_skills,
            "feedback": self.feedback,
            "created_at": self.created_at.isoformat() if hasattr(self.created_at, "isoformat") else self.created_at
        }

    @staticmethod
    def from_dict(data: dict) -> "MatchResult":
        """Deserialize a Firestore document dict into a MatchResult instance."""
        return MatchResult(
            match_id=data.get("match_id"),
            resume_id=data.get("resume_id", ""),
            jd_id=data.get("jd_id", ""),
            relevance_score=data.get("relevance_score", 0.0),
            shortlist_label=data.get("shortlist_label"),
            matched_skills=data.get("matched_skills"),
            missing_skills=data.get("missing_skills"),
            feedback=data.get("feedback"),
            created_at=data.get("created_at")
        )

    def save(self):
        """Persist this MatchResult document to Firestore (upsert by match_id)."""
        from app import db
        db.collection("match_results").document(self.match_id).set(self.to_dict())

    def delete(self):
        """Permanently delete this MatchResult from Firestore."""
        from app import db
        db.collection("match_results").document(self.match_id).delete()

    @staticmethod
    def get(match_id: str) -> "MatchResult | None":
        """Fetch a single MatchResult by its document ID."""
        from app import db
        doc = db.collection("match_results").document(match_id).get()
        if doc.exists:
            return MatchResult.from_dict(doc.to_dict())
        return None

    @staticmethod
    def query_by_jd(jd_id: str) -> list:
        """Return all MatchResults for a given job description, sorted by score descending."""
        from app import db
        docs = db.collection("match_results").where("jd_id", "==", jd_id).stream()
        matches = [MatchResult.from_dict(doc.to_dict()) for doc in docs]
        matches.sort(key=lambda x: x.relevance_score, reverse=True)
        return matches

    @staticmethod
    def query_by_resume(resume_id: str) -> list:
        """Return all MatchResults associated with a given resume."""
        from app import db
        docs = db.collection("match_results").where("resume_id", "==", resume_id).stream()
        return [MatchResult.from_dict(doc.to_dict()) for doc in docs]

    @staticmethod
    def get_all() -> list:
        """Return all MatchResult documents in Firestore (admin use only)."""
        from app import db
        docs = db.collection("match_results").stream()
        return [MatchResult.from_dict(doc.to_dict()) for doc in docs]

    @property
    def resume(self):
        """Lazy-load the linked Resume object via its resume_id foreign key."""
        from app.models.resume import Resume
        return Resume.get(self.resume_id)

    @property
    def job_description(self):
        """Lazy-load the linked JobDescription object via its jd_id foreign key."""
        from app.models.job import JobDescription
        return JobDescription.get(self.jd_id)

    def __repr__(self):
        return f"<Match score={self.relevance_score}>"
