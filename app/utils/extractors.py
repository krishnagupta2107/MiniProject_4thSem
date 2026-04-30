"""
extractors.py
Low-level text extraction utilities used during resume parsing.

Provides regex-based and SpaCy NER-based extraction of:
  - Email addresses
  - Phone numbers
  - LinkedIn/GitHub profile links
  - Named entities (companies, person names)
"""

import re

try:
    import spacy
    nlp = spacy.load("en_core_web_md")
except Exception:
    nlp = None

def extract_email(text: str) -> str | None:
    """Extract the first email address found in the given text using regex."""
    match = re.search(r'[\w\.-]+@[\w\.-]+', text)
    return match.group(0) if match else None

def extract_phone(text: str) -> str | None:
    """Extract the first US/India-formatted phone number found in the given text."""
    match = re.search(r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}', text)
    return match.group(0) if match else None

def extract_links(text: str) -> list:
    """Extract all LinkedIn and GitHub profile URLs from the given text."""
    links = re.findall(r'(https?://(?:www\.)?(?:linkedin\.com|github\.com)[^\s]+)', text)
    return list(set(links))

def extract_entities(text: str) -> dict:
    """
    Use SpaCy Named Entity Recognition to identify organizations and person names.

    Processes only the first 2000 characters to limit CPU usage on large documents.

    Args:
        text (str): Raw resume or document text.

    Returns:
        dict: {
            'companies': list of up to 5 organization names,
            'names':     list of up to 3 person names (2+ word entities only)
        }
    """
    if not nlp:
        return {"companies": [], "names": []}
    
    doc = nlp(text[:2000])  # limit to 2000 chars to save CPU
    companies = set()
    names = set()
    
    for ent in doc.ents:
        if ent.label_ == "ORG" and len(ent.text) > 2:
            companies.add(ent.text.strip())
        elif ent.label_ == "PERSON" and len(ent.text.split()) >= 2:
            names.add(ent.text.strip())
            
    return {
        "companies": list(companies)[:5],
        "names": list(names)[:3]
    }
