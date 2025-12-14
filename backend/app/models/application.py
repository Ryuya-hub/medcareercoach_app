from sqlalchemy import Column, String, DateTime, ForeignKey, Text, Integer, Date, Numeric
from sqlalchemy import Uuid as UUID, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from app.database import Base


class Application(Base):
    __tablename__ = "applications"

    application_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    client_id = Column(UUID(as_uuid=True), ForeignKey("clients.client_id", ondelete="CASCADE"), nullable=False, index=True)
    company_name = Column(String(200), nullable=False, index=True)
    application_date = Column(Date)
    selection_stage = Column(String(50))
    next_interview_date = Column(Date)
    next_action_date = Column(Date)
    priority = Column(Integer, default=5)
    preference_rating = Column(Integer, default=3)
    status = Column(String(20), nullable=False, default='選考中', index=True)
    notes = Column(Text)
    interview_questions = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    client = relationship("Client", back_populates="applications")
    history = relationship("ApplicationHistory", back_populates="application", cascade="all, delete-orphan")


class ApplicationHistory(Base):
    __tablename__ = "application_history"

    history_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    application_id = Column(UUID(as_uuid=True), ForeignKey("applications.application_id", ondelete="CASCADE"), nullable=False, index=True)
    changed_date = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), index=True)
    changed_field = Column(String(100))
    old_value = Column(Text)
    new_value = Column(Text)
    changed_by = Column(UUID(as_uuid=True), ForeignKey("users_auth.user_id"))

    # Relationships
    application = relationship("Application", back_populates="history")


class CompanyAnalysis(Base):
    __tablename__ = "company_analysis"

    company_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_name = Column(String(200), unique=True, nullable=False, index=True)
    industry = Column(String(100))
    location = Column(String(200))
    analysis_notes = Column(Text)
    success_rate = Column(Numeric(5, 2))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
