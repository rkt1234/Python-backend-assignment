from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID

from app.db import get_db
from app.models import Job
from app.api.schemas import JobCreate, JobResponse

router = APIRouter()

@router.post("/", response_model=JobResponse)
def create_job(payload: JobCreate, db: Session = Depends(get_db)):
    if payload.operation not in ["square_sum", "cube_sum"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid operation"
        )

    job = Job(
        data=payload.data,
        operation=payload.operation,
        status="PENDING"
    )
    db.add(job)
    db.commit()
    db.refresh(job)

    return JobResponse(job_id=job.id, status=job.status)
