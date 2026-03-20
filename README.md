# HireMatch – AI Resume–Job Matching System

🚀 **Live Demo:** [https://resume-matcher-c8de.onrender.com](https://resume-matcher-c8de.onrender.com)

**Project 77 | Team 43 | 4th Semester Mini Project**

A Flask web application that automates resume screening using NLP-based skill extraction and a weighted matching algorithm.

## Features

- Upload resumes (PDF, DOCX, TXT) or paste text directly
- Paste job descriptions — skills are auto-extracted
- Score resumes against jobs with a TF-IDF weighted algorithm & SpaCy Deep NLP 
- Ranked results with Shortlisted / Maybe / Rejected labels
- Actionable candidate feedback to help users improve their match scores
- User authentication and database using Firebase & Firestore
- Admin dashboard for system stats
- Responsive, glassmorphic premium UI
- CSRF protection on all forms
- Rate limiting on uploads and matching

## Tech Stack

| Layer      | Technology |
|------------|-----------|
| Backend    | Python, Flask |
| Auth       | Firebase Authentication & Flask-Login |
| Database   | Google Cloud Firestore (Firebase) |
| Parsing    | PyPDF2, python-docx, spaCy |
| Frontend   | Custom CSS (Glassmorphism), Bootstrap 5, Chart.js |

## Project Structure

```
├── app/
│   ├── __init__.py          # App factory & Firebase init
│   ├── models/
│   │   ├── user.py
│   │   ├── resume.py
│   │   ├── job.py
│   │   └── match.py
│   ├── routes/
│   │   ├── auth.py          # Login, register, logout 
│   │   ├── main.py          # Dashboard, index
│   │   ├── resume.py        # Resume upload, viewing, & deletion
│   │   ├── job.py           # JD upload, viewing, & deletion
│   │   ├── match.py         # Matching, scoring, feedback + results
│   │   ├── admin.py         # Admin panel
│   │   └── api.py           # JSON API
│   └── utils/
│       ├── parsing.py       # Regex & Spacy skill extraction
│       ├── matching.py      # TF-IDF & Spacy scoring logic
│       └── helpers.py       # Rate limiter, decorators
├── templates/               # Jinja2 HTML templates
├── static/                  # CSS (style.css) and JS (main.js)
├── render.yaml              # Render deployment blueprint
├── requirements.txt         # Python dependencies
└── wsgi.py                  # Prod entrypoint
```

## Quick Start (Local Development)

```bash
# 1. Clone the repository
git clone https://github.com/krishnagupta2107/MiniProject_4thSem.git
cd MiniProject_4thSem

# 2. Set up virtual environment
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate

# 3. Install dependencies and the SpaCy model
pip install -r requirements.txt

# 4. Set up Environment Variables
# Create a `.env` file in the root directory and add your Firebase credentials:
# FIREBASE_API_KEY="..."
# FIREBASE_JSON='{...}' 
# SECRET_KEY="..."

# 5. Run the app
flask run
```
Open `http://localhost:5000` in your browser.

## Matching Algorithm

Scores are calculated using a blend of heuristic and semantic approaches:

- **Semantic Similarity (50%)** — Deep NLP word-vector comparisons using spaCy between candidates and requirements.
- **Skill Overlap (40%)** — TF-IDF boosted exact-match evaluation of parsed skills (rarer skills are weighted higher).
- **Experience Match (10%)** — Does the candidate meet or exceed the year requirement?

Labels: **Shortlisted** (≥70) | **Maybe** (45–69) | **Rejected** (<45)
