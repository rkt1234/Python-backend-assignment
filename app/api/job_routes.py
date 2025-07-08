from fastapi import APIRouter, Depends, HTTPException, status, Request, Path
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update
from typing import Literal
from uuid import UUID
from datetime import datetime, timedelta
from app.api.rate_limiter import is_rate_limited  # update path
from app.db import get_db
from app.models import Job, User
from app.api.utils import get_current_user
from app.tasks import process_job
from app.api.schemas import JobCreate, JobResponse, JobStatusResponse, JobResultResponse

router = APIRouter()

#   Rate-limited job creation
@router.post("/", response_model=JobResponse)
async def create_job(
    request: Request,
    payload: JobCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if await is_rate_limited(str(current_user.id)):
        raise HTTPException(status_code=429, detail="Rate limit exceeded. Try again in a minute.")

    if payload.operation not in ["square_sum", "cube_sum"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid operation"
        )

    job = Job(
        data=payload.data,
        operation=payload.operation,
        status="PENDING",
        user_id=current_user.id
    )

    db.add(job)
    await db.commit()
    await db.refresh(job)

    process_job.delay(str(job.id), payload.data, payload.operation)

    return JobResponse(job_id=job.id, status=job.status)



#   Other routes remain unchanged

@router.get("/{job_id}/status", response_model=JobStatusResponse)
async def get_job_status(
    job_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(
        select(Job).where(Job.id == job_id, Job.is_deleted == False)
    )
    job = result.scalar_one_or_none()

    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    if job.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to view this job")

    return JobStatusResponse(status=job.status)


@router.get("/{job_id}/result", response_model=JobResultResponse)
async def get_job_result(
    job_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(
        select(Job).where(Job.id == job_id, Job.is_deleted == False)
    )
    job = result.scalar_one_or_none()

    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    if job.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to access this job result")
    if job.status != "SUCCESS":
        return JobResultResponse(job_id=job.id, status=job.status, result=None)

    return JobResultResponse(job_id=job.id, status=job.status, result=job.result)


@router.get("/{status}/{page_no}")
async def get_my_jobs(
    status: Literal["all", "PENDING", "INPROGRESS", "SUCCESS"] = Path(...),
    page_no: int = Path(..., ge=1),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    PAGE_SIZE = 10
    offset = (page_no - 1) * PAGE_SIZE

    query = select(Job).where(Job.user_id == current_user.id, Job.is_deleted == False)
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


@router.post("/cleanup/success-jobs")
async def cleanup_successful_jobs(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")

    one_day_ago = datetime.utcnow() - timedelta(days=1)
    stmt = (
        update(Job)
        .where(Job.status == "SUCCESS", Job.is_deleted == False, Job.created_at < one_day_ago)
        .values(is_deleted=True)
    )

    result = await db.execute(stmt)
    await db.commit()

    return {"message": "Cleanup completed", "rows_updated": result.rowcount}
