from fastapi import FastAPI
from app.api.routes import router as job_router

app = FastAPI()

app.include_router(job_router, prefix="/jobs", tags=["Jobs"])

@app.get("/", tags=["Health"])
def health_check():
    return {"message": "Backend is running"}
