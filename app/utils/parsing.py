"""
parsing_utils.py
Handles extracting text from uploaded files and pulling out
skills, experience, education, and candidate name.
"""

import os
import re

ALLOWED_EXTENSIONS = {"pdf", "doc", "docx", "txt"}


def allowed_file(filename: str) -> bool:
    """Return True if the file extension is in the allowed set (pdf, doc, docx, txt)."""
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


# file padhne ka code

def _read_pdf(filepath: str) -> str:
    """Extract all text from a PDF file using PyPDF2. Returns error string on failure."""
    try:
        import PyPDF2
        pages = []
        with open(filepath, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                text = page.extract_text()
                if text:
                    pages.append(text)
        return "\n".join(pages)
    except Exception as e:
        return f"[PDF parse error: {e}]"


def _read_docx(filepath: str) -> str:
    """Extract all paragraph text from a .docx file using python-docx."""
    try:
        from docx import Document
        doc = Document(filepath)
        return "\n".join(p.text for p in doc.paragraphs if p.text.strip())
    except Exception as e:
        return f"[DOCX parse error: {e}]"


def _read_txt(filepath: str) -> str:
    """Read a plain text file, ignoring encoding errors."""
    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
        return f.read()


def extract_text_from_file(filepath: str) -> str:
    """Dispatch to the appropriate reader based on file extension and return raw text."""
    ext = os.path.splitext(filepath)[1].lower()
    if ext == ".pdf":
        return _read_pdf(filepath)
    if ext in (".docx", ".doc"):
        return _read_docx(filepath)
    return _read_txt(filepath)


# skill nikalne ka code

# category wise skill easy padega
SKILLS_DB = {
    "languages": [
        "python", "java", "javascript", "typescript", "c++", "c", "go", "rust",
        "php", "ruby", "kotlin", "swift",
    ],
    "web_backend": [
        "flask", "django", "fastapi", "spring", "express", "node", "nodejs",
        "rest", "graphql", "microservices",
    ],
    "web_frontend": [
        "react", "vue", "angular", "html", "css", "bootstrap", "tailwind",
        "jquery", "webpack",
    ],
    "databases": [
        "mysql", "postgresql", "sqlite", "mongodb", "redis", "elasticsearch",
        "firebase", "sql",
    ],
    "ml_data": [
        "machine learning", "deep learning", "nlp", "computer vision",
        "pandas", "numpy", "scikit-learn", "sklearn", "tensorflow", "pytorch",
        "keras", "matplotlib", "seaborn", "spacy", "nltk",
    ],
    "cloud_devops": [
        "docker", "kubernetes", "aws", "gcp", "azure", "linux", "git",
        "github", "gitlab", "ci cd", "jenkins", "ansible", "terraform",
    ],
    "soft": [
        "agile", "scrum", "jira", "communication", "teamwork", "leadership",
    ],
}

ALL_SKILLS = [skill for group in SKILLS_DB.values() for skill in group]


def extract_skills(text: str) -> list:
    """
    Scan text for known technical and soft skills from the SKILLS_DB dictionary.

    Uses word-boundary regex to avoid partial matches (e.g. 'c' inside 'cisco').

    Args:
        text (str): Raw document text.

    Returns:
        list: Sorted list of unique matched skill strings in lowercase.
    """
    text_lower = text.lower()
    text_clean = re.sub(r"[^\w\s\+\#\/\.]", " ", text_lower)
    text_clean = re.sub(r"\s+", " ", text_clean).strip()

    found = []
    for skill in ALL_SKILLS:
        pattern = r"(?<!\w)" + re.escape(skill) + r"(?!\w)"
        if re.search(pattern, text_clean):
            found.append(skill)

    return sorted(set(found))


# baaki cheezein extract

def extract_experience_years(text: str) -> float:
    """Look for patterns like '3 years', '2+ years', etc."""
    patterns = [
        r"(\d+\.?\d*)\s*\+?\s*years?",
        r"(\d+\.?\d*)\s*yrs?",
    ]
    for pattern in patterns:
        m = re.search(pattern, text.lower())
        if m:
            return float(m.group(1))
    return 0.0


def extract_education_level(text: str) -> str:
    """
    Detect the highest education level mentioned in the given text.

    Returns one of: 'PhD', 'Masters', 'Bachelors', 'Diploma', or '' if none found.
    """
    t = text.lower()
    if "phd" in t or "doctor" in t:
        return "PhD"
    if any(k in t for k in ["master", "m.tech", "mtech", "mca", "m.sc", "msc", "m.e"]):
        return "Masters"
    if any(k in t for k in ["b.tech", "btech", "b.e", "bsc", "b.sc", "bachelor", "b.ca", "bca"]):
        return "Bachelors"
    if "diploma" in t:
        return "Diploma"
    return ""


def extract_candidate_name(text: str) -> str:
    """
    Super basic name extraction - grabs the first short line that starts with
    a capital letter and doesn't look like a section header.
    Not perfect but works for most standard resumes.
    """
    skip_words = {"resume", "cv", "curriculum", "vitae", "profile", "summary"}
    for line in text.strip().splitlines():
        line = line.strip()
        if not line:
            continue
        words = line.split()
        if 1 < len(words) <= 5 and line[0].isupper():
            if not any(w in line.lower() for w in skip_words):
                return line
    return "Unknown"


# main functions

def parse_resume_file(filepath: str) -> dict:
    """
    Parse a resume from an uploaded file (PDF, DOCX, or TXT).

    Returns a dict with 'error' key if the file could not be read,
    otherwise returns the full resume data dict from _build_resume_dict.
    """
    raw = extract_text_from_file(filepath)
    if raw.startswith("["):
        return {"error": raw, "raw_text": ""}
    return _build_resume_dict(raw)


def parse_resume_text(text: str) -> dict:
    """
    Parse a resume from raw pasted text input.

    Strips whitespace and delegates to _build_resume_dict for full extraction.
    """
    return _build_resume_dict(text.strip())


def parse_job_description(text: str, title: str = "Job") -> dict:
    """
    Parse a job description and extract required skills and experience.

    First performs keyword-based extraction via extract_skills(), then
    optionally augments with Gemini LLM to surface implicit skill requirements.

    Args:
        text  (str): Raw job description text.
        title (str): Job title for metadata context.

    Returns:
        dict: Contains 'raw_text', 'required_skills' (CSV), 'experience_req',
              and 'skills_list' (list of strings).
    """
    text = text.strip()
    base_skills = extract_skills(text)
    
    try:
        from app.services.ai_service import extract_job_skills_with_llm
        skills = extract_job_skills_with_llm(text, base_skills)
    except Exception:
        skills = base_skills
        
    exp = extract_experience_years(text)
    return {
        "raw_text":        text,
        "title":           title,
        "required_skills": ", ".join(skills),
        "experience_req":  f"{exp}+ yrs" if exp else "",
        "skills_list":     skills,
    }


def _build_resume_dict(raw_text: str) -> dict:
    """
    Run the full NLP extraction pipeline on raw resume text.

    Extracts: skills, experience years, education level, and candidate name.

    Returns:
        dict with keys: raw_text, candidate_name, extracted_skills (CSV),
        experience_years (float), education_level (str), skills_list (list).
    """
    skills  = extract_skills(raw_text)
    exp     = extract_experience_years(raw_text)
    edu     = extract_education_level(raw_text)
    name    = extract_candidate_name(raw_text)
    return {
        "raw_text":         raw_text,
        "candidate_name":   name,
        "extracted_skills": ", ".join(skills),
        "experience_years": exp,
        "education_level":  edu,
        "skills_list":      skills,
    }


def sanitize_text(value: str, max_len: int = 8000) -> str:
    """Clean and truncate user-submitted text fields."""
    if not value:
        return ""
    return value.strip()[:max_len]
