from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update
from uuid import UUID
from app.models import Job, User
from app.api.utils import get_current_user  # 🔐 get the current user from token
from app.tasks import process_job
from app.db import get_db
from app.models import Job
from app.api.schemas import JobCreate, JobResponse, JobStatusResponse, JobResultResponse
from fastapi import Path
from typing import Literal
router = APIRouter()

@router.post("/", response_model=JobResponse)
async def create_job(
    payload: JobCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user) 
):
    if payload.operation not in ["square_sum", "cube_sum"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid operation"
        )

    job = Job(
        data=payload.data,
        operation=payload.operation,
        status="PENDING",
        user_id=current_user.id  # 🔗 Associate job with user
    )

    db.add(job)
    await db.commit()
    await db.refresh(job)

    # Background task dispatch
    process_job.delay(str(job.id), payload.data, payload.operation)

    return JobResponse(job_id=job.id, status=job.status)



@router.get("/{job_id}/status", response_model=JobStatusResponse)
async def get_job_status(
    job_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)  # 🔐 Require auth
):
    result = await db.execute(select(Job).where(Job.id == job_id))
    job = result.scalar_one_or_none()
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    # 🔒 Make sure job belongs to the logged-in user
    if job.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to view this job")

    return JobStatusResponse(status=job.status)



@router.get("/{job_id}/result", response_model=JobResultResponse)
async def get_job_result(
    job_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)  # 🔐 Require auth
):
    result = await db.execute(select(Job).where(Job.id == job_id))
    job = result.scalar_one_or_none()

    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    # 🔒 Only allow if the job belongs to the current user
    if job.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to access this job result")

    if job.status != "SUCCESS":
        return JobResultResponse(job_id=job.id, status=job.status, result=None)

    return JobResultResponse(job_id=job.id, status=job.status, result=job.result)


@router.get("/{status}/{page_no}")
async def get_my_jobs(
    status: Literal["all", "PENDING", "INPROGRESS", "SUCCESS", "FAILED"] = Path(..., description="Job status to filter"),
    page_no: int = Path(..., ge=1, description="Page number, starting from 1"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    PAGE_SIZE = 10
    offset = (page_no - 1) * PAGE_SIZE

    query = select(Job).where(Job.user_id == current_user.id)

    if status != "all":
        query = query.where(Job.status == status)

    query = query.offset(offset).limit(PAGE_SIZE)
    result = await db.execute(query)
    jobs = result.scalars().all()

    return [
        {
            "job_id": job.id,
            "operation": job.operation,
            "status": job.status,
            "result": job.result,
            "data": job.data
        }
        for job in jobs
    ]
