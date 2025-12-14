from __future__ import annotations
from pydantic import BaseModel, EmailStr
from typing import Optional, List
from uuid import UUID
from datetime import datetime, date


# Work Experience Schemas
class WorkExperienceBase(BaseModel):
    start_date: date
    end_date: Optional[date] = None
    company_name: str
    department: Optional[str] = None
    position: Optional[str] = None
    employment_type: Optional[str] = None
    job_description: Optional[str] = None
    achievements: Optional[str] = None
    skills_used: Optional[str] = None


class WorkExperienceCreate(WorkExperienceBase):
    display_order: int


class WorkExperienceUpdate(BaseModel):
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    company_name: Optional[str] = None
    department: Optional[str] = None
    position: Optional[str] = None
    employment_type: Optional[str] = None
    job_description: Optional[str] = None
    achievements: Optional[str] = None
    skills_used: Optional[str] = None
    display_order: Optional[int] = None


class WorkExperienceResponse(WorkExperienceBase):
    experience_id: UUID
    resume_id: UUID
    display_order: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Education History Schemas
class EducationHistoryBase(BaseModel):
    start_date: date
    end_date: Optional[date] = None
    school_name: str
    faculty: Optional[str] = None
    major: Optional[str] = None
    graduation_status: Optional[str] = None


class EducationHistoryCreate(EducationHistoryBase):
    display_order: int


class EducationHistoryUpdate(BaseModel):
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    school_name: Optional[str] = None
    faculty: Optional[str] = None
    major: Optional[str] = None
    graduation_status: Optional[str] = None
    display_order: Optional[int] = None


class EducationHistoryResponse(EducationHistoryBase):
    education_id: UUID
    resume_id: UUID
    display_order: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Certification Schemas
class CertificationBase(BaseModel):
    acquisition_date: date
    certification_name: str
    issuing_organization: Optional[str] = None


class CertificationCreate(CertificationBase):
    display_order: int


class CertificationUpdate(BaseModel):
    acquisition_date: Optional[date] = None
    certification_name: Optional[str] = None
    issuing_organization: Optional[str] = None
    display_order: Optional[int] = None


class CertificationResponse(CertificationBase):
    certification_id: UUID
    resume_id: UUID
    display_order: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Skill Schemas
class SkillBase(BaseModel):
    skill_category: Optional[str] = None
    skill_name: str
    proficiency_level: Optional[str] = None


class SkillCreate(SkillBase):
    pass


class SkillUpdate(BaseModel):
    skill_category: Optional[str] = None
    skill_name: Optional[str] = None
    proficiency_level: Optional[str] = None


class SkillResponse(SkillBase):
    skill_id: UUID
    resume_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Resume Schemas
class ResumeBase(BaseModel):
    content: Optional[str] = None
    template_type: str = 'standard'


class ResumeCreate(ResumeBase):
    client_id: Optional[UUID] = None


class ResumeUpdate(ResumeBase):
    pass


class ResumeResponse(ResumeBase):
    resume_id: UUID
    client_id: UUID
    version_number: int
    status: str
    submitted_at: Optional[datetime]
    reviewed_at: Optional[datetime]
    approved_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    reviews: List[ResumeReviewResponse] = []

    class Config:
        from_attributes = True


# Review Comment Schemas
class ReviewCommentBase(BaseModel):
    section_type: str
    section_id: Optional[UUID] = None
    comment_type: str
    priority: Optional[str] = None
    original_text: Optional[str] = None
    suggested_text: Optional[str] = None
    comment_text: str


class ReviewCommentCreate(ReviewCommentBase):
    review_id: UUID


class ReviewCommentUpdate(BaseModel):
    section_type: Optional[str] = None
    section_id: Optional[UUID] = None
    comment_type: Optional[str] = None
    priority: Optional[str] = None
    original_text: Optional[str] = None
    suggested_text: Optional[str] = None
    comment_text: Optional[str] = None


class ReviewCommentResponse(ReviewCommentBase):
    comment_id: UUID
    review_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Resume Review Schemas
class ResumeReviewBase(BaseModel):
    review_status: str = 'in_progress'
    overall_comment: Optional[str] = None


class ResumeReviewCreate(ResumeReviewBase):
    resume_id: Optional[UUID] = None  # URLパラメータから取得するためオプション
    coach_id: Optional[UUID] = None  # 認証情報から取得するためオプション


class ResumeReviewUpdate(BaseModel):
    review_status: Optional[str] = None
    overall_comment: Optional[str] = None


class CoachInfo(BaseModel):
    """コーチ情報（添削履歴用）"""
    coach_id: UUID
    name: Optional[str] = None
    last_name: Optional[str] = None
    first_name: Optional[str] = None
    email: str

    class Config:
        from_attributes = True


class ResumeReviewResponse(ResumeReviewBase):
    review_id: UUID
    resume_id: UUID
    coach_id: UUID
    reviewed_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    comments: List[ReviewCommentResponse] = []
    coach: Optional[CoachInfo] = None  # コーチ情報を追加

    class Config:
        from_attributes = True


# Review Template Schemas
class ReviewTemplateBase(BaseModel):
    template_name: str
    section_type: Optional[str] = None
    comment_type: Optional[str] = None
    template_text: str


class ReviewTemplateCreate(ReviewTemplateBase):
    coach_id: UUID


class ReviewTemplateUpdate(BaseModel):
    template_name: Optional[str] = None
    section_type: Optional[str] = None
    comment_type: Optional[str] = None
    template_text: Optional[str] = None


class ReviewTemplateResponse(ReviewTemplateBase):
    template_id: UUID
    coach_id: UUID
    usage_count: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Rebuild models to resolve forward references
ResumeResponse.model_rebuild()
ResumeReviewResponse.model_rebuild()
