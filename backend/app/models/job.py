import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Text, Integer, Float, Boolean, ForeignKey, DateTime
from backend.app.core.database import Base

class JobListing(Base):
    __tablename__ = "job_listings"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String(255), nullable=False)
    employer = Column(String(255), nullable=False)
    employer_domain = Column(String(255), default="")
    location = Column(String(255), default="Remote")
    work_arrangement = Column(String(50), default="remote")  # remote, hybrid, onsite
    salary_min = Column(Integer, nullable=True)
    salary_max = Column(Integer, nullable=True)
    salary_currency = Column(String(10), default="USD")
    salary_text = Column(String(100), default="")
    description = Column(Text, nullable=False)
    required_skills = Column(Text, default="[]")  # JSON list
    preferred_skills = Column(Text, default="[]")  # JSON list
    qualifications = Column(Text, default="[]")  # JSON list
    experience_required = Column(String(100), default="1-3 years")
    contact_email = Column(String(255), default="")
    contact_phone = Column(String(100), default="")
    contact_messaging = Column(String(100), default="")  # e.g., Telegram handle, WhatsApp
    application_url = Column(String(500), default="")
    source = Column(String(50), default="user_submitted")  # user_submitted, url_retrieved, seed_demo, partner_api
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

class SavedJob(Base):
    __tablename__ = "saved_jobs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    job_id = Column(String(36), ForeignKey("job_listings.id", ondelete="CASCADE"), nullable=False)
    status = Column(String(50), default="saved")  # saved, dismissed, applying
    notes = Column(Text, default="")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

class MatchResult(Base):
    __tablename__ = "match_results"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    job_id = Column(String(36), ForeignKey("job_listings.id", ondelete="CASCADE"), nullable=False)
    match_score = Column(Float, nullable=False)  # 0 to 100
    required_skills_score = Column(Float, default=0.0)
    preferred_skills_score = Column(Float, default=0.0)
    experience_score = Column(Float, default=0.0)
    explanation_json = Column(Text, default="{}")  # structured JSON with matching factors & evidence
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
