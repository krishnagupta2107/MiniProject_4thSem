"""
test_matching.py
Tests for the resume-job scoring algorithm.
"""

import pytest
from unittest.mock import MagicMock
from app.utils.matching import score_resume_for_job, _get_label, _check_experience


# ---------- helpers to build fake resume/jd objects ----------

def make_resume(skills: list, experience: float = 0.0, raw_text: str = ""):
    r = MagicMock()
    r.skills_list.return_value = skills
    r.experience_years = experience
    r.raw_text = raw_text
    return r


def make_jd(skills: list, raw_text: str = ""):
    j = MagicMock()
    j.skills_list.return_value = skills
    j.raw_text = raw_text
    return j


# ---------- tests ----------

class TestGetLabel:

    def test_shortlisted_at_70(self):
        assert _get_label(70) == "Shortlisted"

    def test_shortlisted_above_70(self):
        assert _get_label(95) == "Shortlisted"

    def test_maybe_at_45(self):
        assert _get_label(45) == "Maybe"

    def test_maybe_between_45_and_70(self):
        assert _get_label(60) == "Maybe"

    def test_rejected_below_45(self):
        assert _get_label(30) == "Rejected"

    def test_rejected_at_zero(self):
        assert _get_label(0) == "Rejected"


class TestCheckExperience:

    def test_meets_requirement(self):
        from app.utils.matching import _check_experience
        assert _check_experience(5, 3) == 1.0

    def test_exactly_meets(self):
        from app.utils.matching import _check_experience
        assert _check_experience(3, 3) == 1.0

    def test_close_but_not_there(self):
        from app.utils.matching import _check_experience
        assert _check_experience(2, 3) == 0.5

    def test_way_under(self):
        from app.utils.matching import _check_experience
        assert _check_experience(0, 5) == 0.0

    def test_no_requirement_specified(self):
        from app.utils.matching import _check_experience
        # when jd doesn't mention years, return neutral
        assert _check_experience(0, 0) == 0.5


class TestScoreResumeForJob:

    def test_perfect_match(self):
        """Candidate has all required skills."""
        resume = make_resume(["python", "flask", "mysql"])
        jd     = make_jd(["python", "flask", "mysql"])
        result = score_resume_for_job(resume, jd)
        assert result["score"] > 70
        assert result["label"] == "Shortlisted"
        assert set(result["matched"]) == {"python", "flask", "mysql"}
        assert result["missing"] == []

    def test_no_match(self):
        """Candidate has completely different skills."""
        resume = make_resume(["java", "spring"])
        jd     = make_jd(["python", "flask", "react"])
        result = score_resume_for_job(resume, jd)
        assert result["score"] < 45
        assert result["label"] == "Rejected"
        assert result["matched"] == []
        assert len(result["missing"]) == 3

    def test_partial_match(self):
        """Candidate has some required skills."""
        resume = make_resume(["python", "mysql"])
        jd     = make_jd(["python", "flask", "mysql", "docker"])
        result = score_resume_for_job(resume, jd)
        assert 0 < result["score"] < 100
        assert "python" in result["matched"]
        assert "mysql"  in result["matched"]
        assert "flask"  in result["missing"]
        assert "docker" in result["missing"]

    def test_empty_jd_skills(self):
        """JD has no required skills — should still return a result."""
        resume = make_resume(["python"])
        jd     = make_jd([])
        result = score_resume_for_job(resume, jd)
        assert isinstance(result["score"], float)
        assert result["label"] in {"Shortlisted", "Maybe", "Rejected"}

    def test_empty_resume_skills(self):
        """Resume has no skills — should be low score."""
        resume = make_resume([])
        jd     = make_jd(["python", "flask"])
        result = score_resume_for_job(resume, jd)
        assert result["score"] < 45
        assert result["matched"] == []

    def test_score_is_capped_at_100(self):
        resume = make_resume(["python", "flask", "mysql", "docker", "react"])
        jd     = make_jd(["python", "flask", "mysql"], raw_text="1 year experience")
        result = score_resume_for_job(resume, jd)
        assert result["score"] <= 100

    def test_result_has_explanation(self):
        resume = make_resume(["python"])
        jd     = make_jd(["python", "flask"])
        result = score_resume_for_job(resume, jd)
        assert "explanation" in result
        assert isinstance(result["explanation"], str)
        assert len(result["explanation"]) > 0

    def test_case_insensitive_matching(self):
        """Skills comparison should be case-insensitive."""
        resume = make_resume(["Python", "FLASK"])
        jd     = make_jd(["python", "flask"])
        result = score_resume_for_job(resume, jd)
        assert len(result["matched"]) == 2

    def test_shortlisted_label_at_high_score(self):
        resume = make_resume(["python", "flask", "mysql", "docker", "react"])
        jd     = make_jd(["python", "flask", "mysql", "docker", "react"])
        result = score_resume_for_job(resume, jd)
        assert result["label"] == "Shortlisted"

    def test_experience_boost_applied(self):
        """Candidate with matching experience should score higher than one without."""
        resume_exp    = make_resume(["python"], experience=5.0)
        resume_no_exp = make_resume(["python"], experience=0.0)
        jd = make_jd(["python"], raw_text="5 years experience required")

        score_with    = score_resume_for_job(resume_exp, jd)["score"]
        score_without = score_resume_for_job(resume_no_exp, jd)["score"]

        assert score_with > score_without
