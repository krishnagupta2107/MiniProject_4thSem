"""
routes/api.py
Simple JSON API endpoints for external integrations.
All under /api prefix.
"""

from flask import Blueprint, jsonify, request

from app.models.resume import Resume
from app.models.job    import JobDescription
from app.utils.parsing import parse_resume_text, parse_job_description
from app.utils.helpers import rate_limit

api_bp = Blueprint("api", __name__)


@api_bp.route("/parse-resume", methods=["POST"])
@rate_limit("api_parse", limit=20, window=60)
def api_parse_resume():
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
def api_parse_jd():
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
def api_list_resumes():
    resumes = Resume.query.all()
    return jsonify({"resumes": [
        {
            "resume_id":      r.resume_id,
            "candidate_name": r.candidate_name,
            "skills":         r.skills_list(),
            "experience":     r.experience_years,
            "education":      r.education_level,
            "uploaded_at":    r.uploaded_at.isoformat(),
        }
        for r in resumes
    ]})


@api_bp.route("/jobs", methods=["GET"])
def api_list_jobs():
    jobs = JobDescription.query.all()
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
