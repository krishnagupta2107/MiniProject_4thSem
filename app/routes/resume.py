"""
routes/resume.py
Upload, list, and view resumes.
"""

import os

from flask import (
    Blueprint, render_template, request, redirect, url_for, flash, current_app
)
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename

from app.models.resume import Resume
from app.utils.parsing import allowed_file, parse_resume_file, parse_resume_text, sanitize_text
from app.utils.helpers import rate_limit

resume_bp = Blueprint("resume", __name__)


@resume_bp.route("/upload-resume", methods=["GET", "POST"])
@login_required
@rate_limit("upload_resume", limit=5, window=60)
def upload_resume():
    if request.method == "POST":
        file_inputs = request.files.getlist("resume_file")
        text_input  = sanitize_text(request.form.get("resume_text", ""))
        
        processed_count = 0
        total_skills = 0

        # yaha file lenge
        for file_input in file_inputs:
            if file_input and file_input.filename:
                if not allowed_file(file_input.filename):
                    flash(f"Skipped {file_input.filename}: Only PDF, DOCX, DOC, and TXT files are accepted.", "warning")
                    continue

                filename = secure_filename(file_input.filename)
                filepath = os.path.join(current_app.config["UPLOAD_FOLDER"], filename)
                file_input.save(filepath)
                parsed = parse_resume_file(filepath)

                if "error" in parsed:
                    flash(f"Could not read {filename}: {parsed['error']}", "danger")
                    continue
                
                from app.utils.extractors import extract_email, extract_phone, extract_links, extract_entities
                raw = parsed["raw_text"]
                email = extract_email(raw)
                phone = extract_phone(raw)
                links = extract_links(raw)
                ents = extract_entities(raw)
                
                name = parsed["candidate_name"]
                if name == "Unknown" and ents["names"]:
                    name = ents["names"][0]
                    
                resume = Resume(
                    user_id          = current_user.user_id,
                    filename         = filename,
                    file_path        = filepath,
                    raw_text         = raw,
                    extracted_skills = parsed["extracted_skills"],
                    experience_years = parsed["experience_years"],
                    education_level  = parsed["education_level"],
                    candidate_name   = name,
                    candidate_email  = email,
                    candidate_phone  = phone,
                    candidate_links  = links,
                    candidate_companies = ents["companies"]
                )
                resume.save()
                processed_count += 1
                total_skills += len(parsed["skills_list"])

        # direct text paste
        if text_input and not processed_count:
            parsed   = parse_resume_text(text_input)
            from app.utils.extractors import extract_email, extract_phone, extract_links, extract_entities
            raw = parsed["raw_text"]
            email = extract_email(raw)
            phone = extract_phone(raw)
            links = extract_links(raw)
            ents = extract_entities(raw)
            
            name = parsed["candidate_name"]
            if name == "Unknown" and ents["names"]:
                name = ents["names"][0]
                
            resume = Resume(
                user_id          = current_user.user_id,
                filename         = "pasted_text.txt",
                file_path        = "",
                raw_text         = raw,
                extracted_skills = parsed["extracted_skills"],
                experience_years = parsed["experience_years"],
                education_level  = parsed["education_level"],
                candidate_name   = name,
                candidate_email  = email,
                candidate_phone  = phone,
                candidate_links  = links,
                candidate_companies = ents["companies"]
            )
            resume.save()
            processed_count += 1
            total_skills += len(parsed["skills_list"])

        if processed_count == 0:
            flash("Please upload a valid file or paste your resume text.", "warning")
            return render_template("resume/upload.html")
        
        flash(f"Successfully uploaded {processed_count} resume(s)! Found {total_skills} skills in total.", "success")
        return redirect(url_for("resume.list_resumes"))

    return render_template("resume/upload.html")


@resume_bp.route("/resumes")
@login_required
def list_resumes():
    resumes = Resume.query_by_user(current_user.user_id)
    return render_template("resume/list.html", resumes=resumes)


@resume_bp.route("/resumes/<resume_id>")
@login_required
def view_resume(resume_id):
    from flask import abort
    resume = Resume.get(resume_id)
    if not resume:
        abort(404)

    # sirf owner aur admin dekhega
    if resume.user_id != current_user.user_id and not current_user.is_admin():
        flash("You don't have permission to view this resume.", "danger")
        return redirect(url_for("resume.list_resumes"))

    return render_template("resume/view.html", resume=resume)


@resume_bp.route("/resumes/<resume_id>/delete", methods=["POST"])
@login_required
def delete_resume(resume_id):
    from flask import abort
    resume = Resume.get(resume_id)
    if not resume:
        abort(404)

    if resume.user_id != current_user.user_id and not current_user.is_admin():
        flash("Not allowed.", "danger")
        return redirect(url_for("resume.list_resumes"))

    resume.delete()
    flash("Resume deleted.", "info")
    return redirect(url_for("resume.list_resumes"))
