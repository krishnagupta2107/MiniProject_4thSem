"""
routes/job.py
Upload, list, view job descriptions.
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user

from app.models.job import JobDescription
from app.utils.parsing import parse_job_description, sanitize_text
from app.utils.helpers import rate_limit
from app.utils.job_board import fetch_mock_jobs

job_bp = Blueprint("job", __name__)


@job_bp.route("/upload-jd", methods=["GET", "POST"])
@login_required
@rate_limit("upload_jd", limit=5, window=60)
def upload_jd():
    """
    Handle job description creation from pasted text.

    GET:  Renders the upload form.
    POST: Validates inputs, runs NLP parsing to extract required skills,
          and persists the job description to Firestore.
    
    Raises:
        flash(warning): If title or description text is missing.
        flash(success): On successful save with skill count.
    """
    if request.method == "POST":
        title    = request.form.get("title", "").strip()
        company  = request.form.get("company", "").strip()
        location = request.form.get("location", "").strip()
        jd_text  = sanitize_text(request.form.get("jd_text", ""))

        if not title:
            flash("Job title is required.", "warning")
            return render_template("job/upload.html")
        if not jd_text:
            flash("Job description text is required.", "warning")
            return render_template("job/upload.html")

        parsed = parse_job_description(jd_text, title)

        jd = JobDescription(
            user_id         = current_user.user_id,
            title           = title,
            company         = company or None,
            location        = location or None,
            raw_text        = parsed["raw_text"],
            required_skills = parsed["required_skills"],
            experience_req  = parsed["experience_req"],
        )
        jd.save()

        skill_count = len(parsed["skills_list"])
        flash(f"Job description saved! Found {skill_count} required skill(s).", "success")
        return redirect(url_for("job.view_jd", jd_id=jd.jd_id))

    return render_template("job/upload.html")


@job_bp.route("/jobs")
@login_required
def list_jobs():
    """List all job descriptions created by the currently logged-in user."""
    jobs = JobDescription.query_by_user(current_user.user_id)
    return render_template("job/list.html", jobs=jobs)


@job_bp.route("/jobs/<jd_id>")
@login_required
def view_jd(jd_id):
    """
    View the details and extracted skills of a specific job description.
    
    Only the owner or an admin can access this view.
    Returns 404 if the jd_id does not exist in Firestore.
    """
    from flask import abort
    jd = JobDescription.get(jd_id)
    if not jd:
        abort(404)
    if jd.user_id != current_user.user_id and not current_user.is_admin():
        flash("You don't have permission to view this job.", "danger")
        return redirect(url_for("job.list_jobs"))
    return render_template("job/view.html", jd=jd)


@job_bp.route("/jobs/<jd_id>/delete", methods=["POST"])
@login_required
def delete_jd(jd_id):
    """
    Permanently delete a job description from Firestore.
    
    Only the JD owner or an admin can perform this action.
    Returns 404 if the jd_id does not exist.
    """
    from flask import abort
    jd = JobDescription.get(jd_id)
    if not jd:
        abort(404)
    if jd.user_id != current_user.user_id and not current_user.is_admin():
        flash("Not allowed.", "danger")
        return redirect(url_for("job.list_jobs"))
    jd.delete()
    flash("Job description deleted.", "info")
    return redirect(url_for("job.list_jobs"))

@job_bp.route("/sync-jobs", methods=["POST"])
@login_required
def sync_jobs():
    """
    Admin-only route to import job listings from an external mock board.
    
    Fetches mock jobs and saves them as JobDescription documents in Firestore
    under the current admin user's account.
    """
    if not current_user.is_admin():
        flash("Only admins can sync external jobs.", "danger")
        return redirect(url_for("job.list_jobs"))
        
    mock_jobs = fetch_mock_jobs()
    count = 0
    for mj in mock_jobs:
        jd = JobDescription(
            user_id         = current_user.user_id,
            title           = mj["title"],
            company         = "External Board",
            raw_text        = mj["description"],
            required_skills = mj["required_skills"],
            experience_req  = mj["experience_years"],
        )
        jd.save()
        count += 1
        
    flash(f"Successfully synced {count} jobs from the external board!", "success")
    return redirect(url_for("job.list_jobs"))
