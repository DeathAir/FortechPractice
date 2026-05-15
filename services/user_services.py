from datetime import datetime, timedelta, timezone
import hashlib
import bcrypt
from jose import jwt
from fastapi import HTTPException, status

from config import settings
from sqlalchemy import Select
from sqlalchemy.ext.asyncio import AsyncSession

from models import User
from models.user import AuditLog

from schemas.user import UserCreate, UserUpdate, UserLogin


class UserService:
    def __init__(self, db : AsyncSession):
        self.db = db

    @staticmethod
    def create_token(email: str) -> str:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        payload = {"sub": email, "exp": expire, "type": "access"}
        return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

    @staticmethod
    def create_refresh_token(email: str) -> str:
        expire = datetime.utcnow() + timedelta(minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES)
        payload = {"sub": email, "exp": expire, "type": "refresh"}
        return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

    @staticmethod
    def hash_password(password: str) :
        hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        return hashed.decode('utf-8')


    @staticmethod
    def verify_password(plain_password: str, password_hash: str) -> bool:
        return bcrypt.checkpw(plain_password.encode('utf-8'), password_hash.encode('utf-8'))

    async def check_email_exist(self, email : str) -> bool:
        existing = await self.db.execute(Select(User).where(User.email == email))
        result = existing.scalar()
        return result is not None

    async def get_user_by_id(self, id_user : int) -> User:
        result = await self.db.execute(
            Select(User).where(User.id == id_user)
        )
        user = result.scalar_one_or_none()

        if user is None:
            raise HTTPException(status_code=404, detail="Пользователь не найден")
        return user

    async def register_user(self, user : UserCreate) -> User:

        if await self.check_email_exist(user.email):
            Logs = AuditLog(
                user_id= None,
                Actions="USER_REGISTER",
                log_at=datetime.now(timezone.utc),
                Target="auth/register",
                Outcome="Failure "
            )
            logs = Logs
            self.db.add(logs)
            await self.db.commit()
            await self.db.refresh(logs)

            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Электронная почта уже существует"
            )

        hashed_password = self.hash_password(user.password)
        New_user = User(
            email=user.email,
            password_hash=hashed_password,
            phone=user.phone,
            fullname=user.fullname,
        )
        new_user = New_user
        self.db.add(new_user)

        await self.db.flush()

        Logs = AuditLog(
            user_id=new_user.id,
            Actions="USER_REGISTER",
            log_at=datetime.now(timezone.utc),
            Target="auth/register",
            Outcome="Success "
        )

        logs = Logs
        self.db.add(logs)
        await self.db.commit()
        await self.db.refresh(new_user)
        await self.db.refresh(logs)

        access_tocken = self.create_token(New_user.email)

        return new_user


    async def update_user(self, id_user: int, user : UserUpdate) -> User:
        existing_user = await self.db.execute(Select(User).where(User.id == id_user))
        result = existing_user.scalar_one_or_none()
        if result is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Пользователь не найден"
            )
        updated_user = User(**user.dict())
        self.db.add(updated_user)
        await self.db.commit()
        await self.db.refresh(updated_user)
        return updated_user

    async def login_user(self, user: UserLogin) -> dict:
        existing_user = await self.db.execute(Select(User).where(User.email == user.email))
        result = existing_user.scalar_one_or_none()

        if not result:
            Logs = AuditLog(
                user_id=None,
                Actions="LOGIN_FAIL",
                log_at=datetime.now(timezone.utc),
                Target="auth/login",
                Outcome="Failure "
            )
            logs = Logs
            self.db.add(logs)
            await self.db.commit()
            await self.db.refresh(logs)
            raise HTTPException(status_code=401, detail="Неверный email или пароль")

        if not self.verify_password(user.password, result.password_hash):
            Logs = AuditLog(
                user_id=None,
                Actions="LOGIN_FAIL",
                log_at=datetime.now(timezone.utc),
                Target="auth/login",
                Outcome="Failure "
            )
            logs = Logs
            self.db.add(logs)
            await self.db.commit()
            await self.db.refresh(logs)
            raise HTTPException(status_code=401, detail="Неверный email или пароль")


        access_token = self.create_token(user.email)
        Logs = AuditLog(
            user_id=result.id,
            Actions="LOGIN_SUCCESS",
            log_at=datetime.now(timezone.utc),
            Target="auth/login",
            Outcome="Success "
        )

        logs = Logs
        self.db.add(logs)
        await self.db.commit()
        await self.db.refresh(logs)

        return {
            "access_token": access_token,
            "token_type": "bearer",
            "id": result.id,
            "email": result.email,
            "fullname": result.fullname,
            "phone": result.phone,
            "created_at": result.created_at
        }




