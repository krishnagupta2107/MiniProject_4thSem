import re

try:
    import spacy
    nlp = spacy.load("en_core_web_md")
except Exception:
    nlp = None

def extract_email(text):
    match = re.search(r'[\w\.-]+@[\w\.-]+', text)
    return match.group(0) if match else None

def extract_phone(text):
    match = re.search(r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}', text)
    return match.group(0) if match else None

def extract_links(text):
    links = re.findall(r'(https?://(?:www\.)?(?:linkedin\.com|github\.com)[^\s]+)', text)
    return list(set(links))

def extract_entities(text):
    if not nlp:
        return {"companies": [], "names": []}
    
    # Process only first 2000 chars to save CPU time on huge resumes
    doc = nlp(text[:2000])
    companies = set()
    names = set()
    
    for ent in doc.ents:
        # Filter out common false positive ORGs like "GPA", "Degree"
        if ent.label_ == "ORG" and len(ent.text) > 2:
            companies.add(ent.text.strip())
        elif ent.label_ == "PERSON" and len(ent.text.split()) >= 2:
            names.add(ent.text.strip())
            
    return {
        "companies": list(companies)[:5],
        "names": list(names)[:3]
    }
