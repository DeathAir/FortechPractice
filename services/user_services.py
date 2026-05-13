from datetime import datetime
import hashlib

import jwt
from fastapi import HTTPException, status

from config import settings
from sqlalchemy import Select
from sqlalchemy.ext.asyncio import AsyncSession

from models import User
from schemas.user import UserCreate, UserUpdate, UserLogin, RefreshToken


class UserService:
    def __init__(self, db : AsyncSession):
        self.db = db

    async def hash_password(self, password: str) -> str:
        return hashlib.sha256(password.encode()).hexdigest()

    async def verify_password(self, plain_password: str, password_hash: str) -> bool:
        return await self.hash_password(plain_password) == password_hash

    async def check_email_exist(self, email : str) -> bool:
        existing = await self.db.execute(Select(User).where(User.email == email))
        result = existing.scalar()
        return result is not None

    async def create_token(self, email: str):
        expire = datetime.utcnow() + datetime.timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        payload = {"sub": email, "exp": expire, "type": "access"}
        return await jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

    async def create_refresh_token(self, email: str):
        expire = datetime.utcnow() + datetime.timedelta(minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES)
        payload = {"sub": email, "exp": expire, "type": "refresh"}
        return await jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

    async def get_user_by_id(self, id : int) -> User:
        existing = await self.db.execute(Select(User).where(User.id == id))
        result = existing.scalar().one_or_none()

        if result is None:
            raise HTTPException(status_code=404, detail="Пользователь не найден")
        return result

    async def register_user(self, user : UserCreate) -> UserCreate:

        if await self.check_email_exist(user.email):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Электронная почта уже существует"
            )

        hashed_password = await self.hash_password(user.password)
        New_user = User(
            email=user.email,
            password_hash=hashed_password,
            phone=user.phone,
            fullname=user.fullname,
        )

        access_tocken = self.create_token(New_user.email)
        new_user = New_user
        self.db.add(new_user)
        await self.db.commit()
        await self.db.refresh(new_user)

        return new_user


    async def update_user(self, user : UserUpdate) -> UserUpdate:
        updated_user = User(**user.dict())
        self.db.add(updated_user)
        await self.db.commit()
        await self.db.refresh(updated_user)
        return await updated_user

    async def login_user(self, user: UserLogin) -> UserLogin:
        existing_user = await self.db.execute(Select(User).where(User.email == user.email))
        result = existing_user.scalar_one_or_none()

        if not result:
            raise HTTPException(status_code=401, detail="Неверный email или пароль")

        if not self.verify_password(user.password, existing_user.password_hash):
            raise HTTPException(status_code=401, detail="Неверный email или пароль")


        access_token = self.create_token(user.email)
        return  await {
        "access_token": access_token, "get_login": result
        }




