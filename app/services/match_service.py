"""
matching.py
Core resume-to-job matching logic.

Scoring breakdown:
  - Skill overlap (80%) : how many required skills the candidate has
  - Coverage bonus (10%): avoids penalizing candidates with extra skills
  - Experience match (10%): does the candidate meet the year requirement
"""

import re
import math
from collections import Counter

from app.utils.extractors import nlp

from app.utils.parsing import extract_experience_years


def score_resume_for_job(resume, jd) -> dict:
    """
    Returns a dict with: score (0-100), label, matched skills, missing skills,
    and a basic explanation so recruiters understand why.
    """
    required = [s.lower() for s in jd.skills_list()]
    candidate = [s.lower() for s in resume.skills_list()]

    req_set  = set(required)
    have_set = set(candidate)

    matched = sorted(req_set & have_set)
    missing = sorted(req_set - have_set)

    # ===== STEP 1: CALCULATE STRICT BASE NLP SCORE =====
    # kitna skill match hua
    if req_set:
        skill_score = len(matched) / len(req_set)
    else:
        skill_score = 0.5   # no skills listed = neutral

    # extra skill walon ko marna mat
    if have_set:
        coverage = len(matched) / len(have_set)
    else:
        coverage = 0.0

    # exp ka hisab
    jd_years  = extract_experience_years(jd.raw_text or "")
    exp_bonus = _check_experience(resume.experience_years, jd_years)

    # spacy se deep nlp lagao
    try:
        if nlp:
            # jaldi ke liye 5000 character fix
            text1 = (jd.raw_text or " ".join(required))[:5000]
            text2 = (resume.raw_text or " ".join(candidate))[:5000]
            doc_jd = nlp(text1)
            doc_res = nlp(text2)
            cosine_sim = doc_jd.similarity(doc_res)
        else:
            cosine_sim = skill_score
    except Exception:
        cosine_sim = skill_score

    semantic_score = float(cosine_sim)

    # 70-20-10 ka strict weightage (prioritize hard skills over fuzzy semantics)
    raw_score = (skill_score * 70.0) + (semantic_score * 20.0) + (exp_bonus * 10.0)
    base_score = round(min(raw_score, 100.0), 2)

    # ===== DETAILED EVALUATION METRICS =====
    precision = coverage
    recall = skill_score
    f1_score = (2 * precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0

    # ===== FINAL SCORE & FALLBACK EXPLANATION =====
    label = _get_label(base_score)
    return {
        "score":   base_score,
        "label":   label,
        "matched": matched,
        "missing": missing,
        "explanation": _build_explanation(base_score, matched, missing, exp_bonus, jd_years),
        "metrics": {
            "precision": round(precision, 2),
            "recall": round(recall, 2),
            "f1_score": round(f1_score, 2)
        }
    }


def _check_experience(candidate_years: float, required_years: float) -> float:
    """Returns 0, 0.5, or 1.0 based on how close the candidate is."""
    if required_years <= 0:
        return 0.5   # not specified
    if candidate_years >= required_years:
        return 1.0
    gap = required_years - candidate_years
    if gap <= 1:
        return 0.5   # close enough
    return 0.0


def _tfidf_boost(matched_skills: list, all_required: list) -> float:
    """
    Give a small boost based on TF-IDF-inspired weighting.
    Skills that appear less often in the overall required list are harder to find,
    so matching them should score higher.
    """
    if not matched_skills or not all_required:
        return 0.0

    freq = Counter(all_required)
    n    = len(all_required)

    score = 0.0
    for skill in matched_skills:
        tf  = freq.get(skill, 1)
        idf = math.log((n + 1) / (tf + 1)) + 1
        score += idf

    # 0 to 1 mein set karo
    max_possible = sum(math.log((n + 1) / (freq.get(s, 1) + 1)) + 1 for s in all_required)
    if max_possible > 0:
        return score / max_possible
    return 0.0


def _get_label(score: float) -> str:
    if score >= 70:
        return "Shortlisted"
    if score >= 45:
        return "Maybe"
    return "Rejected"


def _build_explanation(score, matched, missing, exp_bonus, jd_years) -> str:
    """Give a simple human-readable explanation of the score."""
    parts = []

    if matched:
        parts.append(f"Matched {len(matched)} skill(s): {', '.join(matched[:4])}{'...' if len(matched) > 4 else ''}.")
    else:
        parts.append("No required skills matched.")

    if missing:
        parts.append(f"Missing: {', '.join(missing[:3])}{'...' if len(missing) > 3 else ''}.")

    if jd_years > 0:
        if exp_bonus == 1.0:
            parts.append("Experience requirement met.")
        elif exp_bonus == 0.5:
            parts.append("Experience slightly below requirement.")
        else:
            parts.append("Does not meet experience requirement.")

    return " ".join(parts)
