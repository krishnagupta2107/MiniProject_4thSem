"""
test_models.py
Basic unit tests for the database models.
"""

import pytest


class TestUserModel:

    def test_password_hashing(self, app):
        from app.models.user import User
        with app.app_context():
            u = User(email="hash@test.com", full_name="Hash Test")
            u.set_password("mysecretpass")
            assert u.password != "mysecretpass"              # not stored in plain text
            assert u.check_password("mysecretpass") is True
            assert u.check_password("wrongpass")   is False

    def test_is_admin_false_by_default(self, app):
        from app.models.user import User
        with app.app_context():
            u = User(email="recruiter@test.com", full_name="Recruiter")
            u.set_password("pass")
            assert u.is_admin() is False

    def test_is_admin_true_for_admin_role(self, app):
        from app.models.user import User
        with app.app_context():
            u = User(email="admin@test.com", full_name="Admin", role="admin")
            u.set_password("pass")
            assert u.is_admin() is True

    def test_get_id_returns_user_id(self, app):
        from app.models.user import User
        with app.app_context():
            u = User(email="id@test.com", full_name="ID Test")
            u.set_password("pass")
            assert u.get_id() == u.user_id

    def test_repr(self, app):
        from app.models.user import User
        with app.app_context():
            u = User(email="repr@test.com", full_name="Repr")
            u.set_password("pass")
            assert "repr@test.com" in repr(u)


class TestResumeModel:

    def test_skills_list_parses_comma_separated(self, app):
        from app.models.resume import Resume
        with app.app_context():
            r = Resume(
                user_id="some-uuid",
                filename="test.pdf",
                extracted_skills="python, flask, mysql",
            )
            skills = r.skills_list()
            assert "python" in skills
            assert "flask"  in skills
            assert "mysql"  in skills
            assert len(skills) == 3

    def test_skills_list_empty_when_none(self, app):
        from app.models.resume import Resume
        with app.app_context():
            r = Resume(user_id="x", filename="x.pdf", extracted_skills=None)
            assert r.skills_list() == []

    def test_skills_list_handles_whitespace(self, app):
        from app.models.resume import Resume
        with app.app_context():
            r = Resume(user_id="x", filename="x.pdf", extracted_skills=" python , react ")
            skills = r.skills_list()
            assert "python" in skills
            assert "react"  in skills


class TestJobDescriptionModel:

    def test_skills_list(self, app):
        from app.models.job import JobDescription
        with app.app_context():
            j = JobDescription(
                user_id="x",
                title="Dev",
                raw_text="...",
                required_skills="python, docker, aws",
            )
            assert "python" in j.skills_list()
            assert "docker" in j.skills_list()
            assert "aws"    in j.skills_list()

    def test_skills_list_empty(self, app):
        from app.models.job import JobDescription
        with app.app_context():
            j = JobDescription(user_id="x", title="Dev", raw_text="...", required_skills=None)
            assert j.skills_list() == []


class TestMatchResultModel:

    def test_matched_skills_list(self, app):
        from app.models.match import MatchResult
        with app.app_context():
            m = MatchResult(
                resume_id="a",
                jd_id="b",
                relevance_score=75.0,
                matched_skills="python, flask",
                missing_skills="docker, aws",
            )
            assert "python" in m.matched_skills_list()
            assert "flask"  in m.matched_skills_list()

    def test_missing_skills_list(self, app):
        from app.models.match import MatchResult
        with app.app_context():
            m = MatchResult(
                resume_id="a",
                jd_id="b",
                relevance_score=40.0,
                matched_skills="",
                missing_skills="react, node, docker",
            )
            assert "react"  in m.missing_skills_list()
            assert "docker" in m.missing_skills_list()

    def test_empty_skills_return_empty_list(self, app):
        from app.models.match import MatchResult
        with app.app_context():
            m = MatchResult(resume_id="a", jd_id="b", relevance_score=0.0)
            assert m.matched_skills_list() == []
            assert m.missing_skills_list() == []
