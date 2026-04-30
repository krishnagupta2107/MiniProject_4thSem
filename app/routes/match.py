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
from app.services.match_service import score_resume_for_job
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

        # sabka score nikalte hai
        count = 0
        from datetime import datetime, timezone
        from app.services.model_lifecycle import lifecycle_manager
        for r in resumes:
            result = score_resume_for_job(r, jd)
            lifecycle_manager.log_metrics(r.resume_id, jd.jd_id, result.get("metrics", {}))

            # check karo pehle se hai kya match
            existing = None
            for m in MatchResult.query_by_resume(r.resume_id):
                if m.jd_id == jd.jd_id:
                    existing = m
                    break

            fb = None
            if result["score"] < 90:
                suggestions = ["<strong>Areas for Improvement:</strong><br>"]
                
                # Check for missing skills
                if result["missing"]:
                    missing_str = ", ".join(result["missing"])
                    suggestions.append(f"• <strong>Skills to Learn/Add:</strong> Consider acquiring these missing skills and adding them to your resume: {missing_str}.")
                else:
                    suggestions.append("• <strong>Keywords:</strong> While you have the core skills, try optimizing your resume terminology to better align with the job description phrasing.")

                # Check for experience gap
                if result["score"] < 70:
                    suggestions.append("• <strong>Experience:</strong> Building relevant side projects or gaining hands-on experience in the required domains can significantly bridge this gap.")
                
                # Resume formatting action items
                if result["label"] == "Rejected":
                    suggestions.append("• <strong>Next Steps:</strong> This role might be a stretch given your current profile. Focus on entry-level equivalent roles or extensively upskill in the core requirements.")
                elif result["label"] == "Maybe":
                    suggestions.append("• <strong>Actionable Steps:</strong> Highlight any hidden relevant experiences in your bullet points to push your profile into the 'Shortlisted' tier.")

                fb = "<br>".join(suggestions)
            else:
                fb = "Great match! Ensure your resume formatting is clean and easy to read before applying."

            if existing:
                existing.relevance_score = result["score"]
                existing.shortlist_label = result["label"]
                existing.matched_skills  = ", ".join(result["matched"])
                existing.missing_skills  = ", ".join(result["missing"])
                existing.feedback        = fb
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
                    feedback        = fb
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

    # manual filter marna pad raha hai sql join nai hai
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
