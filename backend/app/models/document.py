import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Text, Integer, Float, ForeignKey, DateTime
from backend.app.core.database import Base

class Document(Base):
    __tablename__ = "documents"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    filename = Column(String(255), nullable=False)
    file_hash = Column(String(64), index=True, nullable=False)
    file_type = Column(String(50), nullable=False)  # pdf, docx, txt, image
    mime_type = Column(String(100), nullable=False)
    file_size = Column(Integer, nullable=False)
    storage_path = Column(String(500), nullable=False)
    page_count = Column(Integer, default=1)
    document_type = Column(String(50), default="resume")  # resume, cover_letter, certificate, project_report, other
    extraction_quality = Column(String(50), default="Moderate")  # High, Moderate, Review Required, Low
    status = Column(String(50), default="uploaded")  # uploaded, validating, extracting, structuring, review_required, saved, error
    error_message = Column(Text, default="")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

class ExtractedClaim(Base):
    __tablename__ = "extracted_claims"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    document_id = Column(String(36), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)
    claim_type = Column(String(50), nullable=False)  # skill, education, experience, project, personal_info
    field_name = Column(String(100), nullable=False)
    raw_value = Column(Text, nullable=False)
    normalized_value = Column(Text, default="")
    confidence = Column(Float, default=0.85)
    page_number = Column(Integer, nullable=True)
    section_heading = Column(String(100), default="")
    text_excerpt = Column(Text, default="")
    status = Column(String(50), default="pending_review")  # pending_review, approved, rejected, edited
    user_correction = Column(Text, default="")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
