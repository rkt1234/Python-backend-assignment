import uuid
from sqlalchemy import Column, String, Float, ARRAY
from sqlalchemy.dialects.postgresql import UUID
from app.db import Base

class Job(Base):
    __tablename__ = "jobs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    status = Column(String, default="PENDING")
    operation = Column(String)  # "square_sum" or "cube_sum"
    data = Column(ARRAY(Float))  # list of numbers
    result = Column(Float)  # single number as result
