from fastapi import APIRouter, status, Depends, Request
from slowapi import Limiter

from slowapi.util import get_remote_address
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db

from schemas.user import UserResponse, UserCreate, UserLogin, RefreshToken, UserUpdate
from services.user_services import UserService

router = APIRouter(
    tags=["user"]
)
limiter = Limiter(key_func=get_remote_address)

@limiter.limit("5 per minute")
@router.post("/auth/login", response_model=UserResponse, status_code=status.HTTP_200_OK)
async def login(request: Request, user: UserLogin, db : AsyncSession = Depends(get_db)):
    service = UserService(db)
    return await service.login_user(user)


@router.post("/auth/register", response_model=UserResponse, status_code=status.HTTP_200_OK)
async def register(user: UserCreate, db : AsyncSession = Depends(get_db)):
    service = UserService(db)
    return await service.register_user(user)

@router.post("/auth/refresh", response_model=UserResponse, status_code=status.HTTP_200_OK)
async def refresh(refresh_token: RefreshToken, db : AsyncSession = Depends(get_db)):
    service = UserService(db)
    return service.create_refresh_token(refresh_token.email)

@router.get("/users/me", response_model=UserResponse, status_code=status.HTTP_200_OK)
async def me(id_user: int, db: AsyncSession = Depends(get_db)):
    service = UserService(db)
    return await service.get_user_by_id(id_user)

@router.put("/users/me", response_model=UserResponse, status_code=status.HTTP_200_OK)
async def me(id_user : int,user: UserUpdate, db: AsyncSession = Depends(get_db)):
    service = UserService(db)
    return await service.update_user(id_user, user)