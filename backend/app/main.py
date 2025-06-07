from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.db.sqlite import init_db as sqlite_init
from app.routers import users

@asynccontextmanager
async def lifespan(app: FastAPI):
    await sqlite_init()
    yield

app = FastAPI(title="OurPATHS API", lifespan=lifespan)
app.include_router(users.router, prefix="/users", tags=["users"])
