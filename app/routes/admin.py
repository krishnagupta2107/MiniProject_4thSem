"""
routes/admin.py
Admin-only dashboard.
"""

from flask import Blueprint, render_template
from flask_login import login_required

from app.models.user   import User
from app.models.resume import Resume
from app.models.job    import JobDescription
from app.models.match  import MatchResult
from app.utils.helpers import admin_required

admin_bp = Blueprint("admin", __name__)


@admin_bp.route("/admin")
@login_required
@admin_required
def admin_dashboard():
    all_users = User.get_all()
    all_resumes = Resume.get_all()
    all_jobs = JobDescription.get_all()
    all_matches = MatchResult.get_all()

    stats = {
        "users":   len(all_users),
        "resumes": len(all_resumes),
        "jobs":    len(all_jobs),
        "matches": len(all_matches),
    }

    # naya wala upar!
    recent_users = sorted(all_users, key=lambda x: x.created_at, reverse=True)[:10]

    # pehla graph
    labels_count = {}
    for m in all_matches:
        label = m.shortlist_label or "Unknown"
        labels_count[label] = labels_count.get(label, 0) + 1

    chart_matches_labels = list(labels_count.keys())
    chart_matches_data = list(labels_count.values())

    # doosra view
    chart_overview_labels = ['Users', 'Resumes', 'Job Descriptions', 'Matches']
    chart_overview_data = [stats['users'], stats['resumes'], stats['jobs'], stats['matches']]

    return render_template("admin/dashboard.html", stats=stats, recent_users=recent_users,
                           chart_matches_labels=chart_matches_labels, chart_matches_data=chart_matches_data,
                           chart_overview_labels=chart_overview_labels, chart_overview_data=chart_overview_data)
