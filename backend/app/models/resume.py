import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Text, Boolean, ForeignKey, DateTime
from backend.app.core.database import Base

class ResumeDocument(Base):
    __tablename__ = "resume_documents"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    version_name = Column(String(255), nullable=False)
    target_job_id = Column(String(36), ForeignKey("job_listings.id", ondelete="SET NULL"), nullable=True)
    target_employer = Column(String(255), default="")
    summary = Column(Text, default="")
    selected_projects = Column(Text, default="[]")  # JSON list of project IDs
    selected_skills = Column(Text, default="[]")  # JSON list of skill names
    is_redacted = Column(Boolean, default=False)
    redacted_fields = Column(Text, default="[]")  # e.g., ["phone", "email", "full_name"]
    share_token = Column(String(64), unique=True, default=lambda: uuid.uuid4().hex)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

class EmployerSharingRecord(Base):
    __tablename__ = "employer_sharing_records"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    resume_id = Column(String(36), ForeignKey("resume_documents.id", ondelete="CASCADE"), nullable=False)
    employer_name = Column(String(255), nullable=False)
    share_token = Column(String(64), index=True, nullable=False)
    consent_granted = Column(Boolean, default=True)
    contact_visibility = Column(String(50), default="redacted")  # full, redacted, email_only
    status = Column(String(50), default="active")  # active, revoked, expired
    shared_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    revoked_at = Column(DateTime, nullable=True)
