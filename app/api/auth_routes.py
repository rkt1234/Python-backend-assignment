from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.db import get_db
from app.models import User
from app.api.schemas import UserCreate, UserCreateResponse, UserLogin, UserLoginResponse
from app.api.utils import hash_password, verify_password, create_access_token

router = APIRouter()


@router.post("/register", response_model=UserCreateResponse)
async def register_user(payload: UserCreate, db: AsyncSession = Depends(get_db)):
    # Check if email already exists
    result = await db.execute(select(User).where(User.email == payload.email))
    existing_user = result.scalar_one_or_none()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Create and store new user
    hashed_pw = hash_password(payload.password)
    new_user = User(name=payload.name, email=payload.email, password=hashed_pw, role=payload.role)
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    # Generate JWT token
    token = create_access_token({"sub": str(new_user.id)})

    return UserCreateResponse(token=token, message="User registered successfully")


@router.post("/login", response_model=UserLoginResponse)
async def login_user(payload: UserLogin, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == payload.email))
    user = result.scalar_one_or_none()

    if not user or not verify_password(payload.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    token = create_access_token({"sub": str(user.id)})

    return UserLoginResponse(token=token, message="Login successful")
