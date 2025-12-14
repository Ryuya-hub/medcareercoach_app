from sqlalchemy import Column, String, DateTime, ForeignKey, Text, Integer, Date, UniqueConstraint
from sqlalchemy import Uuid as UUID, JSON, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from app.database import Base


class Resume(Base):
    __tablename__ = "resumes"
    __table_args__ = (
        UniqueConstraint('client_id', 'version_number', name='uq_client_version'),
    )

    resume_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    client_id = Column(UUID(as_uuid=True), ForeignKey("clients.client_id", ondelete="CASCADE"), nullable=False, index=True)
    version_number = Column(Integer, nullable=False, default=1)
    status = Column(String(20), nullable=False, default='draft', index=True)

    # フリーテキスト形式の職務経歴書内容
    content = Column(Text)

    # メタ情報
    submitted_at = Column(DateTime(timezone=True), index=True)
    reviewed_at = Column(DateTime(timezone=True))
    approved_at = Column(DateTime(timezone=True))
    template_type = Column(String(50), default='standard')

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    client = relationship("Client", back_populates="resumes")
    reviews = relationship("ResumeReview", back_populates="resume", cascade="all, delete-orphan")
    work_experiences = relationship("WorkExperience", back_populates="resume", cascade="all, delete-orphan")
    education_history = relationship("EducationHistory", back_populates="resume", cascade="all, delete-orphan")
    certifications = relationship("Certification", back_populates="resume", cascade="all, delete-orphan")
    skills = relationship("Skill", back_populates="resume", cascade="all, delete-orphan")


class WorkExperience(Base):
    __tablename__ = "work_experiences"

    experience_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    resume_id = Column(UUID(as_uuid=True), ForeignKey("resumes.resume_id", ondelete="CASCADE"), nullable=False, index=True)
    display_order = Column(Integer, nullable=False)

    start_date = Column(Date, nullable=False)
    end_date = Column(Date)  # NULL = 現在も在籍中
    company_name = Column(String(200), nullable=False)
    department = Column(String(100))
    position = Column(String(100))
    employment_type = Column(String(50))

    job_description = Column(Text)
    achievements = Column(Text)
    skills_used = Column(Text)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    resume = relationship("Resume", back_populates="work_experiences")


class EducationHistory(Base):
    __tablename__ = "education_history"

    education_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    resume_id = Column(UUID(as_uuid=True), ForeignKey("resumes.resume_id", ondelete="CASCADE"), nullable=False, index=True)
    display_order = Column(Integer, nullable=False)

    start_date = Column(Date, nullable=False)
    end_date = Column(Date)
    school_name = Column(String(200), nullable=False)
    faculty = Column(String(100))
    major = Column(String(100))
    graduation_status = Column(String(20))

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    resume = relationship("Resume", back_populates="education_history")


class Certification(Base):
    __tablename__ = "certifications"

    certification_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    resume_id = Column(UUID(as_uuid=True), ForeignKey("resumes.resume_id", ondelete="CASCADE"), nullable=False, index=True)
    display_order = Column(Integer, nullable=False)

    acquisition_date = Column(Date, nullable=False)
    certification_name = Column(String(200), nullable=False)
    issuing_organization = Column(String(200))

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    resume = relationship("Resume", back_populates="certifications")


class Skill(Base):
    __tablename__ = "skills"

    skill_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    resume_id = Column(UUID(as_uuid=True), ForeignKey("resumes.resume_id", ondelete="CASCADE"), nullable=False, index=True)

    skill_category = Column(String(50), index=True)
    skill_name = Column(String(100), nullable=False)
    proficiency_level = Column(String(20))

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    resume = relationship("Resume", back_populates="skills")


class ResumeReview(Base):
    __tablename__ = "resume_reviews"

    review_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    resume_id = Column(UUID(as_uuid=True), ForeignKey("resumes.resume_id", ondelete="CASCADE"), nullable=False, index=True)
    coach_id = Column(UUID(as_uuid=True), ForeignKey("coaches.coach_id"), nullable=False)

    review_status = Column(String(20), nullable=False, default='in_progress', index=True)
    overall_comment = Column(Text)

    reviewed_at = Column(DateTime(timezone=True))

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    resume = relationship("Resume", back_populates="reviews")
    coach = relationship("Coach", back_populates="resume_reviews")
    comments = relationship("ReviewComment", back_populates="review", cascade="all, delete-orphan")


class ReviewComment(Base):
    __tablename__ = "review_comments"

    comment_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    review_id = Column(UUID(as_uuid=True), ForeignKey("resume_reviews.review_id", ondelete="CASCADE"), nullable=False, index=True)

    section_type = Column(String(50), nullable=False, index=True)
    section_id = Column(UUID(as_uuid=True), index=True)

    comment_type = Column(String(20), nullable=False, index=True)
    priority = Column(String(10))

    original_text = Column(Text)
    suggested_text = Column(Text)
    comment_text = Column(Text, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    review = relationship("ResumeReview", back_populates="comments")


class ReviewTemplate(Base):
    __tablename__ = "review_templates"

    template_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    coach_id = Column(UUID(as_uuid=True), ForeignKey("coaches.coach_id", ondelete="CASCADE"), nullable=False, index=True)

    template_name = Column(String(100), nullable=False)
    section_type = Column(String(50))
    comment_type = Column(String(20))
    template_text = Column(Text, nullable=False)

    usage_count = Column(Integer, default=0, index=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    coach = relationship("Coach", back_populates="review_templates")
