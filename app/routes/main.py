"""
routes/main.py
Landing page, dashboard, about.
"""

from collections import Counter

from flask import Blueprint, render_template
from flask_login import login_required, current_user

from app.models.resume import Resume
from app.models.job    import JobDescription
from app.models.match  import MatchResult

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def index():
    return render_template("index.html")


@main_bp.route("/about")
def about():
    return render_template("about.html")


@main_bp.route("/dashboard")
@login_required
def dashboard():
    resumes   = Resume.query_by_user(current_user.user_id)
    job_descs = JobDescription.query_by_user(current_user.user_id)

    user_matches = []
    for m in MatchResult.get_all():
        r = m.resume
        if r and r.user_id == current_user.user_id:
            user_matches.append(m)
            
    user_matches.sort(key=lambda x: x.created_at, reverse=True)
    match_count = len(user_matches)
    recent_matches = user_matches[:5]

    # top 20 mein se best skills
    resume_skills = Counter()
    jd_skills     = Counter()
    for r in resumes[:20]:
        resume_skills.update(s.lower() for s in r.skills_list())
    for j in job_descs[:20]:
        jd_skills.update(s.lower() for s in j.skills_list())

    stats = {
        "resumes": len(resumes),
        "jobs":    len(job_descs),
        "matches": match_count,
    }

    return render_template(
        "dashboard.html",
        resumes=resumes[:5],
        job_descs=job_descs[:5],
        stats=stats,
        top_resume_skills=resume_skills.most_common(6),
        top_jd_skills=jd_skills.most_common(6),
        recent_matches=recent_matches,
    )
