from pydantic import BaseModel, Field
from typing import List
from uuid import UUID

class JobCreate(BaseModel):
    data: List[float]
    operation: str = Field(..., pattern="^(square_sum|cube_sum)$")

class JobResponse(BaseModel):
    job_id: UUID
    status: str
