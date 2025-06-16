from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from typing import List, Optional
from datetime import datetime
import os, uuid, shutil
from app.core.config import settings
from app.db.mongo import get_mongo_client
from app.models.chatbot import (
    StartChatRequest,
    RenameChatRequest,
    SendMessageResponse,
    ChatbotResponse,
    UploadContextResponse,
    RenameChatResponse,
    DeleteChatResponse
)

router = APIRouter()
UPLOAD_DIR = "./uploaded_files"
os.makedirs(UPLOAD_DIR, exist_ok=True)

def get_chat_collection():
    client = get_mongo_client()
    if client is None:
        raise HTTPException(status_code=500, detail="MongoDB not connected")
    return client[settings.mongo_db]["chat_sessions"]

@router.post("/chat/start")
async def create_chat(request: StartChatRequest):
    collection = get_chat_collection()
    session_id = str(uuid.uuid4())
    chat = {
        "session_id": session_id,
        "user_id": request.user_id,
        "title": request.title,
        "created_at": datetime.utcnow(),
        "messages": []
    }
    await collection.insert_one(chat)
    return {"session_id": session_id, "title": request.title}

@router.post("/chat/{session_id}/message", response_model=SendMessageResponse)
async def post_user_message(
    session_id: str,
    user_id: int = Form(...),
    message: str = Form(...),
    files: Optional[List[UploadFile]] = File(None),
):
    collection = get_chat_collection()
    attachments = []

    if files:
        for file in files:
            unique_name = f"{user_id}_{uuid.uuid4()}_{file.filename}"
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

@router.post("/chat/{session_id}/chatbot-respond", response_model=ChatbotResponse)
async def get_chatbot_reply(session_id: str, user_id: int):
    collection = get_chat_collection()
    chat = await collection.find_one({"session_id": session_id, "user_id": user_id})
    if not chat or not chat.get("messages"):
        raise HTTPException(status_code=404, detail="No chat or messages found")

    last_msg = chat["messages"][-1]
    if last_msg["sender"] != "user":
        raise HTTPException(status_code=400, detail="Last message is not a user query")

    response_text, sources = await generate_bot_response(last_msg)  # Placeholder for OUR-45

    bot_msg = {
        "sender": "assistant",
        "message": response_text,
        "timestamp": datetime.utcnow(),
        "attachments": [],
        "sources": sources
    }

    await collection.update_one(
        {"session_id": session_id, "user_id": user_id},
        {"$push": {"messages": bot_msg}},
    )
    return {"response": bot_msg}

@router.post("/chat/{session_id}/upload-context", response_model=UploadContextResponse)
async def upload_context_data(session_id: str, user_id: int, file: UploadFile = File(...)):
    filepath = f"{UPLOAD_DIR}/context_{user_id}_{uuid.uuid4()}_{file.filename}"
    with open(filepath, "wb") as f:
        shutil.copyfileobj(file.file, f)

    await ingest_user_file(session_id, user_id, filepath)  # Placeholder for OUR-45
    return {"status": "Context uploaded", "filename": file.filename}

@router.get("/chat/{session_id}/messages")
async def get_messages_by_session(session_id: str, user_id: int):
    collection = get_chat_collection()
    chat = await collection.find_one({"session_id": session_id, "user_id": user_id})
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")
    return chat.get("messages", [])

@router.get("/chat/sessions")
async def get_chat_sessions(user_id: int):
    collection = get_chat_collection()
    chats = await collection.find({"user_id": user_id}).to_list(length=100)
    return [{"session_id": chat["session_id"], "title": chat["title"], "created_at": chat["created_at"]} for chat in chats]

@router.put("/chat/{session_id}/rename", response_model=RenameChatResponse)
async def update_chat_title(session_id: str, request: RenameChatRequest):
    collection = get_chat_collection()
    result = await collection.update_one(
        {"session_id": session_id, "user_id": request.user_id},
        {"$set": {"title": request.new_title}}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Chat not found")
    return {"status": "Renamed", "new_title": request.new_title}

@router.delete("/chat/{session_id}", response_model=DeleteChatResponse)
async def delete_chat(session_id: str, user_id: int):
    collection = get_chat_collection()
    result = await collection.delete_one({"session_id": session_id, "user_id": user_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Chat not found")
    return {"status": "Deleted"}
