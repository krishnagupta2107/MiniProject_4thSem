# AI-Powered Resume-Job Matching & Hiring Intelligence System

A highly rigorous, dual-engine (NLP + LLM) platform built to match candidates to Job Descriptions intelligently, strictly penalizing vague keyword-stuffing and rewarding deep, implicitly required technical skills. Built collaboratively by **Krishna Gupta, Anushka Bansal, and Mahak Bhatia**.

## 🔥 Project Highlights & "Wow" Factors
*   **Dual-Layer Matcher:** Fuses strict mathematical metrics (TF-IDF keyword overlap + Experience scaling) with **SpaCy Cosine Similarity**.
*   **Gemini Implicit Reasoning:** Augments rudimentary Job Descriptions natively by pinging the Gemini LLM during Job Uploads to derive hidden architectural requirements. 
*   **Actionable Candidate Feedback:** Generates contextual feedback for "Rejected" or "Maybe" candidates indicating exactly what architectural skills they must learn.
*   **Skill Distribution Radar Charts:** Highly visual, analytical frontend built on Vanilla JS and Bootstrap 5 to cleanly report the intersection of required vs. owned skills.
*   **Serverless DB:** Powered completely by Google Firestore for seamless scalability.

## 📥 Setup & Installation

### 1. Requirements
*   Python 3.9+
*   Google Firebase Service Account (`credentials.json`)
*   Gemini API Key

### 2. Environment Variables (.env)
Create a `.env` file at the root:
```env
FLASK_SECRET_KEY=your_secure_secret
FIREBASE_CREDENTIALS=credentials.json
GEMINI_API_KEY=your_gemini_project_key
```

### 3. Quick Start
```bash
# Install dependencies
pip install -r requirements.txt

# Download the massive SpaCy NLP model locally
python -m spacy download en_core_web_md

# Boot the application
flask run
```

## 🔒 Production-Grade Security Enforcements
*   **JWT Backend Validation:** All Google Firebase authorizations are actively verified cryptographically in the backend natively via `firebase-admin` rather than trusting arbitrary frontend cookies.
*   **Werkzeug Cryptography:** Native username/password authentication strictly hashes strings off memory using `generate_password_hash`.
*   **Algorithmic Sanitization:** Every single file parsed is explicitly run through truncation sequences (`sanitize_text()`) to natively block code-injection and large heap-overflow payloads before passing into the DB or LLM.

## 🛠 Tech Stack
| Component | Technology | Description |
| :--- | :--- | :--- |
| **Backend** | Flask (Python) | Modular monolithic framework. |
| **Logic Core** | SpaCy, Regex | Drives the strict mathematical heuristic text processing. |
| **Generative LLM** | Google Gemini Flash | Extracts implicit hidden job skills natively. |
| **Database** | Google Firestore | Highly scalable NoSQL Database. |
| **Frontend** | Jinja2, Bootstrap 5, Chart.js | Renders complex scoring visuals intuitively. |

## 🏗 Architecture
See `ARCHITECTURE.md` for full Data Flow and System Schematics.

---
*Built for Academic Evaluation and High-Performance Utility.*
