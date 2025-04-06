# Recruitment Automation System

An automated recruitment system that processes job descriptions and resumes, matches candidates, and schedules interviews.

## Features

- Job Description Summarization using Ollama LLM
- Resume Parsing (PDF/DOCX)
- Candidate-Job Matching
- Interview Scheduling
- Multi-Agent System Coordination
- REST API Endpoints

## Setup

1. Create and activate virtual environment:
```bash
python -m venv recruitment_env
# Windows
.\recruitment_env\Scripts\activate
# Linux/Mac
source recruitment_env/bin/activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
Create a `.env` file with:
```
OLLAMA_API_URL=http://localhost:11434
SMTP_SERVER=your_smtp_server
SMTP_PORT=587
SMTP_USERNAME=your_email
SMTP_PASSWORD=your_password
```

4. Run the application:
```bash
uvicorn main:app --reload
```

## API Endpoints

- POST /upload_jd - Upload and summarize job description
- POST /upload_resume - Parse resume
- POST /match_candidate - Calculate match score
- GET /shortlist_candidates - Get shortlisted candidates
- POST /schedule_interview - Schedule interview

## Project Structure

```
.
├── main.py                 # FastAPI application entry point
├── requirements.txt        # Project dependencies
├── .env                    # Environment variables
├── database/              # Database related files
│   └── models.py          # Database models
├── services/              # Core business logic
│   ├── jd_processor.py    # Job description processing
│   ├── resume_parser.py   # Resume parsing
│   ├── matcher.py         # Candidate matching
│   └── scheduler.py       # Interview scheduling
└── utils/                 # Utility functions
    └── email_sender.py    # Email sending functionality
``` 