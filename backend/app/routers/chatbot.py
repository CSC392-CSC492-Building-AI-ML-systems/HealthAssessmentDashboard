from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException
from typing import List, Optional
from datetime import datetime
from bson import ObjectId
import os, uuid, shutil
from app.core.config import settings
from app.db.mongo import get_mongo_client

router = APIRouter()

UPLOAD_DIR = "./uploaded_files"
os.makedirs(UPLOAD_DIR, exist_ok=True)

def get_chat_collection():
    client = get_mongo_client()
    if client is None:
        raise HTTPException(status_code=500, detail="MongoDB not connected")
    return client[settings.mongo_db]["chat_sessions"]

@router.post("/chat/start")
async def start_chat(user_id: int, title: Optional[str] = "Untitled"):
    collection = get_chat_collection()
    session_id = str(uuid.uuid4())
    chat = {
        "session_id": session_id,
        "user_id": user_id,
        "title": title,
        "created_at": datetime.utcnow(),
        "messages": []
    }
    await collection.insert_one(chat)
    return {"session_id": session_id, "title": title}

@router.post("/chat/{session_id}/message")
async def send_message(
    session_id: str,
    user_id: int = Form(...),
    message: str = Form(...),
    files: Optional[List[UploadFile]] = File(None),
):
    collection = get_chat_collection()
    attachments = []

    if files:
        for file in files:
            unique_name = f"{uuid.uuid4()}_{file.filename}"
            path = os.path.join(UPLOAD_DIR, unique_name)
            with open(path, "wb") as f:
                shutil.copyfileobj(file.file, f)
            attachments.append(path)

    msg = {
        "sender": "user",
        "message": message,
        "timestamp": datetime.utcnow(),
        "attachments": attachments
    }

    result = await collection.update_one(
        {"session_id": session_id, "user_id": user_id},
        {"$push": {"messages": msg}},
    )

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Chat session not found")

    return {"status": "Message added", "message": msg}

@router.get("/chat/{session_id}/messages")
async def get_messages(session_id: str, user_id: int):
    collection = get_chat_collection()
    chat = await collection.find_one({"session_id": session_id, "user_id": user_id})
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")
    return chat.get("messages", [])

@router.get("/chat/sessions")
async def list_user_chats(user_id: int):
    collection = get_chat_collection()
    chats = await collection.find({"user_id": user_id}).to_list(length=100)
    return [{"session_id": chat["session_id"], "title": chat["title"], "created_at": chat["created_at"]} for chat in chats]

@router.put("/chat/{session_id}/rename")
async def rename_chat(session_id: str, user_id: int, new_title: str):
    collection = get_chat_collection()
    result = await collection.update_one(
        {"session_id": session_id, "user_id": user_id},
        {"$set": {"title": new_title}}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Chat not found")
    return {"status": "Renamed", "new_title": new_title}

@router.delete("/chat/{session_id}")
async def delete_chat(session_id: str, user_id: int):
    collection = get_chat_collection()
    result = await collection.delete_one({"session_id": session_id, "user_id": user_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Chat not found")
    return {"status": "Deleted"}
