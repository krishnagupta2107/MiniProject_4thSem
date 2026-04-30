# 🚀 AI-Powered Resume–Job Matching & Hiring Intelligence System

![System Status](https://img.shields.io/badge/Status-Beta_Ready-success)
![Platform](https://img.shields.io/badge/Platform-Web-blue)
![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![Flask](https://img.shields.io/badge/Framework-Flask-red)
![Firebase](https://img.shields.io/badge/Database-Firestore-orange)
![License](https://img.shields.io/badge/License-MIT-green)
![Tests](https://img.shields.io/badge/Tests-Pytest-yellow)

🌍 **Live Deployment:** [https://resume-matcher-c8de.onrender.com/](https://resume-matcher-c8de.onrender.com/)

> An intelligent, dual-engine (NLP + LLM) hiring platform that fairly matches candidates to job descriptions using SpaCy semantic analysis and Google Gemini AI — with built-in evaluation metrics, blind hiring mode, and role-based access control.

**Team 43** — Krishna Gupta, Anushka Bansal, Mahak Bhatia

---

## 📖 Table of Contents
1. [Problem Statement](#-problem-statement)
2. [Core Features](#-core-features)
3. [Tech Stack](#-tech-stack)
4. [Architecture & System Design](#-architecture--system-design)
5. [AI Evaluation Metrics](#-ai-evaluation-metrics--lifecycle)
6. [Setup & Installation](#-setup--installation)
7. [How to Run](#-how-to-run)
8. [API Documentation](#-api-documentation)
9. [Security Practices](#-security-practices)
10. [Project Structure](#-project-structure)
11. [Running Tests](#-running-tests)

---

## 🎯 Problem Statement

Traditional Applicant Tracking Systems (ATS) rely on rigid keyword-based filtering, leading to high false-negative rates and unconscious bias. This system solves the **"Volume Overload"** problem by introducing an intelligent semantic bridge between job seekers and employers, ranking candidates based on actual capability rather than keyword frequency.

---

## 🔥 Core Features

| Feature | Description |
|---|---|
| **Dual-Layer Matcher** | Fuses TF-IDF keyword overlap + SpaCy cosine similarity for robust scoring |
| **Gemini Skill Extraction** | Uses Google Gemini Flash to derive implicit hidden job requirements from JD text |
| **Blind Hiring Mode** | Anonymizes candidate identity for unbiased, DEI-compliant screening |
| **Evaluation Metrics** | Reports Precision, Recall, and F1-Score per match |
| **Model Lifecycle Tracking** | Logs all match evaluations to `instance/model_logs/` for auditability |
| **Actionable Feedback** | Tells "Maybe"/"Rejected" candidates exactly which skills to learn |
| **Role-Based Access Control** | Admin users can manage all data; recruiters manage their own |
| **API Key-Protected REST API** | JSON endpoints for external integrations |
| **CSRF Protection** | All forms protected via Flask-WTF |
| **Rate Limiting** | In-memory per-IP rate limiting on all submission endpoints |

---

## 🛠 Tech Stack

| Layer | Technology | Purpose |
|---|---|---|
| **Backend** | Flask (Python) | MVC web framework |
| **NLP Engine** | SpaCy `en_core_web_md` | Cosine similarity & entity extraction |
| **LLM** | Google Gemini 1.5 Flash | Implicit skill extraction from JDs |
| **Database** | Google Firestore (NoSQL) | Serverless, scalable document storage |
| **Auth** | Firebase Auth + Flask-Login | Google SSO + email/password sessions |
| **Frontend** | Jinja2 + Bootstrap 5 + Chart.js | Responsive UI with skill distribution charts |
| **Testing** | Pytest + MockFirestore | Unit tests without real DB dependency |
| **Deployment** | Render.com | Cloud hosting via `render.yaml` |

---

## 🏗 Architecture & System Design

The application follows the **MVC (Model-View-Controller)** pattern with a Service Layer for AI logic.

```
app/
├── routes/          # Controllers — HTTP request handling
│   ├── auth.py      # Login, register, Google OAuth
│   ├── resume.py    # Resume upload & management
│   ├── job.py       # Job description CRUD
│   ├── match.py     # AI matching pipeline
│   ├── admin.py     # Admin panel & metrics dashboard
│   └── api.py       # REST API endpoints (API-key protected)
├── models/          # Firestore data models
│   ├── user.py
│   ├── resume.py
│   ├── job.py
│   └── match.py
├── services/        # Business logic / AI services
│   ├── match_service.py      # Scoring algorithm (Precision/Recall/F1)
│   ├── ai_service.py         # Gemini LLM integration
│   └── model_lifecycle.py    # Metrics logging & version tracking
└── utils/           # Shared helpers
    ├── parsing.py   # Resume/JD NLP parsing
    ├── extractors.py # Email, phone, entity extraction
    └── helpers.py   # Rate limiter, admin decorator
```

*(See `ARCHITECTURE.md` for full Data Flow and System Schematics.)*

---

## 📊 AI Evaluation Metrics & Lifecycle

Every match run calculates and logs:

- **Precision** — of all resumes predicted as relevant, what fraction truly were
- **Recall** — of all truly relevant resumes, what fraction were found
- **F1-Score** — harmonic mean of precision and recall

Metrics are tracked per-run in `instance/model_logs/evaluation_metrics.jsonl` by the `ModelLifecycleManager`. The admin panel at `/admin/metrics` visualises these live.

| Metric | Formula | Value Range |
|---|---|---|
| Precision | matched / candidate_skills | 0.0 – 1.0 |
| Recall | matched / required_skills | 0.0 – 1.0 |
| F1 Score | 2 × (P × R) / (P + R) | 0.0 – 1.0 |

---

## 📥 Setup & Installation

### Prerequisites
- Python 3.10+
- A Google Firebase project with Firestore enabled
- Firebase service account key (`resume-checker-key.json`)
- Google Gemini API Key

### 1. Clone the Repository
```bash
git clone https://github.com/krishnagupta2107/MiniProject_4thSem.git
cd MiniProject_4thSem
```

### 2. Create a Virtual Environment
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Download the SpaCy NLP Model
```bash
python -m spacy download en_core_web_md
```

### 5. Configure Environment Variables
Create a `.env` file at the project root:
```env
SECRET_KEY=your-very-secure-random-secret-key
GEMINI_API_KEY=your-google-gemini-api-key
FLASK_ENV=development
```

Place your Firebase service account JSON as `resume-checker-key.json` in the root directory.

---

## ▶ How to Run

```bash
# Start the development server
python run.py
```

Then open your browser at: **http://127.0.0.1:5000**

**Demo Accounts (auto-seeded on first run):**
| Role | Email | Password |
|---|---|---|
| Recruiter | `recruiter@demo.com` | `demo123` |
| Admin | `admin@demo.com` | `admin123` |

---

## 🌐 API Documentation

All API routes are prefixed with `/api` and require an `X-API-Key` header.

**Header:** `X-API-Key: <your SECRET_KEY value>`

### `POST /api/parse-resume`
Parse raw resume text and extract candidate information.

**Request:**
```json
{ "text": "John Doe | Python Developer | 3 years experience..." }
```

**Response:**
```json
{
  "success": true,
  "data": {
    "candidate_name": "John Doe",
    "skills": ["python", "django", "sql"],
    "experience_years": 3.0,
    "education_level": "B.Tech"
  }
}
```

### `POST /api/parse-jd`
Parse a job description and extract required skills.

**Request:**
```json
{ "text": "Looking for a backend developer with Python and Flask...", "title": "Backend Dev" }
```

**Response:**
```json
{
  "success": true,
  "data": {
    "required_skills": ["python", "flask", "rest api"],
    "experience_req": 2.0
  }
}
```

### `GET /api/resumes`
List all resumes in the system. Requires admin-level API key.

### `GET /api/jobs`
List all job descriptions in the system. Requires admin-level API key.

---

## 🔒 Security Practices

| Practice | Status | Implementation |
|---|---|---|
| Password Hashing | ✅ Active | Werkzeug `generate_password_hash` / `check_password_hash` |
| CSRF Protection | ✅ Active | Flask-WTF `CSRFProtect` on all forms |
| Input Sanitization | ✅ Active | Custom `sanitize_text()` strips HTML/scripts before NLP |
| Rate Limiting | ✅ Active | In-memory per-IP bucket on all upload & match routes |
| Security Headers | ✅ Active | HSTS, X-Frame-Options, X-XSS-Protection via `after_request` |
| Content Security Policy | ✅ Active | Strict CSP allowing only whitelisted CDNs |
| API Authorization | ✅ Active | `X-API-Key` header check on all `/api/*` routes |
| Role-Based Access | ✅ Active | `admin_required` decorator + ownership checks in every route |
| XSS Prevention | ✅ Active | Jinja2 auto-escaping + `sanitize_text()` on all user input |
| CORS Configuration | ✅ Active | `flask-cors` restricts cross-origin to `/api/*` only |

---

## 📂 Project Structure

```
MiniProject_4thSem/
├── app/                    # Main application package
│   ├── __init__.py         # App factory (create_app)
│   ├── models/             # Firestore data model classes
│   ├── routes/             # Flask Blueprints (controllers)
│   ├── services/           # AI/business logic layer
│   └── utils/              # NLP parsing, helpers, extractors
├── templates/              # Jinja2 HTML templates
├── static/                 # CSS, JS, images
├── tests/                  # Pytest unit tests
├── instance/               # Runtime data (model logs)
├── config.py               # App configuration class
├── run.py                  # Development server entry point
├── wsgi.py                 # Production WSGI entry point
├── render.yaml             # Render.com deployment config
├── requirements.txt        # Python dependencies
├── ARCHITECTURE.md         # Detailed system architecture
└── README.md               # This file
```

---

## 🧪 Running Tests

```bash
# Run all tests with verbose output
pytest tests/ -v

# Run only matching logic tests
pytest tests/test_matching.py -v

# Run with coverage report
pytest tests/ --cov=app --cov-report=term-missing
```

---

*Developed for Academic Evaluation — MiniProject 4th Semester, Team 43.*
