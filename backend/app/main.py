from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.db.sqlite import init_db as sqlite_init
from app.routers import users, auth, chatbot
import app.models

@asynccontextmanager
async def lifespan(app: FastAPI):
    await sqlite_init()
    yield

app = FastAPI(title="OurPATHS API", lifespan=lifespan)
app.include_router(users.router, prefix="/users", tags=["users"])
app.include_router(chatbot.router, prefix="/chat", tags=["chat"])
app.include_router(auth.router, prefix="/auth", tags=["auth"])