import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Text, Float, ForeignKey, DateTime
from backend.app.core.database import Base

class InterviewSession(Base):
    __tablename__ = "interview_sessions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    job_id = Column(String(36), ForeignKey("job_listings.id", ondelete="SET NULL"), nullable=True)
    role_title = Column(String(255), nullable=False)
    interview_type = Column(String(100), default="Technical")  # Technical, Behavioral, Project-grounded, System Design
    difficulty = Column(String(50), default="Intermediate")  # Entry, Intermediate, Advanced
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

class InterviewQuestion(Base):
    __tablename__ = "interview_questions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String(36), ForeignKey("interview_sessions.id", ondelete="CASCADE"), nullable=False)
    question_type = Column(String(50), nullable=False)  # role_specific, technical, behavioral, project_grounded
    question_text = Column(Text, nullable=False)
    context_rationale = Column(Text, default="")
    suggested_framework = Column(Text, default="")  # e.g., STAR structure guide
    linked_skill = Column(String(100), default="")
    linked_project = Column(String(255), default="")

class InterviewPractice(Base):
    __tablename__ = "interview_practices"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    question_id = Column(String(36), ForeignKey("interview_questions.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    user_response = Column(Text, nullable=False)
    feedback_score = Column(Float, default=80.0)
    feedback_summary = Column(Text, default="")
    strengths = Column(Text, default="[]")  # JSON list
    improvements = Column(Text, default="[]")  # JSON list
    practiced_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
