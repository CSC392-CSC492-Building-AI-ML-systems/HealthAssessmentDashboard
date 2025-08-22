from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Depends, Header
from typing import List
from app.services.chatbot_service import ChatbotService
from app.services.auth_service import AuthService
from app.db.sqlite import SessionLocal, get_db
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.security import OAuth2PasswordBearer
from fastapi import Cookie

from pydantic import BaseModel

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

# Helper function to get chatbot service
async def get_chatbot_service(db: AsyncSession = Depends(get_db)) -> ChatbotService:
    async with db as session:
        return ChatbotService(session)

# Create a new chat session
@router.post("/sessions")
async def create_chat(
    title: str = Form(...),
    user_id: str = Form(...),
    chatbot_service: ChatbotService = Depends(get_chatbot_service)
):
    try:
        # user_id = chatbot_service.verify_token(refresh_token, "refresh")
        return await chatbot_service.create_chat(user_id, title)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    
# List all chat sessions for a user
@router.get("/sessions")
async def list_chats(
    user_id: int,
    chatbot_service: ChatbotService = Depends(get_chatbot_service)
):
    try:
        return await chatbot_service.get_sessions(user_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

# Get a specific chat session by ID
@router.get("/sessions/{session_id}")
async def get_chat(
    session_id: int,
    user_id: int,
    chatbot_service: ChatbotService = Depends(get_chatbot_service)
):
    try:
        session = await chatbot_service.get_session(session_id, user_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        return session
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

# Rename a chat session
@router.put("/sessions/{session_id}")
async def rename_chat(
    session_id: int,
    user_id: int = Form(...),
    new_title: str = Form(...),
    chatbot_service: ChatbotService = Depends(get_chatbot_service)
):
    try:
        updated = await chatbot_service.rename_session(session_id, user_id, new_title)
        if not updated:
            raise HTTPException(status_code=404, detail="Session not found")
        return {"detail": "Session renamed"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

# Delete a chat session
@router.delete("/sessions/{session_id}")
async def delete_chat(
    session_id: int,
    user_id: int,
    chatbot_service: ChatbotService = Depends(get_chatbot_service)
):
    try:
        success = await chatbot_service.delete_session(session_id, user_id)
        if not success:
            raise HTTPException(status_code=404, detail="Session not found")
        return {"detail": "Session deleted"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    
# ─────────────────────────────────────────────
# Message endpoints
# ─────────────────────────────────────────────

class SendMessageRequest(BaseModel):
    user_id: int
    message: str

# Add messages to a chat session
@router.post("/sessions/{session_id}/messages")
async def send_message(
    session_id: int,
    body: SendMessageRequest,
    chatbot_service: ChatbotService = Depends(get_chatbot_service)
):
    return await chatbot_service.send_message(session_id, body.user_id, body.message)

# Get all messages in a chat session
@router.get("/sessions/{session_id}/messages")
async def get_messages(
    session_id: int,
    user_id: int,
    chatbot_service: ChatbotService = Depends(get_chatbot_service)
):
    try:
        msgs = await chatbot_service.get_messages(session_id, user_id)
        return {"messages": msgs}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


# Upload a context file for a chat session
@router.post("/sessions/{session_id}/upload")
async def upload_context(
    session_id: int,
    user_id: int = Form(...),
    file: UploadFile = File(...),
    chatbot_service: ChatbotService = Depends(get_chatbot_service)
):
    try:
        success = await chatbot_service.upload_context_file(session_id, user_id, file)
        if not success:
            raise HTTPException(status_code=400, detail="Upload failed")
        return {"detail": "File uploaded"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))