from pydantic import BaseModel, EmailStr
from typing import Optional
from uuid import UUID
from datetime import datetime, date


class UserBase(BaseModel):
    email: EmailStr


class UserAuthResponse(BaseModel):
    user_id: UUID
    email: str
    user_type: str
    created_at: datetime

    class Config:
        from_attributes = True


class CoachBase(BaseModel):
    name: Optional[str] = None  # 後方互換性のために保持
    last_name: Optional[str] = None
    first_name: Optional[str] = None
    furigana: Optional[str] = None  # 後方互換性のために保持
    last_name_kana: Optional[str] = None
    first_name_kana: Optional[str] = None
    email: EmailStr
    phone: Optional[str] = None  # ハイフンなし、数字のみ
    mtg_url: Optional[str] = None


class CoachCreate(CoachBase):
    pass


class CoachUpdate(BaseModel):
    name: Optional[str] = None
    last_name: Optional[str] = None
    first_name: Optional[str] = None
    furigana: Optional[str] = None
    last_name_kana: Optional[str] = None
    first_name_kana: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    mtg_url: Optional[str] = None


class CoachResponse(CoachBase):
    coach_id: UUID
    user_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ClientBase(BaseModel):
    name: Optional[str] = None  # 後方互換性のために保持
    last_name: Optional[str] = None
    first_name: Optional[str] = None
    furigana: Optional[str] = None  # 後方互換性のために保持
    last_name_kana: Optional[str] = None
    first_name_kana: Optional[str] = None
    email: EmailStr
    phone: Optional[str] = None  # ハイフンなし、数字のみ
    company_name: Optional[str] = None
    occupation: Optional[str] = None
    registration_date: Optional[date] = None
    contract_end_date: Optional[date] = None
    status: str = 'active'
    will_can_must: Optional[str] = None
    strengths_finder: Optional[str] = None
    desired_income: Optional[int] = None


class ClientCreate(ClientBase):
    pass  # 担当コーチ概念を削除


class ClientUpdate(BaseModel):
    name: Optional[str] = None
    last_name: Optional[str] = None
    first_name: Optional[str] = None
    furigana: Optional[str] = None
    last_name_kana: Optional[str] = None
    first_name_kana: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    company_name: Optional[str] = None
    occupation: Optional[str] = None
    registration_date: Optional[date] = None
    contract_end_date: Optional[date] = None
    status: Optional[str] = None
    will_can_must: Optional[str] = None
    strengths_finder: Optional[str] = None
    desired_income: Optional[int] = None
    # coach_id: Optional[UUID] = None  # 削除：担当コーチ概念廃止


class ClientResponse(ClientBase):
    client_id: UUID
    user_id: UUID
    # coach_id: Optional[UUID]  # 削除：担当コーチ概念廃止
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
