from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from app.core.config import settings

client: AsyncIOMotorClient | None = None

async def connect() -> None:
    global _client
    _client = AsyncIOMotorClient(settings.mongo_uri)
    await init_beanie(
        database=_client[settings.mongo_db],
        document_models=[],
    )

async def close() -> None:
    client.close()

def get_mongo_client() -> AsyncIOMotorClient | None:
    return _client
