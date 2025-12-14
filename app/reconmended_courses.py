from fastapi import APIRouter, UploadFile, File, Form
from PyPDF2 import PdfReader
import requests
import re

router = APIRouter()

# --- UDEMY API CONFIG (new working one) ---
UDEMY_API_URL = "https://paid-udemy-course-for-free.p.rapidapi.com/"
API_KEY = "cc1ad1ef15msh8c8d7c4ac148bf3p13ab85jsn3d8cade8bee2"  # your working key

HEADERS = {
    "x-rapidapi-key": API_KEY,
    "x-rapidapi-host": "paid-udemy-course-for-free.p.rapidapi.com"
}

# --- Helper: Extract text from resume ---
def extract_text_from_pdf(file: UploadFile):
    try:
        reader = PdfReader(file.file)
        text = "\n".join([page.extract_text() or "" for page in reader.pages])
        return text.strip()
    except Exception as e:
        print("PDF extraction failed:", e)
        return ""

# --- Helper: Extract skills from resume text ---
def extract_skills(text: str):
    lines = [line.lower() for line in text.split("\n") if line.strip()]
    skills = []
    for line in lines:
        if any(k in line for k in ["skills", "coursework", "framework", "language"]):
            skills.extend(re.findall(r"[a-zA-Z\+\#]+", line.lower()))
    return list(set(skills))

# --- Skill mapping by domain ---
DOMAIN_SKILLS = {
    "ai": ["machine learning", "deep learning", "pytorch", "nlp", "computer vision"],
    "ml": ["machine learning", "supervised learning", "unsupervised learning", "tensorflow"],
    "data": ["data analysis", "pandas", "numpy", "sql", "statistics"],
    "web": ["html", "css", "javascript", "react", "nodejs"],
    "cloud": ["aws", "azure", "gcp", "docker", "kubernetes"]
}

# --- Route: Recommend courses ---
@router.post("/recommend-courses")
async def recommend_courses(
    file: UploadFile = File(...),
    domain: str = Form(...)
):
    text = extract_text_from_pdf(file)
    if not text:
        return {"success": False, "message": "Could not extract text from resume"}

    extracted_skills = extract_skills(text)
    target_skills = DOMAIN_SKILLS.get(domain.lower(), [])
    missing_skills = [s for s in target_skills if s not in extracted_skills]

    all_courses = []
    try:
        # Fetch from the new Udemy API
        response = requests.get(UDEMY_API_URL, headers=HEADERS, params={"page": 0})
        if response.status_code == 200:
            data = response.json()
            # Filter only courses that match missing skills
            for skill in missing_skills:
                matched = [course for course in data if skill.lower() in course["title"].lower()]
                all_courses.extend(matched)
    except Exception as e:
        print("API error:", e)

    return {
        "success": True,
        "extracted_skills": extracted_skills,
        "missing_skills": missing_skills,
        "courses": all_courses[:10] if all_courses else [],
    }
