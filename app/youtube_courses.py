from fastapi import APIRouter, UploadFile, File, Form
from PyPDF2 import PdfReader
import requests
import re

router = APIRouter(tags=["YouTube Courses"])

# --- YouTube API CONFIG ---
YOUTUBE_API_KEY = "###"
YOUTUBE_API_URL = "###"


# --- Resume text extraction (unchanged, reliable) ---
def extract_text_from_pdf(file: UploadFile) -> str:
    try:
        reader = PdfReader(file.file)
        text = "\n".join([page.extract_text() or "" for page in reader.pages])
        return text.strip()
    except Exception as e:
        print("PDF extraction failed:", e)
        return ""


# --- Skill extraction: same logic as Code 1 ---
def extract_skills(text: str):
    """
    Extracts skills by scanning lines that mention 'skills', 'coursework',
    'framework', or 'language', and collecting words from those lines.
    """
    lines = [line.lower() for line in text.split("\n") if line.strip()]
    skills = []

    for line in lines:
        if any(k in line for k in ["skills", "coursework", "framework", "language"]):
            skills.extend(re.findall(r"[a-zA-Z\+\#]+", line.lower()))

    return list(set(skills))


@router.post("/recommend-youtube-courses")
async def recommend_youtube_courses(
    domain: str = Form(...),
    file: UploadFile = File(...)
):
    """
    Takes a resume and domain, identifies extracted and missing skills,
    and returns YouTube playlists that match those skills.
    """

    # --- Step 1: Extract text & skills (same logic as Code 1) ---
    text = extract_text_from_pdf(file)
    if not text:
        return {"success": False, "message": "Could not extract text from resume"}

    extracted_skills = extract_skills(text)

    # --- Step 2: Domain → required skills ---
    domain_missing_map = {
        "ai": ["machine learning", "deep learning", "neural networks"],
        "ml": ["data preprocessing", "model deployment", "scikit-learn"],
        "data": ["sql", "data visualization", "power bi"],
        "web": ["react", "nodejs", "typescript"],
        "cloud": ["aws", "docker", "kubernetes"],
    }

    target_skills = domain_missing_map.get(domain.lower(), [])
    missing_skills = [s for s in target_skills if s not in extracted_skills]

    # --- Step 3: YouTube search query ---
    search_query = f"{domain} {' '.join(missing_skills)} full course"

    params = {
        "part": "snippet",
        "q": search_query,
        "type": "playlist",
        "maxResults": 8,
        "key": YOUTUBE_API_KEY,
    }

    res = requests.get(YOUTUBE_API_URL, params=params)
    yt_data = res.json()

    # --- Step 4: Extract playlists ---
    courses = []
    for item in yt_data.get("items", []):
        snippet = item["snippet"]
        playlist_id = item["id"]["playlistId"]
        courses.append({
            "title": snippet["title"],
            "description": snippet.get("description", ""),
            "thumbnail": snippet["thumbnails"]["medium"]["url"],
            "url": f"https://www.youtube.com/playlist?list={playlist_id}",
        })

    # --- Step 5: Return structured response ---
    return {
        "success": True,
        "domain": domain,
        "extracted_skills": extracted_skills,
        "missing_skills": missing_skills,
        "courses": courses,
    }
