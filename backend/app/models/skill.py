import uuid
from sqlalchemy import Column, String, Text
from backend.app.core.database import Base

class SkillTaxonomy(Base):
    __tablename__ = "skill_taxonomy"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    canonical_name = Column(String(100), unique=True, index=True, nullable=False)
    category = Column(String(100), nullable=False)
    description = Column(Text, default="")
    aliases = Column(Text, default="[]")  # JSON list
    prerequisites = Column(Text, default="[]")  # JSON list
    related_skills = Column(Text, default="[]")  # JSON list
