import asyncio
from app.models import Job
from app.db import SessionLocal
from app.celery_worker import celery_app

@celery_app.task
def process_job(job_id: str, data: list, operation: str):
    db = SessionLocal()
    job = db.query(Job).filter(Job.id == job_id).first()

    if not job:
        return

    job.status = "IN_PROGRESS"
    db.commit()

    try:
        # Simulate delay
        asyncio.run(asyncio.sleep(2))

        if operation == "square_sum":
            result = sum([x**2 for x in data])
        elif operation == "cube_sum":
            result = sum([x**3 for x in data])
        else:
            raise ValueError("Unsupported operation")

        job.result = result
        job.status = "SUCCESS"
    except Exception:
        job.status = "FAILED"
        job.result = None
    finally:
        db.commit()
        db.close()
