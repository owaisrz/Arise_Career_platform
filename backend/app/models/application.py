import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Text, Boolean, ForeignKey, DateTime
from backend.app.core.database import Base

class Application(Base):
    __tablename__ = "applications"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    job_id = Column(String(36), ForeignKey("job_listings.id", ondelete="CASCADE"), nullable=False)
    stage = Column(String(50), default="Saved")  # Saved, Planned, Applied, Assessment, Interview, Offer, Rejected, Withdrawn
    applied_date = Column(String(50), default="")
    follow_up_date = Column(String(50), default="")
    notes = Column(Text, default="")
    resume_version_id = Column(String(36), nullable=True)
    interview_date = Column(String(50), default="")
    outcome_notes = Column(Text, default="")
    is_archived = Column(Boolean, default=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

class ApplicationNote(Base):
    __tablename__ = "application_notes"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    application_id = Column(String(36), ForeignKey("applications.id", ondelete="CASCADE"), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
