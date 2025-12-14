from pydantic import BaseModel
from typing import Optional, Dict, Any
from uuid import UUID
from datetime import datetime, date


class ClientInfo(BaseModel):
    """クライアント情報のサブスキーマ"""
    client_id: UUID
    name: Optional[str] = None  # 後方互換性のために保持
    last_name: Optional[str] = None
    first_name: Optional[str] = None
    status: str

    class Config:
        from_attributes = True


class ApplicationBase(BaseModel):
    company_name: str
    application_date: Optional[date] = None
    selection_stage: Optional[str] = None
    next_interview_date: Optional[date] = None
    next_action_date: Optional[date] = None
    priority: int = 5
    preference_rating: int = 3
    status: str = '選考中'
    notes: Optional[str] = None
    interview_questions: Optional[Dict[str, Any]] = None


class ApplicationCreate(ApplicationBase):
    client_id: Optional[UUID] = None


class ApplicationUpdate(BaseModel):
    company_name: Optional[str] = None
    application_date: Optional[date] = None
    selection_stage: Optional[str] = None
    next_interview_date: Optional[date] = None
    next_action_date: Optional[date] = None
    priority: Optional[int] = None
    preference_rating: Optional[int] = None
    status: Optional[str] = None
    notes: Optional[str] = None
    interview_questions: Optional[Dict[str, Any]] = None


class ApplicationResponse(ApplicationBase):
    application_id: UUID
    client_id: UUID
    client: Optional[ClientInfo] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ApplicationHistoryResponse(BaseModel):
    history_id: UUID
    application_id: UUID
    changed_date: datetime
    changed_field: Optional[str]
    old_value: Optional[str]
    new_value: Optional[str]
    changed_by: Optional[UUID]

    class Config:
        from_attributes = True


class CompanyAnalysisBase(BaseModel):
    company_name: str
    industry: Optional[str] = None
    location: Optional[str] = None
    analysis_notes: Optional[str] = None
    success_rate: Optional[float] = None


class CompanyAnalysisCreate(CompanyAnalysisBase):
    pass


class CompanyAnalysisUpdate(BaseModel):
    industry: Optional[str] = None
    location: Optional[str] = None
    analysis_notes: Optional[str] = None
    success_rate: Optional[float] = None


class CompanyAnalysisResponse(CompanyAnalysisBase):
    company_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
