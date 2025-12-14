from pydantic import BaseModel
from typing import Optional, List
from uuid import UUID
from datetime import datetime


class AppointmentBase(BaseModel):
    appointment_date: datetime
    appointment_type: Optional[str] = None
    status: str = '予約済'
    mtg_url: Optional[str] = None
    notes: Optional[str] = None


class AppointmentCreate(AppointmentBase):
    client_id: Optional[UUID] = None
    coach_id: Optional[UUID] = None  # 後方互換性のため保持
    coach_ids: Optional[List[UUID]] = None  # 複数コーチ対応


class AppointmentUpdate(BaseModel):
    appointment_date: Optional[datetime] = None
    appointment_type: Optional[str] = None
    status: Optional[str] = None
    mtg_url: Optional[str] = None
    notes: Optional[str] = None


class ClientInfo(BaseModel):
    client_id: UUID
    last_name: Optional[str] = None
    first_name: Optional[str] = None
    name: Optional[str] = None
    email: str

    class Config:
        from_attributes = True


class CoachInfo(BaseModel):
    coach_id: UUID
    name: Optional[str] = None
    last_name: Optional[str] = None
    first_name: Optional[str] = None
    email: str

    class Config:
        from_attributes = True


class AppointmentResponse(AppointmentBase):
    appointment_id: UUID
    client_id: UUID
    coach_id: UUID  # 後方互換性のため保持
    duration_minutes: Optional[int] = 30
    created_at: datetime
    updated_at: datetime
    client: Optional[ClientInfo] = None
    coaches: Optional[List[CoachInfo]] = None  # 複数コーチ対応

    class Config:
        from_attributes = True


class CoachAvailabilityBase(BaseModel):
    available_start: datetime
    available_end: datetime
    is_booked: bool = False


class CoachAvailabilityCreate(CoachAvailabilityBase):
    coach_id: UUID


class CoachAvailabilityResponse(CoachAvailabilityBase):
    availability_id: UUID
    coach_id: UUID
    created_at: datetime
    coach: Optional[CoachInfo] = None

    class Config:
        from_attributes = True
