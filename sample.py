import requests
import sqlite3
import json

# ---------- CONFIG ----------
API_URL = "https://jsearch.p.rapidapi.com/search"
API_KEY = "cc1ad1ef15msh8c8d7c4ac148bf3p13ab85jsn3d8cade8bee2"  # <-- replace with your actual key
DB_NAME = "jobs.db"

# ---------- FETCH DATA ----------
def fetch_jobs():
    query_params = {
        "query": "developer jobs in chicago",
        "page": "1",
        "num_pages": "1",
        "country": "us",
        "date_posted": "all"
    }

    headers = {
        "x-rapidapi-host": "jsearch.p.rapidapi.com",
        "x-rapidapi-key": API_KEY
    }

    response = requests.get(API_URL, headers=headers, params=query_params)
    response.raise_for_status()
    return response.json()

# ---------- STORE DATA ----------
def store_jobs(data):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Create table for storing job data
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            job_title TEXT,
            employer_name TEXT,
            location TEXT,
            job_posted TEXT,
            job_description TEXT,
            raw_json TEXT
        )
    """)

    for job in data.get("data", []):
        cursor.execute("""
            INSERT INTO jobs (job_title, employer_name, location, job_posted, job_description, raw_json)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            job.get("job_title"),
            job.get("employer_name"),
            job.get("job_city") or job.get("job_country"),
            job.get("job_posted_at_datetime_utc"),
            job.get("job_description"),
            json.dumps(job)
        ))

    conn.commit()
    conn.close()

# ---------- MAIN ----------
if __name__ == "__main__":
    try:
        data = fetch_jobs()
        store_jobs(data)
        print("Job data fetched and stored successfully.")
    except Exception as e:
        print(f"Error: {e}")
