from app.core.config import settings
from http.client import HTTPException
from backend.app.db.mongo import get_mongo_client


def get_chat_collection():
    client = get_mongo_client()
    if client is None:
        raise HTTPException(status_code=500, detail="MongoDB not connected")
    return client[settings.mongo_db]["chat_sessions"]

# Placeholder
async def generate_bot_response(user_msg: dict):
    # LLM logic
    return "", []

async def ingest_user_file(session_id: str, user_id: int, file_path: str):
    # Ingest and embed the file for retrieval
    pass