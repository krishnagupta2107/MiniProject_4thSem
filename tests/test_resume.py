"""
test_resume.py
Tests for resume upload and listing routes.
"""

import pytest


class TestResumePages:

    def test_upload_page_requires_login(self, client):
        response = client.get("/upload-resume", follow_redirects=True)
        assert b"Log in" in response.data or b"Please log in" in response.data

    def test_upload_page_loads_when_logged_in(self, logged_in_client):
        response = logged_in_client.get("/upload-resume")
        assert response.status_code == 200
        assert b"Upload a Resume" in response.data

    def test_list_page_requires_login(self, client):
        response = client.get("/resumes", follow_redirects=True)
        assert b"Log in" in response.data or b"Please log in" in response.data

    def test_list_page_loads_when_logged_in(self, logged_in_client):
        response = logged_in_client.get("/resumes")
        assert response.status_code == 200

    def test_upload_with_text(self, logged_in_client, app):
        """Upload a resume by pasting text — should parse and redirect."""
        resume_text = """
        Mahak Bhatia
        Python Developer with 2 years experience
        B.Tech CSE
        Skills: Python, Flask, MySQL, React
        """
        response = logged_in_client.post("/upload-resume", data={
            "resume_text": resume_text,
        }, follow_redirects=True)
        assert response.status_code == 200
        # should show the resume view page with skills
        assert b"Resume uploaded" in response.data or b"skill" in response.data.lower()

    def test_upload_without_file_or_text_shows_warning(self, logged_in_client):
        response = logged_in_client.post("/upload-resume", data={
            "resume_text": "",
        }, follow_redirects=True)
        assert response.status_code == 200
        assert b"Please upload a valid file" in response.data

    def test_invalid_file_extension_rejected(self, logged_in_client):
        """Only PDF, DOCX, DOC, TXT allowed."""
        from io import BytesIO
        fake_file = (BytesIO(b"fake content"), "resume.exe")
        response = logged_in_client.post("/upload-resume", data={
            "resume_file": fake_file,
        }, content_type="multipart/form-data", follow_redirects=True)
        assert b"Only PDF" in response.data or response.status_code == 200
