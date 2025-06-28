from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.db.mongo import get_mongo_client
from app.core.config import settings
from app.models.user import User
from app.db.sqlite import SessionLocal, get_db

router = APIRouter()

# Create a User
@router.post("/")
async def create_user(
    name: str,
    email: str,
    db: AsyncSession = Depends(get_db)):
    user = User(name=name, email=email)
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user

# Get a User
@router.get("/")
async def list_users(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User))
    return result.scalars().all()