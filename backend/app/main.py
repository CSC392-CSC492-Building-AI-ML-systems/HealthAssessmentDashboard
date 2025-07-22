from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.db.sqlite import init_db as sqlite_init
from app.routers import users, auth, chatbot, organizations
import app.models

@asynccontextmanager
async def lifespan(app: FastAPI):
    await sqlite_init()
    yield

app = FastAPI(title="OurPATHS API", lifespan=lifespan)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(users.router, prefix="/users", tags=["users"])
app.include_router(chatbot.router, prefix="/chat", tags=["chat"])
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(organizations.router, prefix="/organizations", tags=["organizations"])