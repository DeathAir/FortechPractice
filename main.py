from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

import api
from config import settings

app = FastAPI(title=settings.PROJECT_NAME,
              debug=settings.DEBUG,
              )

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(api.v1.user)
