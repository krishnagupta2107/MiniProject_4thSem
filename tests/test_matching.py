"""
test_matching.py
Unit tests for the core resume-to-job matching engine.
Tests label classification, experience scoring, and evaluation metrics.
"""

import pytest
from app.services.match_service import _get_label, _check_experience, score_resume_for_job


class TestMatchingLogic:

    def test_get_label_shortlist(self):
        """Candidates >= 70 score must classify as Shortlisted."""
        assert _get_label(85.0) == "Shortlisted"
        assert _get_label(70.0) == "Shortlisted"

    def test_get_label_maybe(self):
        """Candidates >= 45 and < 70 score classify as Maybe."""
        assert _get_label(55.0) == "Maybe"
        assert _get_label(45.0) == "Maybe"

    def test_get_label_rejected(self):
        """Candidates < 45 score strictly classify as Rejected."""
        assert _get_label(44.9) == "Rejected"
        assert _get_label(20.0) == "Rejected"

    def test_check_experience_underqualified(self):
        """Candidate more than 1 year below requirement returns 0.0."""
        assert _check_experience(candidate_years=1.0, required_years=5.0) == 0.0

    def test_check_experience_perfect_fit(self):
        """Candidate meeting exact requirement returns 1.0."""
        assert _check_experience(candidate_years=5.0, required_years=5.0) == 1.0

    def test_check_experience_overqualified(self):
        """Overqualified candidate still returns 1.0 (no penalty)."""
        assert _check_experience(candidate_years=8.0, required_years=2.0) == 1.0

    def test_check_experience_edge_case_zero(self):
        """No experience requirement stated returns neutral 0.5."""
        assert _check_experience(candidate_years=0.0, required_years=0.0) == 0.5

    def test_check_experience_close_gap(self):
        """Candidate within 1 year of requirement returns 0.5 (close enough)."""
        assert _check_experience(candidate_years=4.0, required_years=5.0) == 0.5


class TestEvaluationMetrics:

    def test_score_result_has_metrics_keys(self):
        """score_resume_for_job must return a dict containing a 'metrics' key."""
        class MockDoc:
            raw_text = "Python developer with 3 years experience in Django and REST APIs"
            experience_years = 3.0
            def skills_list(self):
                return ["python", "django", "rest api"]

        resume = MockDoc()
        jd = MockDoc()
        jd.raw_text = "Looking for a Python developer with Django experience"
        jd.experience_years = 2.0

        result = score_resume_for_job(resume, jd)

        assert "metrics" in result, "Result must include evaluation metrics"
        assert "precision" in result["metrics"]
        assert "recall" in result["metrics"]
        assert "f1_score" in result["metrics"]

    def test_metrics_are_between_zero_and_one(self):
        """All metric values must be in range [0, 1]."""
        class MockDoc:
            raw_text = "Machine learning engineer skilled in tensorflow and pytorch"
            experience_years = 2.0
            def skills_list(self):
                return ["tensorflow", "pytorch"]

        resume = MockDoc()
        jd = MockDoc()
        jd.raw_text = "ML engineer needed with tensorflow, pytorch, scikit-learn"
        jd.experience_years = 3.0

        result = score_resume_for_job(resume, jd)
        m = result["metrics"]

        assert 0.0 <= m["precision"] <= 1.0
        assert 0.0 <= m["recall"] <= 1.0
        assert 0.0 <= m["f1_score"] <= 1.0

    def test_perfect_skill_match_f1_equals_one(self):
        """When all required skills are matched, precision and recall should both be 1.0."""
        class MockDoc:
            raw_text = "Expert in python and sql"
            experience_years = 3.0
            def skills_list(self):
                return ["python", "sql"]

        resume = MockDoc()
        jd = MockDoc()
        jd.raw_text = "Need python and sql developer"
        jd.experience_years = 2.0

        result = score_resume_for_job(resume, jd)
        m = result["metrics"]

        assert m["recall"] == 1.0, "All required skills matched → recall must be 1.0"
        assert m["f1_score"] == 1.0, "Perfect match → F1 must be 1.0"

