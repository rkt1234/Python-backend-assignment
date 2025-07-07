from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional
from uuid import UUID

# ==== Job Schemas ====

class JobCreate(BaseModel):
    data: List[float]
    operation: str = Field(..., pattern="^(square_sum|cube_sum)$")

class JobResponse(BaseModel):
    job_id: UUID
    status: str

class JobStatusResponse(BaseModel):
    status: str

class JobResultResponse(BaseModel):
    job_id: UUID
    result: Optional[float]
    status: str

# ==== User Schemas ====

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str

class UserCreateResponse(BaseModel):
    token: Optional[str] = None
    message: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserLoginResponse(BaseModel):
    token: Optional[str] = None
    message: str
