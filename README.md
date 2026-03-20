# HireMatch – AI Resume–Job Matching System

**Project 77 | Team 43 | 4th Semester Mini Project**

🚀 **Live Demo:** [https://resume-matcher-c8de.onrender.com](https://resume-matcher-c8de.onrender.com)

A Flask web application that automates resume screening using NLP-based skill extraction and a weighted matching algorithm.

## Features

- Upload resumes (PDF, DOCX, TXT) or paste text directly
- Paste job descriptions — skills are auto-extracted
- Score resumes against jobs with a TF-IDF weighted algorithm
- Ranked results with Shortlisted / Maybe / Rejected labels
- User authentication (login / register)
- Admin dashboard for system stats
- REST API endpoints for external integration
- CSRF protection on all forms
- Rate limiting on uploads and matching
- 30+ unit and integration tests

## Tech Stack

| Layer      | Technology |
|------------|-----------|
| Backend    | Python, Flask |
| Auth       | Flask-Login, Flask-WTF (CSRF) |
| Database   | SQLAlchemy ORM, SQLite |
| Parsing    | PyPDF2, python-docx |
| Frontend   | Bootstrap 5, Font Awesome |
| Testing    | pytest |

## Project Structure

```
├── app/
│   ├── __init__.py          # App factory
│   ├── models/
│   │   ├── user.py
│   │   ├── resume.py
│   │   ├── job.py
│   │   └── match.py
│   ├── routes/
│   │   ├── auth.py          # Login, register, logout
│   │   ├── main.py          # Dashboard, index
│   │   ├── resume.py        # Resume upload/view
│   │   ├── job.py           # JD upload/view
│   │   ├── match.py         # Matching + results
│   │   ├── admin.py         # Admin panel
│   │   └── api.py           # JSON API
│   └── utils/
│       ├── parsing.py       # NLP skill extraction
│       ├── matching.py      # Scoring algorithm
│       └── helpers.py       # Rate limiter, decorators
├── templates/               # Jinja2 HTML templates
├── static/                  # CSS and JS
├── tests/                   # pytest test suite
├── config.py
├── run.py
└── requirements.txt
```

## Quick Start

```bash
# 1. Clone and set up virtual environment
git clone https://github.com/krishnagupta2107/MiniProject_4thSem.git
cd MiniProject_4thSem
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the app
python run.py
```

Open `http://localhost:5000` in your browser.

## Demo Accounts

| Role      | Email                  | Password  |
|-----------|------------------------|-----------|
| Recruiter | recruiter@demo.com     | demo123   |
| Admin     | admin@demo.com         | admin123  |

## Running Tests

```bash
pytest tests/ -v
```

## Matching Algorithm

Scores are calculated as:

- **Skill Overlap (75%)** — how many required skills the candidate has
- **Coverage Bonus (10%)** — avoids penalizing candidates with extra skills
- **Experience Match (10%)** — does candidate meet the year requirement
- **TF-IDF Boost (5%)** — rarer/specialized skills are weighted higher

Labels: **Shortlisted** (≥70) | **Maybe** (45–69) | **Rejected** (<45)

## API Endpoints

| Method | Endpoint         | Description |
|--------|-----------------|-------------|
| POST   | /api/parse-resume | Extract skills from resume text |
| POST   | /api/parse-jd    | Extract skills from JD text |
| GET    | /api/resumes     | List all resumes |
| GET    | /api/jobs        | List all job descriptions |
