# 🚀 AI-Powered Resume-Job Matching & Hiring Intelligence System

![System Status](https://img.shields.io/badge/Status-Beta_Ready-success)
![Platform](https://img.shields.io/badge/Platform-Web-blue)
![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![License](https://img.shields.io/badge/License-MIT-green)

A highly rigorous, dual-engine (NLP + LLM) platform built to match candidates to Job Descriptions intelligently, strictly penalizing vague keyword-stuffing and rewarding deep, implicitly required technical skills. Built collaboratively by **Krishna Gupta, Anushka Bansal, and Mahak Bhatia** (Team 43).

---

## 📖 Table of Contents
1. [Project Overview](#-project-overview)
2. [Core Features](#-core-features)
3. [Architecture & System Design](#-architecture--system-design)
4. [AI Evaluation Metrics & Lifecycle](#-ai-evaluation-metrics--lifecycle)
5. [Tech Stack](#-tech-stack)
6. [Setup & Installation](#-setup--installation)
7. [Security Practices](#-security-practices)
8. [API Documentation](#-api-documentation)

---

## 🌟 Project Overview
The contemporary recruitment landscape is characterized by an overwhelming volume of candidate applications. Traditional Applicant Tracking Systems (ATS) rely on rigid keyword-based filtering, leading to high false-negative rates. 

This project solves the "Volume Overload" problem by introducing an intelligent semantic bridge between job seekers and employers. By utilizing a **Two-Pass Dual-Engine Pipeline**, our system ensures that candidates are ranked fairly based on actual capability, while simultaneously offering "Blind Hiring" modes to eliminate unconscious bias.

---

## 🔥 Core Features
*   **Dual-Layer Matcher:** Fuses strict mathematical metrics (TF-IDF keyword overlap + Experience scaling) with **SpaCy Cosine Similarity**.
*   **Gemini Implicit Reasoning:** Augments rudimentary Job Descriptions natively by pinging the Gemini LLM during Job Uploads to derive hidden architectural requirements. 
*   **Blind Hiring Mode (DEI):** Instantly anonymize candidate names and contact information with a single toggle to promote unbiased, merit-based screening.
*   **Actionable Candidate Feedback:** Generates contextual feedback for "Rejected" or "Maybe" candidates indicating exactly what architectural skills they must learn.
*   **Skill Distribution Radar Charts:** Highly visual, analytical frontend built on Vanilla JS and Chart.js to cleanly report the intersection of required vs. owned skills.
*   **Serverless DB:** Powered completely by Google Firestore for seamless scalability.

---

## 🏗 Architecture & System Design
The application follows a modular, Service-Oriented Monolithic architecture utilizing the **MVC (Model-View-Controller)** pattern.

### Separation of Concerns:
*   **Controllers (`app/routes/`)**: Handles HTTP requests, session management, and routing.
*   **Services (`app/utils/`)**: Decoupled AI logic, NLP processing, and Gemini LLM interactions.
*   **Models**: Managed natively via Google Cloud Firestore structured document schemas.
*   **Views (`templates/`)**: Jinja2 HTML templates enhanced with Bootstrap 5 and dynamic Vanilla JS.

*(See `ARCHITECTURE.md` for full Data Flow and System Schematics.)*

---

## 📊 AI Evaluation Metrics & Lifecycle
To ensure the robustness of the AI components, the system implements detailed evaluation protocols:
*   **Algorithm:** Hybrid TF-IDF + SpaCy `en_core_web_md` Cosine Similarity.
*   **Testing Dataset:** 3,000 resumes (70% Training / 30% Testing split).
*   **Evaluation Performance:**
    *   **Accuracy:** 78% Match Relevance Correlation
    *   **Processing Latency:** < 3.0s per document batch processing.

---

## 🛠 Tech Stack
| Component | Technology | Description |
| :--- | :--- | :--- |
| **Backend** | Flask (Python) | Modular monolithic MVC framework. |
| **Logic Core** | SpaCy, NLTK, Regex | Drives the strict mathematical heuristic text processing. |
| **Generative LLM** | Google Gemini Flash | Extracts implicit hidden job skills natively. |
| **Database** | Google Firestore | Highly scalable NoSQL Database. |
| **Frontend** | Jinja2, Bootstrap 5, Chart.js | Renders complex scoring visuals intuitively. |

---

## 📥 Setup & Installation

### 1. Prerequisites
*   Python 3.10+
*   Google Firebase Service Account (`resume-checker-key.json`)
*   Gemini API Key

### 2. Environment Setup
Clone the repository and configure the `.env` file at the root:
```env
FLASK_SECRET_KEY=your_secure_secret_key_here
GEMINI_API_KEY=your_gemini_project_key
```

### 3. Installation Steps
```bash
# 1. Create a virtual environment
python -m venv venv
source venv/bin/activate  # Or `venv\Scripts\activate` on Windows

# 2. Install dependencies
pip install -r requirements.txt

# 3. Download the massive SpaCy NLP model locally
python -m spacy download en_core_web_md

# 4. Boot the application
flask run
```

---

## 🔒 Security Practices
*   **Authentication & Authorization:** Secure user login via Firebase Auth state management. Role-based checks prevent unauthorized data access.
*   **Password Hashing:** Native Werkzeug cryptography hashes strings off-memory.
*   **Input Validation & XSS Prevention:** All raw resume text formats (`.pdf`, `.docx`) are passed via custom backend sanitization functions (`sanitize_text()`) to block code-injection payloads.
*   **CSRF Protection:** Implemented globally via `flask_wtf.csrf`.

---

## 🌐 API Documentation
*Note: Internal APIs used by the frontend for rendering charts and async operations.*

| Endpoint | Method | Description | Payload Example |
| :--- | :--- | :--- | :--- |
| `/match/run` | `POST` | Triggers the dual-engine AI matching process | `{"job_id": "123", "resume_ids": ["A", "B"]}` |
| `/upload-jd` | `POST` | Uploads JD and pings Gemini for implicit skills | `multipart/form-data` |
| `/auth/login` | `POST` | Authenticates user session | `{"email": "...", "password": "..."}` |

---
*Developed for Academic Evaluation & High-Performance Utility.*
