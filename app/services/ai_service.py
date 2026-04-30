"""
services/ai_service.py
Google Gemini 1.5 Flash integration for job skill expansion and project-based resume auditing.
"""

import os
import json
import google.generativeai as genai
from flask import current_app

def _get_gemini_model():
    """Initializes the Gemini model using the API key from Flask Config."""
    api_key = current_app.config.get("GEMINI_API_KEY")
    if not api_key:
        return None
    genai.configure(api_key=api_key)
    # Use gemini-1.5-flash for fast and complex reasoning at scale
    model = genai.GenerativeModel("gemini-1.5-flash")
    return model

from typing import List, Optional

def extract_job_skills_with_llm(jd_text: str, base_skills: List[str]) -> List[str]:
    """
    Uses Gemini to strictly identify both explicit and implicit core technical skills from the Job Description.
    Returns: list of string skill names natively matched to standard formats.
    """
    model = _get_gemini_model()
    if not model:
        return base_skills

    prompt = f"""
I am parsing a Job Description. I have already found the following technical skills: {', '.join(base_skills)}

Job Description:
```
{jd_text}
```

Task:
Read the Job Description. Return a JSON array of strings containing up to 10 additional, non-trivial MISSING technical skills (languages, frameworks, essential tooling) strictly required or highly recommended by the text. Return them entirely in lowercase.
If no extra skills are found beyond the base skills, return an empty array [].
Respond ONLY with the JSON array format, e.g. ["docker", "typescript", "kubernetes"].
"""
    try:
        response = model.generate_content(prompt)
        text = response.text.strip()
        if text.startswith("```json"):
            text = text[7:]
        if text.endswith("```"):
            text = text[:-3]
            
        extra_skills = json.loads(text)
        if isinstance(extra_skills, list):
            # clean and merge
            combined = set(base_skills)
            for skill in extra_skills:
                trimmed = str(skill).strip().lower()
                if len(trimmed) > 1 and len(trimmed) < 25:
                    combined.add(trimmed)
            return sorted(list(combined))
        return base_skills
    except Exception as e:
        current_app.logger.error(f"Gemini Skill Extraction Error: {e}")
        return base_skills

def evaluate_candidate_with_llm(resume_text, jd_text, required_skills, candidate_skills, base_nlp_score):
    """
    Evaluates a resume against a JD using Gemini.
    Returns None if LLM is unavailable or fails, triggering a fallback.
    Returns a dict with: 'score', 'label', 'feedback', 'missing_skills'
    """
    model = _get_gemini_model()
    if not model:
        current_app.logger.warning("No GEMINI_API_KEY found. Falling back to base matcher.")
        return None

    prompt = f"""
You are an extremely strict, senior Technical HR Recruiter. 
Your task is to take an initial algorithmic base score of {base_nlp_score:.2f}/100 and STRICLY review it.
The base score was calculated using Spacy NLP and keyword frequency matching. You must now act as the human filter to deduct points based on REAL project quality.

Candidate Resume Text:
```
{resume_text}
```

Job Description Text:
```
{jd_text}
```

Required Skills Context: {', '.join(required_skills)}

Instructions:
1. Examine the candidate's actual projects and experience depth.
2. If the candidate just lists skills but has NO relevant projects or poor depth, you MUST DEDUCT heavily from the base score {base_nlp_score:.2f} (e.g. subtract 20-50 points).
3. If their experience is a perfect match, you may maintain or slightly boost the score.
4. Provide highly specific, strict, actionable feedback. 

Respond ONLY with a valid JSON object matching this schema:
{{
  "score": <Number (float) from 0-100 representing the STRICT finalized project-audited score>,
  "label": <String: "Shortlisted" if score >= 70, "Maybe" if >= 45, else "Rejected">,
  "missing_skills": [<String array of required skills they lack practical experience with>],
  "feedback": <String: Strict, actionable explanation. Format using <br> and <strong> tags>
}}
"""

    try:
        response = model.generate_content(prompt)
        text = response.text.strip()
        if text.startswith("```json"):
            text = text[7:]
        if text.endswith("```"):
            text = text[:-3]
            
        result = json.loads(text)
        
        required_keys = ["score", "label", "missing_skills", "feedback"]
        if all(k in result for k in required_keys):
            # Ensure score is a float
            result["score"] = float(result["score"])
            return result
        else:
            current_app.logger.error("LLM Schema Mismatch")
            return None
    except Exception as e:
        current_app.logger.error(f"Gemini API Error: {e}")
        return None
