import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Text, Boolean, Integer, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from backend.app.core.database import Base

class CandidateProfile(Base):
    __tablename__ = "candidate_profiles"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    headline = Column(String(255), default="")
    summary = Column(Text, default="")
    preferred_role = Column(String(255), default="")
    preferred_location = Column(String(255), default="")
    work_arrangement = Column(String(50), default="remote")  # remote, hybrid, onsite
    availability = Column(String(100), default="Immediate")
    phone = Column(String(50), default="")
    portfolio_url = Column(String(255), default="")
    github_url = Column(String(255), default="")
    linkedin_url = Column(String(255), default="")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

class Education(Base):
    __tablename__ = "education"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    profile_id = Column(String(36), ForeignKey("candidate_profiles.id", ondelete="CASCADE"), nullable=False)
    institution = Column(String(255), nullable=False)
    degree = Column(String(255), nullable=False)
    field_of_study = Column(String(255), default="")
    start_year = Column(Integer, nullable=True)
    end_year = Column(Integer, nullable=True)
    grade = Column(String(50), default="")
    is_extracted = Column(Boolean, default=False)
    source_reference = Column(Text, default="")

class WorkExperience(Base):
    __tablename__ = "work_experiences"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    profile_id = Column(String(36), ForeignKey("candidate_profiles.id", ondelete="CASCADE"), nullable=False)
    company = Column(String(255), nullable=False)
    role = Column(String(255), nullable=False)
    location = Column(String(255), default="")
    start_date = Column(String(50), default="")
    end_date = Column(String(50), default="")
    is_current = Column(Boolean, default=False)
    description = Column(Text, default="")
    is_extracted = Column(Boolean, default=False)
    source_reference = Column(Text, default="")

class Project(Base):
    __tablename__ = "projects"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    profile_id = Column(String(36), ForeignKey("candidate_profiles.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    skills_used = Column(Text, default="[]")  # JSON list of skills
    demo_url = Column(String(255), default="")
    repo_url = Column(String(255), default="")
    role = Column(String(255), default="Lead Developer")
    start_date = Column(String(50), default="")
    end_date = Column(String(50), default="")
    is_extracted = Column(Boolean, default=False)
    source_reference = Column(Text, default="")

class CandidateSkill(Base):
    __tablename__ = "candidate_skills"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    profile_id = Column(String(36), ForeignKey("candidate_profiles.id", ondelete="CASCADE"), nullable=False)
    skill_name = Column(String(100), nullable=False)
    canonical_name = Column(String(100), nullable=False)
    proficiency_level = Column(String(50), default="Intermediate")  # Beginner, Intermediate, Advanced, Expert
    category = Column(String(100), default="Technical")
    verified_status = Column(String(50), default="self_reported")  # unverified, self_reported, document_extracted, project_verified
    confidence_score = Column(Float, default=0.7)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

class SkillEvidence(Base):
    __tablename__ = "skill_evidences"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    candidate_skill_id = Column(String(36), ForeignKey("candidate_skills.id", ondelete="CASCADE"), nullable=False)
    evidence_type = Column(String(50), nullable=False)  # project, document_claim, work_experience, certification
    source_title = Column(String(255), nullable=False)
    excerpt = Column(Text, nullable=False)
    page_number = Column(Integer, nullable=True)
    confidence = Column(Float, default=0.85)
    is_approved = Column(Boolean, default=True)
