#!/usr/bin/env python3
"""
Advanced ATS Backend System
Enterprise-level Applicant Tracking System with AI-powered features
"""

from fastapi import FastAPI, HTTPException, Depends, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Float, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import uvicorn
import json
import datetime
import os
from pathlib import Path
import openai
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import pandas as pd

# Configuration
DATABASE_URL = "sqlite:///./advanced_ats.db"
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "your-openai-api-key")

# FastAPI App
app = FastAPI(
    title="Advanced ATS System",
    description="Enterprise-level Applicant Tracking System with AI-powered features",
    version="2.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database setup
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Security
security = HTTPBearer()

# Database Models
class Candidate(Base):
    __tablename__ = "candidates"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    phone = Column(String)
    location = Column(String)
    current_title = Column(String)
    experience_years = Column(Float)
    current_ctc = Column(Float)
    expected_ctc = Column(Float)
    notice_period = Column(Integer)
    skills = Column(Text)  # JSON string
    education = Column(Text)  # JSON string
    experience = Column(Text)  # JSON string
    resume_path = Column(String)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    
    applications = relationship("Application", back_populates="candidate")

class Job(Base):
    __tablename__ = "jobs"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    company = Column(String)
    location = Column(String)
    description = Column(Text)
    requirements = Column(Text)
    skills_required = Column(Text)  # JSON string
    experience_required = Column(Float)
    salary_range_min = Column(Float)
    salary_range_max = Column(Float)
    job_type = Column(String)  # Full-time, Part-time, Contract
    status = Column(String, default="Active")  # Active, Closed, Draft
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    
    applications = relationship("Application", back_populates="job")

class Application(Base):
    __tablename__ = "applications"
    
    id = Column(Integer, primary_key=True, index=True)
    candidate_id = Column(Integer, ForeignKey("candidates.id"))
    job_id = Column(Integer, ForeignKey("jobs.id"))
    status = Column(String, default="Applied")  # Applied, Screening, Interview, Offer, Rejected
    ai_score = Column(Float)  # AI-generated match score
    screening_notes = Column(Text)
    applied_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    
    candidate = relationship("Candidate", back_populates="applications")
    job = relationship("Job", back_populates="applications")
    interviews = relationship("Interview", back_populates="application")

class Interview(Base):
    __tablename__ = "interviews"
    
    id = Column(Integer, primary_key=True, index=True)
    application_id = Column(Integer, ForeignKey("applications.id"))
    interview_type = Column(String)  # Phone, Video, On-site
    scheduled_at = Column(DateTime)
    duration = Column(Integer)  # minutes
    interviewer = Column(String)
    status = Column(String, default="Scheduled")  # Scheduled, Completed, Cancelled
    feedback = Column(Text)
    score = Column(Float)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    application = relationship("Application", back_populates="interviews")

# Pydantic Models for API
class CandidateCreate(BaseModel):
    name: str
    email: str
    phone: Optional[str] = None
    location: Optional[str] = None
    current_title: Optional[str] = None
    experience_years: Optional[float] = None
    current_ctc: Optional[float] = None
    expected_ctc: Optional[float] = None
    notice_period: Optional[int] = None
    skills: Optional[List[str]] = None
    education: Optional[List[Dict]] = None
    experience: Optional[List[Dict]] = None

class JobCreate(BaseModel):
    title: str
    company: str
    location: str
    description: str
    requirements: str
    skills_required: List[str]
    experience_required: float
    salary_range_min: Optional[float] = None
    salary_range_max: Optional[float] = None
    job_type: str = "Full-time"

class ApplicationCreate(BaseModel):
    candidate_id: int
    job_id: int

# AI Service Class
class AIService:
    def __init__(self):
        self.openai_client = openai.OpenAI(api_key=OPENAI_API_KEY)
        self.vectorizer = TfidfVectorizer(stop_words='english')
    
    async def analyze_resume(self, resume_text: str) -> Dict[str, Any]:
        """Analyze resume using OpenAI GPT"""
        try:
            prompt = f"""
            Analyze this resume and extract the following information in JSON format:
            {resume_text}
            
            Return a JSON object with:
            - name: Full name
            - email: Email address
            - phone: Phone number
            - location: City/State
            - current_title: Current job title
            - experience_years: Years of experience
            - current_ctc: Current salary (number only)
            - expected_ctc: Expected salary (number only)
            - notice_period: Notice period in days
            - skills: Array of technical skills
            - education: Array of education details
            - experience: Array of work experience
            """
            
            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1
            )
            
            result = json.loads(response.choices[0].message.content)
            return result
            
        except Exception as e:
            print(f"AI analysis error: {e}")
            return self._fallback_analysis(resume_text)
    
    def _fallback_analysis(self, resume_text: str) -> Dict[str, Any]:
        """Fallback analysis using basic text processing"""
        lines = resume_text.split('\n')
        
        # Basic extraction
        name = lines[0] if lines else "Unknown"
        email = next((line for line in lines if '@' in line), "No email")
        
        # Extract skills (basic keyword matching)
        skill_keywords = ['python', 'java', 'javascript', 'react', 'angular', 'node.js', 'sql', 'aws', 'docker']
        skills = [skill for skill in skill_keywords if skill.lower() in resume_text.lower()]
        
        return {
            "name": name,
            "email": email,
            "phone": "Not found",
            "location": "Not found",
            "current_title": "Not found",
            "experience_years": 0.0,
            "current_ctc": 0.0,
            "expected_ctc": 0.0,
            "notice_period": 30,
            "skills": skills,
            "education": [],
            "experience": []
        }
    
    def calculate_match_score(self, candidate_skills: List[str], job_skills: List[str]) -> float:
        """Calculate match score between candidate and job"""
        if not candidate_skills or not job_skills:
            return 0.0
        
        # Convert skills to TF-IDF vectors
        all_skills = candidate_skills + job_skills
        skill_texts = [' '.join(candidate_skills), ' '.join(job_skills)]
        
        try:
            tfidf_matrix = self.vectorizer.fit_transform(skill_texts)
            similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
            return round(similarity * 100, 2)
        except:
            # Fallback: simple overlap calculation
            common_skills = set(candidate_skills) & set(job_skills)
            total_skills = set(candidate_skills) | set(job_skills)
            return round((len(common_skills) / len(total_skills)) * 100, 2)

