from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.tasks import process_job
from app.db import get_db
from app.models import Job
from app.api.schemas import JobCreate, JobResponse

router = APIRouter()

@router.post("/", response_model=JobResponse)
async def create_job(payload: JobCreate, db: Session = Depends(get_db)):
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

    # Dispatch background processing
    process_job.delay(str(job.id), payload.data, payload.operation)

    return JobResponse(job_id=job.id, status=job.status)
