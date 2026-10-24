import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Text, Integer, Float, ForeignKey, DateTime
from backend.app.core.database import Base

class JobReport(Base):
    __tablename__ = "job_reports"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    job_id = Column(String(36), ForeignKey("job_listings.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    reason = Column(String(100), nullable=False)  # scam_payment, fake_company, misleading_info, harassment, other
    details = Column(Text, default="")
    status = Column(String(50), default="pending_review")  # pending_review, reviewed, dismissed
    reported_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

class AuditEvent(Base):
    __tablename__ = "audit_events"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    event_type = Column(String(100), nullable=False)  # profile_edit, evidence_approved, evidence_rejected, document_deleted, application_stage_change, resume_created, consent_revoked, share_created
    details_json = Column(Text, default="{}")
    ip_address = Column(String(50), default="127.0.0.1")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

class FairnessEvaluationRun(Base):
    __tablename__ = "fairness_evaluation_runs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    run_title = Column(String(255), nullable=False)
    test_dimension = Column(String(100), nullable=False)  # Name/Demographic, College Tier, Geographic/Location
    sample_size = Column(Integer, default=10)
    baseline_score = Column(Float, nullable=False)
    counterfactual_score = Column(Float, nullable=False)
    delta_score = Column(Float, nullable=False)
    rank_shift_count = Column(Integer, default=0)
    notes = Column(Text, default="")
    run_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