# Database dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# AI service instance
ai_service = AIService()

# API Endpoints
@app.post("/candidates/", response_model=Dict[str, Any])
async def create_candidate(
    resume_file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Create candidate from resume upload with AI analysis"""
    try:
        # Read resume file
        resume_content = resume_file.file.read().decode('utf-8')
        
        # AI analysis
        candidate_data = await ai_service.analyze_resume(resume_content)
        
        # Save resume file
        resume_path = f"uploads/{resume_file.filename}"
        os.makedirs("uploads", exist_ok=True)
        with open(resume_path, "w") as f:
            f.write(resume_content)
        
        # Create candidate record
        candidate = Candidate(
            name=candidate_data.get("name", "Unknown"),
            email=candidate_data.get("email", "No email"),
            phone=candidate_data.get("phone", "No phone"),
            location=candidate_data.get("location", "Unknown"),
            current_title=candidate_data.get("current_title", "Unknown"),
            experience_years=candidate_data.get("experience_years", 0.0),
            current_ctc=candidate_data.get("current_ctc", 0.0),
            expected_ctc=candidate_data.get("expected_ctc", 0.0),
            notice_period=candidate_data.get("notice_period", 30),
            skills=json.dumps(candidate_data.get("skills", [])),
            education=json.dumps(candidate_data.get("education", [])),
            experience=json.dumps(candidate_data.get("experience", [])),
            resume_path=resume_path
        )
        
        db.add(candidate)
        db.commit()
        db.refresh(candidate)
        
        return {
            "success": True,
            "candidate_id": candidate.id,
            "analysis": candidate_data,
            "message": "Candidate created successfully with AI analysis"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/jobs/", response_model=Dict[str, Any])
async def create_job(
    job_data: JobCreate,
    db: Session = Depends(get_db)
):
    """Create new job posting"""
    try:
        job = Job(
            title=job_data.title,
            company=job_data.company,
            location=job_data.location,
            description=job_data.description,
            requirements=job_data.requirements,
            skills_required=json.dumps(job_data.skills_required),
            experience_required=job_data.experience_required,
            salary_range_min=job_data.salary_range_min,
            salary_range_max=job_data.salary_range_max,
            job_type=job_data.job_type
        )
        
        db.add(job)
        db.commit()
        db.refresh(job)
        
        return {
            "success": True,
            "job_id": job.id,
            "message": "Job created successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/applications/", response_model=Dict[str, Any])
async def create_application(
    application_data: ApplicationCreate,
    db: Session = Depends(get_db)
):
    """Create job application with AI scoring"""
    try:
        # Get candidate and job
        candidate = db.query(Candidate).filter(Candidate.id == application_data.candidate_id).first()
        job = db.query(Job).filter(Job.id == application_data.job_id).first()
        
        if not candidate or not job:
            raise HTTPException(status_code=404, detail="Candidate or job not found")
        
        # Calculate AI match score
        candidate_skills = json.loads(candidate.skills)
        job_skills = json.loads(job.skills_required)
        ai_score = ai_service.calculate_match_score(candidate_skills, job_skills)
        
        # Create application
        application = Application(
            candidate_id=application_data.candidate_id,
            job_id=application_data.job_id,
            ai_score=ai_score
        )
        
        db.add(application)
        db.commit()
        db.refresh(application)
        
        return {
            "success": True,
            "application_id": application.id,
            "ai_score": ai_score,
            "message": f"Application created with AI score: {ai_score}%"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/candidates/", response_model=List[Dict[str, Any]])
async def get_candidates(
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get candidates with search and pagination"""
    query = db.query(Candidate)
    
    if search:
        query = query.filter(
            Candidate.name.contains(search) |
            Candidate.email.contains(search) |
            Candidate.skills.contains(search)
        )
    
    candidates = query.offset(skip).limit(limit).all()
    
    return [
        {
            "id": c.id,
            "name": c.name,
            "email": c.email,
            "current_title": c.current_title,
            "experience_years": c.experience_years,
            "skills": json.loads(c.skills),
            "created_at": c.created_at.isoformat()
        }
        for c in candidates
    ]

@app.get("/jobs/", response_model=List[Dict[str, Any]])
async def get_jobs(
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get jobs with filtering"""
    query = db.query(Job)
    
    if status:
        query = query.filter(Job.status == status)
    
    jobs = query.offset(skip).limit(limit).all()
    
    return [
        {
            "id": j.id,
            "title": j.title,
            "company": j.company,
            "location": j.location,
            "experience_required": j.experience_required,
            "status": j.status,
            "created_at": j.created_at.isoformat()
        }
        for j in jobs
    ]

@app.get("/applications/", response_model=List[Dict[str, Any]])
async def get_applications(
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get applications with filtering"""
    query = db.query(Application).join(Candidate).join(Job)
    
    if status:
        query = query.filter(Application.status == status)
    
    applications = query.offset(skip).limit(limit).all()
    
    return [
        {
            "id": a.id,
            "candidate_name": a.candidate.name,
            "job_title": a.job.title,
            "company": a.job.company,
            "status": a.status,
            "ai_score": a.ai_score,
            "applied_at": a.applied_at.isoformat()
        }
        for a in applications
    ]

@app.get("/analytics/dashboard", response_model=Dict[str, Any])
async def get_dashboard_analytics(db: Session = Depends(get_db)):
    """Get dashboard analytics"""
    try:
        total_candidates = db.query(Candidate).count()
        total_jobs = db.query(Job).count()
        total_applications = db.query(Application).count()
        
        # Status distribution
        status_counts = db.query(Application.status, db.func.count(Application.id)).group_by(Application.status).all()
        status_distribution = {status: count for status, count in status_counts}
        
        # Average AI scores
        avg_score = db.query(db.func.avg(Application.ai_score)).scalar() or 0
        
        # Recent activity
        recent_applications = db.query(Application).order_by(Application.created_at.desc()).limit(5).all()
        
        return {
            "total_candidates": total_candidates,
            "total_jobs": total_jobs,
            "total_applications": total_applications,
            "status_distribution": status_distribution,
            "average_ai_score": round(avg_score, 2),
            "recent_applications": [
                {
                    "candidate": a.candidate.name,
                    "job": a.job.title,
                    "score": a.ai_score,
                    "date": a.created_at.isoformat()
                }
                for a in recent_applications
            ]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Create database tables
Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    print("🚀 Starting Advanced ATS Backend...")
    print("📊 Database initialized")
    print("🤖 AI service ready")
    print("🌐 API server starting on http://localhost:8000")
    
    uvicorn.run(
        "advanced_ats_backend:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
