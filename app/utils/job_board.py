"""
job_board.py
A mock integration module for syncing jobs from third-party boards (e.g., LinkedIn API, Indeed API).
"""
import random

MOCK_TITLES = ["Senior Python Developer", "Data Scientist", "Frontend Engineer (React)"]
MOCK_SKILLS = [
    "Python, Flask, SQL, Docker",
    "Machine Learning, Python, numpy, Pandas, scikit-learn",
    "JavaScript, React, Redux, CSS"
]

def fetch_mock_jobs():
    """Returns a list of mock job dictionaries fetched from an 'external API'."""
    jobs = []
    for _ in range(3):
        idx = random.randint(0, 2)
        jobs.append({
            "title": MOCK_TITLES[idx] + f" (External-{random.randint(100,999)})",
            "required_skills": MOCK_SKILLS[idx],
            "experience_years": random.randint(1, 6),
            "description": "This is a synced job from an external job board. Experience is highly valued."
        })
    return jobs
