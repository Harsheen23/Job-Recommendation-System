from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.realtime_jobs import router as jobs_router
from app.reconmended_courses import router as courses_router   # corrected spelling
from app.youtube_courses import router as yt_router             # new YouTube router

app = FastAPI(title="Smart Job & Course Recommender")

# --- CORS Configuration ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],      # loosened for local testing
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Include Routers ---
app.include_router(jobs_router, prefix="/api")
app.include_router(courses_router, prefix="/api")
app.include_router(yt_router, prefix="/api")

# --- Health Check ---
@app.get("/")
def root():
    return {"message": "Backend running successfully", "status": "ok"}
