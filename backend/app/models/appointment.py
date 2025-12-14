from sqlalchemy import Column, String, DateTime, ForeignKey, Text, Boolean, Table, Integer
from sqlalchemy import Uuid as UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from app.database import Base


# Appointment-Coach中間テーブル（多対多リレーション）
appointment_coaches = Table(
    'appointment_coaches',
    Base.metadata,
    Column('appointment_id', UUID(as_uuid=True), ForeignKey('appointments.appointment_id', ondelete='CASCADE'), primary_key=True),
    Column('coach_id', UUID(as_uuid=True), ForeignKey('coaches.coach_id', ondelete='CASCADE'), primary_key=True),
    Column('created_at', DateTime(timezone=True), server_default=func.now()),
)


class Appointment(Base):
    __tablename__ = "appointments"

    appointment_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    client_id = Column(UUID(as_uuid=True), ForeignKey("clients.client_id", ondelete="CASCADE"), nullable=False, index=True)
    coach_id = Column(UUID(as_uuid=True), ForeignKey("coaches.coach_id", ondelete="CASCADE"), nullable=False, index=True)  # 主担当コーチ（後方互換性）
    appointment_date = Column(DateTime(timezone=True), nullable=False, index=True)
    duration_minutes = Column(Integer, default=30)  # 面談時間（分）デフォルト30分
    appointment_type = Column(String(20))  # '定期' or 'スポット'
    status = Column(String(20), nullable=False, default='予約済', index=True)
    mtg_url = Column(Text)
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    client = relationship("Client", back_populates="appointments")
    coach = relationship("Coach", foreign_keys=[coach_id], back_populates="appointments")  # 主担当コーチ（後方互換性）
    coaches = relationship("Coach", secondary=appointment_coaches, backref="appointments_multi")  # 全担当コーチ（多対多）


class CoachAvailability(Base):
    __tablename__ = "coach_availability"

    availability_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    coach_id = Column(UUID(as_uuid=True), ForeignKey("coaches.coach_id", ondelete="CASCADE"), nullable=False, index=True)
    available_start = Column(DateTime(timezone=True), nullable=False, index=True)
    available_end = Column(DateTime(timezone=True), nullable=False, index=True)
    is_booked = Column(Boolean, default=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    coach = relationship("Coach", back_populates="availability")
