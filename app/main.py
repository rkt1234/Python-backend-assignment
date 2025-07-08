from fastapi import FastAPI, Request
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from app.api.job_routes import router as job_router
from app.api.auth_routes import router as auth_router
from app.db import Base, engine
from app.api.utils import get_current_user
from fastapi.openapi.utils import get_openapi

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
    print("  Tables created")

# 👇 Include routers
app.include_router(job_router, prefix="/jobs", tags=["Jobs"])
app.include_router(auth_router, prefix="/auth", tags=["Auth"])

# 👇 Health check
@app.get("/", tags=["Health"])
async def health_check():
    return {"message": "Backend is running"}

# ✅ Custom OpenAPI for Swagger UI with Bearer Auth support (excluding login/register)
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title="My API",
        version="1.0.0",
        description="API with JWT Bearer auth in Swagger UI",
        routes=app.routes,
    )

    # Define Bearer security scheme
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT"
        }
    }

    # Exclude these endpoints from requiring Bearer auth
    exclude_paths = ["/auth/login", "/auth/register"]

    for path, methods in openapi_schema["paths"].items():
        if path not in exclude_paths:
            for method in methods.values():
                method.setdefault("security", []).append({"BearerAuth": []})

    app.openapi_schema = openapi_schema
    return app.openapi_schema

# ✅ Assign the custom OpenAPI generator to FastAPI app
app.openapi = custom_openapi
