from sqlalchemy import Column, String, DateTime, ForeignKey, Text, Integer
from sqlalchemy import Uuid as UUID
from sqlalchemy.sql import func
import uuid
from app.database import Base


class File(Base):
    __tablename__ = "files"

    file_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    related_type = Column(String(50), nullable=False, index=True)  # 'client' or 'application'
    related_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    file_name = Column(String(255), nullable=False)
    file_path = Column(Text, nullable=False)
    file_size = Column(Integer)
    uploaded_by = Column(UUID(as_uuid=True), ForeignKey("users_auth.user_id"))
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())
