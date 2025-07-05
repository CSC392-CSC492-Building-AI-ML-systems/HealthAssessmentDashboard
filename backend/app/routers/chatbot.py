from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Depends
from typing import List
from app.services.chatbot_service import ChatbotService
from app.db.sqlite import SessionLocal, get_db
from sqlalchemy.ext.asyncio import AsyncSession


router = APIRouter()

# Create a new chat session
@router.post("/sessions")
async def create_chat(
    user_id: int = Form(...),
    title: str = Form(...),
    db: AsyncSession = Depends(get_db)
):
    service = ChatbotService(db)
    session = await service.create_chat(user_id, title)
    return session

# List all chat sessions for a user
@router.get("/sessions")
async def list_chats(
    user_id: int,
    db: AsyncSession = Depends(get_db)
):
    service = ChatbotService(db)
    return await service.get_sessions(user_id)

# Get a specific chat session by ID
@router.get("/sessions/{session_id}")
async def get_chat(
    session_id: int,
    user_id: int,
    db: AsyncSession = Depends(get_db)
):
    service = ChatbotService(db)
    session = await service.get_session(session_id, user_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session

# Rename a chat session
@router.put("/sessions/{session_id}")
async def rename_chat(
    session_id: int,
    user_id: int = Form(...),
    new_title: str = Form(...),
    db: AsyncSession = Depends(get_db)
):
    service = ChatbotService(db)
    updated = await service.rename_session(session_id, user_id, new_title)
    if not updated:
        raise HTTPException(status_code=404, detail="Session not found")
    return {"detail": "Session renamed"}

# Delete a chat session
async def delete_chat(
    session_id: int,
    user_id: int,
    db: AsyncSession = Depends(get_db)
):
    service = ChatbotService(db)
    success = await service.delete_session(session_id, user_id)
    if not success:
        raise HTTPException(status_code=404, detail="Session not found")
    return {"detail": "Session deleted"}
    
# ─────────────────────────────────────────────
# Message endpoints
# ─────────────────────────────────────────────

# Add messages to a chat session
@router.post("/sessions/{session_id}/messages")
async def send_message(
    session_id: int,
    user_id: int = Form(...),
    message: str = Form(...),
    db: AsyncSession = Depends(get_db)
):
    service = ChatbotService(db)
    try:
        return await service.send_message(session_id, user_id, message)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

# Get all messages in a chat session
@router.get("/sessions/{session_id}/messages")
async def get_messages(
    session_id: int,
    user_id: int,
    db: AsyncSession = Depends(get_db)
):
    service = ChatbotService(db)
    try:
        msgs = await service.get_messages(session_id, user_id)
        return {"messages": msgs}
    except ValueError:
        raise HTTPException(status_code=404, detail="Session not found")


# Upload a context file for a chat session
@router.post("/sessions/{session_id}/upload")
async def upload_context(
    session_id: int,
    user_id: int = Form(...),
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
):
    service = ChatbotService(db)
    success = service.upload_context_file(session_id, user_id, file)
    if not success:
        raise HTTPException(status_code=400, detail="Upload failed")
    return {"detail": "File uploaded"}