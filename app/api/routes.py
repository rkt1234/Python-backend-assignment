from fastapi import APIRouter

router = APIRouter()

@router.get("/sample")
def sample_route():
    return {"message": "Jobs API is live"}
