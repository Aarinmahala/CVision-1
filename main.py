from fastapi import FastAPI, UploadFile, File, Form, Depends
from services.job_description_processor import JobDescriptionProcessor
from services.resume_parser import ResumeParser
from services.candidate_matcher import CandidateMatcher
from services.interview_scheduler import InterviewScheduler
from database.models import JobDescription, Resume, ShortlistedCandidate, InterviewSchedule
from database.database import SessionLocal, engine
from sqlalchemy.orm import Session
import os
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv()

# Create database tables
JobDescription.metadata.create_all(bind=engine)
Resume.metadata.create_all(bind=engine)
ShortlistedCandidate.metadata.create_all(bind=engine)
InterviewSchedule.metadata.create_all(bind=engine)

app = FastAPI()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
async def read_root():
    return {"message": "Recruitment API - Use the available endpoints to manage your recruitment process"}

@app.post("/upload_jd")
async def upload_jd(
    jd_file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    try:
        # Save the uploaded file
        file_path = f"uploads/{jd_file.filename}"
        os.makedirs("uploads", exist_ok=True)
        with open(file_path, "wb") as buffer:
            content = await jd_file.read()
            buffer.write(content)

        # Process the job description
        processor = JobDescriptionProcessor()
        summary = processor.process(file_path)

        # Save to database
        job = JobDescription(
            title=summary.get("title", "Untitled"),
            description=summary.get("description", ""),
            requirements=summary.get("requirements", ""),
            file_path=file_path
        )
        db.add(job)
        db.commit()

        return {"status": "success", "message": "Job description processed successfully"}
    except Exception as e:
        return {"status": "error", "detail": str(e)}

@app.post("/upload_resume")
async def upload_resume(
    resume_file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    try:
        # Save the uploaded file
        file_path = f"uploads/{resume_file.filename}"
        os.makedirs("uploads", exist_ok=True)
        with open(file_path, "wb") as buffer:
            content = await resume_file.read()
            buffer.write(content)

        # Parse the resume
        parser = ResumeParser()
        resume_data = parser.parse(file_path)

        # Save to database
        resume = Resume(
            name=resume_data.get("name", "Unknown"),
            email=resume_data.get("email", ""),
            phone=resume_data.get("phone", ""),
            skills=", ".join(resume_data.get("skills", [])),
            experience=resume_data.get("experience", ""),
            education=resume_data.get("education", ""),
            file_path=file_path
        )
        db.add(resume)
        db.commit()

        return {"status": "success", "message": "Resume processed successfully"}
    except Exception as e:
        return {"status": "error", "detail": str(e)}

@app.post("/match_candidate")
async def match_candidate(
    job_id: int = Form(...),
    candidate_id: int = Form(...),
    db: Session = Depends(get_db)
):
    try:
        job = db.query(JobDescription).filter(JobDescription.id == job_id).first()
        candidate = db.query(Resume).filter(Resume.id == candidate_id).first()

        if not job or not candidate:
            return {"status": "error", "detail": "Job or candidate not found"}

        matcher = CandidateMatcher()
        match_score = matcher.calculate_match_score(job, candidate)

        # Save to shortlisted candidates if score is high enough
        if match_score >= 70:
            shortlisted = ShortlistedCandidate(
                job_id=job_id,
                candidate_id=candidate_id,
                match_score=match_score
            )
            db.add(shortlisted)
            db.commit()

        return {"status": "success", "match_score": match_score}
    except Exception as e:
        return {"status": "error", "detail": str(e)}

@app.post("/schedule_interview")
async def schedule_interview(
    job_id: int = Form(...),
    candidate_id: int = Form(...),
    interview_date: str = Form(...),
    db: Session = Depends(get_db)
):
    try:
        job = db.query(JobDescription).filter(JobDescription.id == job_id).first()
        candidate = db.query(Resume).filter(Resume.id == candidate_id).first()

        if not job or not candidate:
            return {"status": "error", "detail": "Job or candidate not found"}

        scheduler = InterviewScheduler()
        scheduled_time = scheduler.schedule_interview(
            job=job,
            candidate=candidate,
            interview_date=interview_date
        )

        # Save to database
        interview = InterviewSchedule(
            job_id=job_id,
            candidate_id=candidate_id,
            scheduled_time=scheduled_time
        )
        db.add(interview)
        db.commit()

        return {
            "status": "success",
            "message": "Interview scheduled successfully",
            "scheduled_time": scheduled_time
        }
    except Exception as e:
        return {"status": "error", "detail": str(e)}

# Get all job descriptions
@app.get("/jobs")
async def get_jobs(db: Session = Depends(get_db)):
    try:
        jobs = db.query(JobDescription).all()
        return {"status": "success", "jobs": jobs}
    except Exception as e:
        return {"status": "error", "detail": str(e)}

# Get all resumes/candidates
@app.get("/candidates")
async def get_candidates(db: Session = Depends(get_db)):
    try:
        candidates = db.query(Resume).all()
        return {"status": "success", "candidates": candidates}
    except Exception as e:
        return {"status": "error", "detail": str(e)}

# Get shortlisted candidates for a job
@app.get("/shortlisted/{job_id}")
async def get_shortlisted(job_id: int, db: Session = Depends(get_db)):
    try:
        shortlisted = db.query(ShortlistedCandidate).filter(
            ShortlistedCandidate.job_id == job_id
        ).all()
        return {"status": "success", "shortlisted": shortlisted}
    except Exception as e:
        return {"status": "error", "detail": str(e)}

# Get scheduled interviews
@app.get("/interviews")
async def get_interviews(db: Session = Depends(get_db)):
    try:
        interviews = db.query(InterviewSchedule).all()
        return {"status": "success", "interviews": interviews}
    except Exception as e:
        return {"status": "error", "detail": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 