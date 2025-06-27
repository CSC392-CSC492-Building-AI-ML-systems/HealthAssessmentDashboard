from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.db.mongo import connect as mongo_connect, close as mongo_close
from app.db.sqlite import init_db as sqlite_init
from app.routers import users, auth
import app.models

@asynccontextmanager
async def lifespan(app: FastAPI):
    await mongo_connect()
    await sqlite_init()
    yield
    await mongo_close()

app = FastAPI(title="OurPATHS API", lifespan=lifespan)
app.include_router(users.router, prefix="/users", tags=["users"])
app.include_router(auth.router, prefix="/auth", tags=["auth"])
