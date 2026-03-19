"""
test_parsing.py
Tests for skill extraction, education detection, and experience parsing.
These are pure unit tests — no DB or Flask needed.
"""

import pytest
from app.utils.parsing import (
    extract_skills,
    extract_experience_years,
    extract_education_level,
    extract_candidate_name,
    parse_resume_text,
    parse_job_description,
    sanitize_text,
)


class TestExtractSkills:

    def test_finds_python(self):
        assert "python" in extract_skills("I know Python and Flask")

    def test_finds_multiple_skills(self):
        text = "Experience with Python, React, Docker and MySQL"
        skills = extract_skills(text)
        assert "python" in skills
        assert "react"  in skills
        assert "docker" in skills
        assert "mysql"  in skills

    def test_case_insensitive(self):
        assert "python" in extract_skills("PYTHON DEVELOPER")

    def test_returns_sorted_list(self):
        skills = extract_skills("docker python react")
        assert skills == sorted(skills)

    def test_no_skills_returns_empty(self):
        assert extract_skills("Hello world, nothing here") == []

    def test_no_partial_matches(self):
        # "java" should not match inside "javascript" — wait, actually both are in
        # the skills list so let's test a word that's a substring of another
        result = extract_skills("reactivity is high")
        # "react" should not be in there — "reactivity" is not "react"
        assert "react" not in result

    def test_multi_word_skill(self):
        assert "machine learning" in extract_skills("experience in machine learning and AI")


class TestExtractExperienceYears:

    def test_basic_years(self):
        assert extract_experience_years("5 years of experience") == 5.0

    def test_decimal_years(self):
        assert extract_experience_years("2.5 years") == 2.5

    def test_yrs_abbreviation(self):
        assert extract_experience_years("3 yrs experience") == 3.0

    def test_plus_notation(self):
        assert extract_experience_years("8+ years") == 8.0

    def test_no_experience_mentioned(self):
        assert extract_experience_years("No experience info here") == 0.0

    def test_takes_first_match(self):
        # should grab the first number
        result = extract_experience_years("3 years at Company A, then 5 years at Company B")
        assert result == 3.0


class TestExtractEducationLevel:

    def test_bachelors_btech(self):
        assert extract_education_level("B.Tech in Computer Science") == "Bachelors"

    def test_masters(self):
        assert extract_education_level("M.Tech from IIT") == "Masters"

    def test_phd(self):
        assert extract_education_level("PhD in Machine Learning") == "PhD"

    def test_diploma(self):
        assert extract_education_level("Diploma in Engineering") == "Diploma"

    def test_no_education_returns_empty(self):
        assert extract_education_level("just some random text") == ""

    def test_bachelor_keyword(self):
        assert extract_education_level("Bachelor of Science in CS") == "Bachelors"

    def test_mca(self):
        assert extract_education_level("MCA from Delhi University") == "Masters"


class TestExtractCandidateName:

    def test_grabs_first_line_name(self):
        text = "Krishna Gupta\nSoftware Developer\n5 years Python"
        name = extract_candidate_name(text)
        assert name == "Krishna Gupta"

    def test_skips_resume_keyword(self):
        text = "Resume\nJohn Smith\nDeveloper"
        name = extract_candidate_name(text)
        assert name == "John Smith"

    def test_returns_unknown_if_nothing_found(self):
        assert extract_candidate_name("") == "Unknown"


class TestParseResumeText:

    def test_returns_all_fields(self):
        text = """
        Anushka Bansal
        Python Developer with 3 years experience
        B.Tech from AKTU
        Skills: Python, Flask, MySQL, Docker
        """
        result = parse_resume_text(text)
        assert "raw_text"         in result
        assert "candidate_name"   in result
        assert "extracted_skills" in result
        assert "experience_years" in result
        assert "education_level"  in result
        assert "skills_list"      in result

    def test_skills_list_is_list(self):
        result = parse_resume_text("Python developer with flask experience")
        assert isinstance(result["skills_list"], list)

    def test_experience_parsed(self):
        result = parse_resume_text("I have 4 years of experience in Java")
        assert result["experience_years"] == 4.0

    def test_education_parsed(self):
        result = parse_resume_text("B.Tech graduate with Python skills")
        assert result["education_level"] == "Bachelors"


class TestParseJobDescription:

    def test_returns_required_fields(self):
        jd_text = "We need a Python developer with 2 years experience in Flask and MySQL"
        result = parse_job_description(jd_text, "Backend Dev")
        assert "raw_text"        in result
        assert "required_skills" in result
        assert "experience_req"  in result
        assert "skills_list"     in result

    def test_experience_in_output(self):
        result = parse_job_description("Minimum 3 years of experience required", "Dev")
        assert "3" in result["experience_req"]

    def test_no_experience_mentioned(self):
        result = parse_job_description("We need Python and React skills", "Dev")
        assert result["experience_req"] == ""


class TestSanitizeText:

    def test_strips_whitespace(self):
        assert sanitize_text("  hello  ") == "hello"

    def test_truncates_to_max_len(self):
        long_text = "a" * 9000
        result = sanitize_text(long_text, max_len=8000)
        assert len(result) == 8000

    def test_empty_string(self):
        assert sanitize_text("") == ""

    def test_none_returns_empty(self):
        assert sanitize_text(None) == ""
