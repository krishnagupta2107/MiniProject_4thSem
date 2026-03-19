"""
routes/match.py
Run resume-job matching and display results.
"""

from datetime import datetime

from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user

from app.models.resume import Resume
from app.models.job    import JobDescription
from app.models.match  import MatchResult
from app.utils.matching import score_resume_for_job
from app.utils.helpers  import rate_limit

match_bp = Blueprint("match", __name__)


@match_bp.route("/match", methods=["GET", "POST"])
@login_required
@rate_limit("run_match", limit=10, window=60)
def run_match():
    jobs = JobDescription.query_by_user(current_user.user_id)

    if request.method == "POST":
        jd_id = request.form.get("jd_id", "").strip()
        if not jd_id:
            flash("Please select a job description first.", "warning")
            return render_template("match/select.html", jobs=jobs)

        jd = JobDescription.get(jd_id)
        if not jd:
            flash("Job not found.", "danger")
            return redirect(url_for("match.run_match"))

        resumes = Resume.query_by_user(current_user.user_id)

        if not resumes:
            flash("You haven't uploaded any resumes yet.", "warning")
            return redirect(url_for("resume.upload_resume"))

        # run scoring for each resume
        count = 0
        from datetime import datetime, timezone
        for r in resumes:
            result = score_resume_for_job(r, jd)

            # Manually find existing match
            existing = None
            for m in MatchResult.query_by_resume(r.resume_id):
                if m.jd_id == jd.jd_id:
                    existing = m
                    break

            if existing:
                existing.relevance_score = result["score"]
                existing.shortlist_label = result["label"]
                existing.matched_skills  = ", ".join(result["matched"])
                existing.missing_skills  = ", ".join(result["missing"])
                existing.created_at      = datetime.now(timezone.utc).isoformat()
                existing.save()
            else:
                match = MatchResult(
                    resume_id       = r.resume_id,
                    jd_id           = jd.jd_id,
                    relevance_score = result["score"],
                    shortlist_label = result["label"],
                    matched_skills  = ", ".join(result["matched"]),
                    missing_skills  = ", ".join(result["missing"]),
                )
                match.save()
            count += 1

        flash(f"Matching complete! Scored {count} resume(s).", "success")
        return redirect(url_for("match.match_results", jd_id=jd.jd_id))

    return render_template("match/select.html", jobs=jobs)


@match_bp.route("/matches/<jd_id>")
@login_required
def match_results(jd_id):
    from flask import abort
    jd = JobDescription.get(jd_id)
    if not jd:
        abort(404)

    if jd.user_id != current_user.user_id and not current_user.is_admin():
        flash("Not allowed to view these results.", "danger")
        return redirect(url_for("match.run_match"))

    # Fetch matches and filter manually for user_id to emulate SQL JOIN
    raw_matches = MatchResult.query_by_jd(jd.jd_id)
    matches = []
    for m in raw_matches:
        if m.resume and m.resume.user_id == current_user.user_id:
            matches.append(m)

    avg_score = 0
    if matches:
        avg_score = round(sum(m.relevance_score for m in matches) / len(matches), 1)

    return render_template(
        "match/results.html",
        jd=jd,
        matches=matches,
        avg_score=avg_score,
    )
