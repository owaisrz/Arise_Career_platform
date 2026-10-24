import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Text, Integer, ForeignKey, DateTime
from backend.app.core.database import Base

class CareerPlan(Base):
    __tablename__ = "career_plans"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    target_role = Column(String(255), nullable=False)
    target_job_id = Column(String(36), ForeignKey("job_listings.id", ondelete="SET NULL"), nullable=True)
    duration_days = Column(Integer, default=30)
    current_day = Column(Integer, default=1)
    status = Column(String(50), default="active")  # active, completed, paused
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

class CareerPlanTask(Base):
    __tablename__ = "career_plan_tasks"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    plan_id = Column(String(36), ForeignKey("career_plans.id", ondelete="CASCADE"), nullable=False)
    stage = Column(String(100), nullable=False)  # Days 1–7: Assess & Prioritize, Days 8–14: Learn & Build Evidence, etc.
    day_number = Column(Integer, nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    linked_skill = Column(String(100), default="")
    priority = Column(String(50), default="Medium")  # High, Medium, Low
    duration_hours = Column(Integer, default=2)
    status = Column(String(50), default="pending")  # pending, in_progress, completed, skipped
    skip_reason = Column(Text, default="")
    completion_evidence = Column(Text, default="")
    due_date = Column(String(50), default="")
    completed_at = Column(DateTime, nullable=True)
