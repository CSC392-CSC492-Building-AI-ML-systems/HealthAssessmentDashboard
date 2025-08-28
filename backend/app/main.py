from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.db.sqlite import init_db as sqlite_init
from app.routers import users, auth, chatbot, organizations, users_drugs
from app.core.config import settings
import app.models

@asynccontextmanager
async def lifespan(app: FastAPI):
    await sqlite_init()
    yield

app = FastAPI(title=settings.app_name, lifespan=lifespan, debug=settings.debug)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(users.router, prefix="/users", tags=["users"])
app.include_router(chatbot.router, prefix="/chat", tags=["chat"])
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(organizations.router, prefix="/organizations", tags=["organizations"])
app.include_router(organizations.router, prefix="/user-drugs", tags=["user-drugs"])