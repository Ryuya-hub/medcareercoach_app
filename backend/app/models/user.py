from sqlalchemy import Column, String, DateTime, ForeignKey, Text, Integer, Date, Table
from sqlalchemy import Uuid as UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from app.database import Base


# Client-Coach中間テーブル（多対多リレーション）
client_coach_association = Table(
    'client_coach',
    Base.metadata,
    Column('client_id', UUID(as_uuid=True), ForeignKey('clients.client_id', ondelete='CASCADE'), primary_key=True),
    Column('coach_id', UUID(as_uuid=True), ForeignKey('coaches.coach_id', ondelete='CASCADE'), primary_key=True),
    Column('created_at', DateTime(timezone=True), server_default=func.now()),
)


class UserAuth(Base):
    __tablename__ = "users_auth"

    user_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    user_type = Column(String(20), nullable=False, index=True)  # 'coach' or 'client'
    role = Column(String(20), nullable=False, index=True)  # 'super_admin', 'coach', or 'client'
    status = Column(String(20), nullable=False, default='active', index=True)  # 'active', 'inactive', 'suspended'
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    coach = relationship("Coach", back_populates="user", uselist=False, cascade="all, delete-orphan")
    client = relationship("Client", back_populates="user", uselist=False, cascade="all, delete-orphan")


class Coach(Base):
    __tablename__ = "coaches"

    coach_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users_auth.user_id", ondelete="CASCADE"), nullable=False)
    name = Column(String(100))  # 後方互換性のために保持
    last_name = Column(String(50))
    first_name = Column(String(50))
    furigana = Column(String(100))  # 後方互換性のために保持
    last_name_kana = Column(String(50))
    first_name_kana = Column(String(50))
    email = Column(String(255), unique=True, nullable=False, index=True)
    phone = Column(String(20))  # ハイフンなし、数字のみ
    mtg_url = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    user = relationship("UserAuth", back_populates="coach")
    clients = relationship("Client", secondary=client_coach_association, back_populates="coaches")
    appointments = relationship("Appointment", back_populates="coach")
    availability = relationship("CoachAvailability", back_populates="coach", cascade="all, delete-orphan")
    resume_reviews = relationship("ResumeReview", back_populates="coach")
    review_templates = relationship("ReviewTemplate", back_populates="coach", cascade="all, delete-orphan")


class Client(Base):
    __tablename__ = "clients"

    client_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users_auth.user_id", ondelete="CASCADE"), nullable=False)
    name = Column(String(100))  # 後方互換性のために保持
    last_name = Column(String(50))
    first_name = Column(String(50))
    furigana = Column(String(100))  # 後方互換性のために保持
    last_name_kana = Column(String(50))
    first_name_kana = Column(String(50))
    email = Column(String(255), unique=True, nullable=False, index=True)
    phone = Column(String(20))  # ハイフンなし、数字のみ
    company_name = Column(String(200))
    occupation = Column(String(100))
    registration_date = Column(Date)
    contract_end_date = Column(Date)
    status = Column(String(20), nullable=False, default='active', index=True)
    will_can_must = Column(Text)
    strengths_finder = Column(Text)
    desired_income = Column(Integer)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    user = relationship("UserAuth", back_populates="client")
    coaches = relationship("Coach", secondary=client_coach_association, back_populates="clients")  # 全担当コーチ（多対多）
    applications = relationship("Application", back_populates="client", cascade="all, delete-orphan")
    appointments = relationship("Appointment", back_populates="client", cascade="all, delete-orphan")
    resumes = relationship("Resume", back_populates="client", cascade="all, delete-orphan")
