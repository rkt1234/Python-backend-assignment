from fastapi import FastAPI
from app.api.routes import router as job_router
from app.db import Base, engine
from app.models import Job
import asyncio

app = FastAPI()

# Create tables asynchronously
@app.on_event("startup")
async def on_startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("✅ Tables created")

# Include the router
app.include_router(job_router, prefix="/jobs", tags=["Jobs"])

# Health check route
@app.get("/", tags=["Health"])
async def health_check():
    return {"message": "Backend is running"}
