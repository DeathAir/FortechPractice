from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware


from api.v1.user import router as user_router

from config import settings

app = FastAPI(title=settings.app_name,
              debug=settings.debug,
              )

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(user_router, prefix="/api/v1/users")
