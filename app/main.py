from fastapi import FastAPI
from app.api.routes import router as job_router
from app.db import Base, engine
import app.db
from app.models import Job 

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(job_router, prefix="/jobs", tags=["Jobs"])

@app.get("/", tags=["Health"])
def health_check():
    return {"message": "Backend is running"}
