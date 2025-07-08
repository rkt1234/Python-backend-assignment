from fastapi import FastAPI, Request
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from app.api.job_routes import router as job_router
from app.api.auth_routes import router as auth_router
from app.db import Base, engine
from app.api.utils import get_current_user

# 👇 Define key_func for per-user rate limiting
def user_id_key_func(request: Request):
    user = getattr(request.state, "user", None)
    return str(user.id) if user else request.client.host

# 👇 Set up limiter with user-based key function
limiter = Limiter(key_func=user_id_key_func)

# 👇 FastAPI app setup
app = FastAPI()
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# 👇 Inject current_user into request.state for use in key_func
@app.middleware("http")
async def add_user_to_request(request: Request, call_next):
    try:
        # Use the same get_current_user function already defined in utils.py
        user = await get_current_user(request)
        request.state.user = user
    except Exception:
        request.state.user = None
    return await call_next(request)

# 👇 Create tables on startup
@app.on_event("startup")
async def on_startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("✅ Tables created")

# 👇 Include routers
app.include_router(job_router, prefix="/jobs", tags=["Jobs"])
app.include_router(auth_router, prefix="/auth", tags=["Auth"])

# 👇 Health check
@app.get("/", tags=["Health"])
async def health_check():
    return {"message": "Backend is running"}
