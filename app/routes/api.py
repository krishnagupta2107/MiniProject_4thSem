"""
routes/api.py
JSON API endpoints for external integrations and data parsing.
All routes are prefixed with /api.
"""

from flask import Blueprint, jsonify, request, current_app
from functools import wraps

from app.models.resume import Resume
from app.models.job    import JobDescription
from app.utils.parsing import parse_resume_text, parse_job_description
from app.utils.helpers import rate_limit

api_bp = Blueprint("api", __name__)

def require_api_key(f):
    """
    Decorator to enforce API key authorization.
    Clients must provide 'X-API-Key' in the header matching the server's API_KEY (or SECRET_KEY).
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        api_key = request.headers.get("X-API-Key")
        # In a real app, use a dedicated API keys table. Here we use SECRET_KEY as a quick token.
        if api_key and api_key == current_app.config.get("SECRET_KEY"):
            return f(*args, **kwargs)
        return jsonify({"error": "Unauthorized. Invalid or missing X-API-Key header."}), 401
    return decorated

@api_bp.route("/parse-resume", methods=["POST"])
@rate_limit("api_parse", limit=20, window=60)
@require_api_key
def api_parse_resume():
    """
    Parse raw resume text and extract candidate information.
    
    Expected JSON payload:
        { "text": "Raw resume text here..." }
        
    Returns:
        JSON response with extracted skills, experience, and education.
    """
    data = request.get_json()
    if not data or not data.get("text"):
        return jsonify({"error": "text field is required"}), 400

    result = parse_resume_text(str(data["text"]))
    return jsonify({
        "success": True,
        "data": {
            "candidate_name":   result["candidate_name"],
            "skills":           result["skills_list"],
            "experience_years": result["experience_years"],
            "education_level":  result["education_level"],
        }
    })


@api_bp.route("/parse-jd", methods=["POST"])
@rate_limit("api_parse", limit=20, window=60)
@require_api_key
def api_parse_jd():
    """
    Parse raw job description text and extract requirements.
    
    Expected JSON payload:
        { "text": "Raw JD text...", "title": "Optional Title" }
        
    Returns:
        JSON response with required skills and experience requirements.
    """
    data = request.get_json()
    if not data or not data.get("text"):
        return jsonify({"error": "text field is required"}), 400

    result = parse_job_description(str(data["text"]), data.get("title", "Job"))
    return jsonify({
        "success": True,
        "data": {
            "required_skills": result["skills_list"],
            "experience_req":  result["experience_req"],
        }
    })


@api_bp.route("/resumes", methods=["GET"])
@require_api_key
def api_list_resumes():
    """
    Retrieve a list of all parsed resumes in the system.
    Requires API key authorization to prevent data leaks.
    """
    resumes = Resume.get_all()
    return jsonify({"resumes": [
        {
            "resume_id":      r.resume_id,
            "candidate_name": r.candidate_name,
            "skills":         r.skills_list(),
            "experience":     r.experience_years,
            "education":      r.education_level,
            "uploaded_at":    r.uploaded_at.isoformat() if hasattr(r.uploaded_at, 'isoformat') else r.uploaded_at,
        }
        for r in resumes
    ]})


@api_bp.route("/jobs", methods=["GET"])
@require_api_key
def api_list_jobs():
    """
    Retrieve a list of all job descriptions in the system.
    Requires API key authorization to prevent data leaks.
    """
    jobs = JobDescription.get_all()
    return jsonify({"jobs": [
        {
            "jd_id":           j.jd_id,
            "title":           j.title,
            "company":         j.company,
            "required_skills": j.skills_list(),
            "experience_req":  j.experience_req,
        }
        for j in jobs
    ]})
