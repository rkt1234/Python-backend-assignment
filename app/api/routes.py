from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.tasks import process_job
from app.db import get_db
from app.models import Job
from app.api.schemas import JobCreate, JobResponse, JobStatusResponse, JobResultResponse
from uuid import UUID

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

@router.get("/{job_id}/status", response_model=JobStatusResponse)
async def get_job_status(job_id: UUID, db: Session = Depends(get_db)):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return JobStatusResponse(status=job.status)


@router.get("/{job_id}/result", response_model=JobResultResponse)
async def get_job_result(job_id: UUID, db: Session = Depends(get_db)):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    if job.status != "SUCCESS":
        return JobResultResponse(job_id=job.id, status=job.status, result=None)

    return JobResultResponse(job_id=job.id, status=job.status, result=job.result)