import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Text, Float, ForeignKey, DateTime
from backend.app.core.database import Base

class JobAssessment(Base):
    __tablename__ = "job_assessments"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    job_id = Column(String(36), ForeignKey("job_listings.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=True)
    risk_score = Column(Float, nullable=False)  # 0 to 100
    risk_tier = Column(String(50), nullable=False)  # Lower observed risk, Needs verification, Elevated risk indicators
    summary = Column(Text, nullable=False)
    positive_signals = Column(Text, default="[]")  # JSON list
    unknown_signals = Column(Text, default="[]")  # JSON list
    method = Column(String(100), default="Multi-Signal Heuristic & Calibration Engine")
    assessed_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

class RiskSignal(Base):
    __tablename__ = "risk_signals"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    assessment_id = Column(String(36), ForeignKey("job_assessments.id", ondelete="CASCADE"), nullable=False)
    signal_category = Column(String(100), nullable=False)  # payment_request, domain_mismatch, communication_pattern, listing_content, implausible_experience, duplication
    severity = Column(String(50), nullable=False)  # low, medium, high, critical
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    evidence_excerpt = Column(Text, default="")
    certainty = Column(String(50), default="potential")  # confirmed, potential, unknown
    recommended_action = Column(Text, default="")
