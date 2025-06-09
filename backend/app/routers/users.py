from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.db.mongo import get_mongo_client
from app.core.config import settings
from app.models.user import User
from app.db.sqlite import SessionLocal

router = APIRouter()

async def get_db():
    async with SessionLocal() as session:
        yield session

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

# MONGO TEST ENDPOINT
@router.get("/mongo/ping")
async def mongo_test():
    client = get_mongo_client()
    if client is None:
        return {"status": "Mongo client not connected"}
    
    try:
        db = client[settings.mongo_db]  # ← use settings
        collections = await db.list_collection_names()
        return {"status": "OK", "collections": collections}
    except Exception as e:
        return {"status": "Error", "details": str(e)}


