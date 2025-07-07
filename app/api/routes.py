from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update
from uuid import UUID

from app.tasks import process_job
from app.db import get_db
from app.models import Job
from app.api.schemas import JobCreate, JobResponse, JobStatusResponse, JobResultResponse

router = APIRouter()

@router.post("/", response_model=JobResponse)
async def create_job(payload: JobCreate, db: AsyncSession = Depends(get_db)):
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
    await db.commit()
    await db.refresh(job)

    # Dispatch background processing
    process_job.delay(str(job.id), payload.data, payload.operation)

    return JobResponse(job_id=job.id, status=job.status)


@router.get("/{job_id}/status", response_model=JobStatusResponse)
async def get_job_status(job_id: UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Job).where(Job.id == job_id))
    job = result.scalar_one_or_none()
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    return JobStatusResponse(status=job.status)


@router.get("/{job_id}/result", response_model=JobResultResponse)
async def get_job_result(job_id: UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Job).where(Job.id == job_id))
    job = result.scalar_one_or_none()

    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    if job.status != "SUCCESS":
        return JobResultResponse(job_id=job.id, status=job.status, result=None)

    return JobResultResponse(job_id=job.id, status=job.status, result=job.result)
