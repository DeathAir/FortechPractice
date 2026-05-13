from typing import Union, List

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "ApiPractice"
    debug: bool = True
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/user_auth"
    cors_origins: Union[List[str], str] = [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
    ]
    static_dir: str = "static"

    SECRET_KEY = "123456"
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 7


    class Config:
        env_file = ".env"

settings = Settings()