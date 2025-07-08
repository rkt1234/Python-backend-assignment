import uuid
from sqlalchemy import Column, DateTime, String, Float, ForeignKey, ARRAY, Boolean, Enum as PgEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.db import Base
from datetime import datetime
import enum
class UserRole(str, enum.Enum):
    user = "user"
    admin = "admin"

class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, nullable=False)
    name = Column(String, nullable=False)
    password = Column(String, nullable=False)
    role = Column(PgEnum(UserRole), default=UserRole.user, nullable=False)
    jobs = relationship("Job", back_populates="user", cascade="all, delete-orphan")

class Job(Base):
    __tablename__ = "jobs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    status = Column(String, default="PENDING")
    operation = Column(String)  # "square_sum" or "cube_sum"
    data = Column(ARRAY(Float))  # list of numbers
    result = Column(Float)  # single number as result
    is_deleted = Column(Boolean, default=False)  # New field added here
    created_at = Column(DateTime, default=datetime.utcnow)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    user = relationship("User", back_populates="jobs")
