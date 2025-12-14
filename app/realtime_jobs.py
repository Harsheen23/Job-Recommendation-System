from fastapi import APIRouter, UploadFile, File, Query
from app.db import SessionLocal, JobLog
from PyPDF2 import PdfReader
from sentence_transformers import SentenceTransformer, util
import httpx
import time
import os

router = APIRouter()

# --- CONFIG ---
API_URL = "https://jsearch.p.rapidapi.com/search"
API_KEY = "cc1ad1ef15msh8c8d7c4ac148bf3p13ab85jsn3d8cade8bee2"  # safer than hardcoding

HEADERS = {
    "x-rapidapi-key": API_KEY,
    "x-rapidapi-host": "jsearch.p.rapidapi.com"
}

# --- DATABASE LOGGER ---
def log_to_db(step, message, keyword="", location="", success=0, job_count=0, duration=0.0):
    session = SessionLocal()
    try:
        log = JobLog(
            step=step, message=message, keyword=keyword,
            location=location, success=success,
            job_count=job_count, duration=duration
        )
        session.add(log)
        session.commit()
    finally:
        session.close()

# --- HELPERS ---
async def extract_pdf_text(file: UploadFile) -> str:
    """Extract text from PDF safely."""
    try:
        reader = PdfReader(file.file)
        text = "\n".join([page.extract_text() or "" for page in reader.pages])
        return text.strip()
    except Exception as e:
        print("PDF read failed:", e)
        return ""

# --- LOAD MODEL ONCE ---
model = SentenceTransformer("all-MiniLM-L6-v2")

# --- MAIN ENDPOINT ---
@router.post("/resume-jobs")
async def recommend_jobs(
    file: UploadFile = File(...),
    keyword: str = Query(..., description="Job keyword (e.g. python developer, data scientist)"),
    location: str = Query(..., description="Location for job search (e.g. Bangalore, New York)"),
    limit: int = Query(10, description="Number of jobs to return")
):
    """
    Match a resume to job listings using semantic similarity.
    Both keyword and location are provided by the user.
    """
    start = time.time()
    log_to_db("start", "Recommendation started", keyword, location)

    text = await extract_pdf_text(file)
    if not text:
        return {"success": False, "message": "Could not extract text from resume"}

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            res = await client.get(API_URL, headers=HEADERS, params={"query": f"{keyword} in {location}"})
            if res.status_code != 200:
                return {"success": False, "message": f"Job API failed: {res.text}"}
            jobs = res.json().get("data", [])[:limit]
    except Exception as e:
        return {"success": False, "message": f"API request failed: {e}"}

    if not jobs:
        return {"success": False, "message": "No jobs found"}

    # Compute similarities
    resume_emb = model.encode(text, convert_to_tensor=True)
    job_texts = [f"{j.get('job_title', '')} {j.get('job_description', '')}" for j in jobs]
    job_embs = model.encode(job_texts, convert_to_tensor=True)

    similarities = util.pytorch_cos_sim(resume_emb, job_embs)[0]
    ranked = sorted(zip(jobs, similarities), key=lambda x: float(x[1]), reverse=True)

    results = []
    for j, sim in ranked:
        results.append({
            "title": j.get("job_title"),
            "company": j.get("employer_name"),
            "location": j.get("job_city"),
            "apply_link": j.get("job_apply_link"),
            "description": (j.get("job_description") or "")[:200],
            "score": round(float(sim), 3)
        })

    duration = round(time.time() - start, 2)
    log_to_db("complete", "Pipeline finished", keyword, location, success=1, job_count=len(results), duration=duration)

    return {"success": True, "jobs": results, "duration": duration}
