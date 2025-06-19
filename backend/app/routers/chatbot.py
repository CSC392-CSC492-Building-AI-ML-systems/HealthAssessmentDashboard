from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from typing import List
from app.services.chatbot_service import ChatbotService

router = APIRouter()

@router.post("/sessions")
async def create_chat(user_id: int = Form(...), title: str = Form(...)):
    session = ChatbotService().create_chat(user_id, title)
    return session

@router.get("/sessions")
async def list_chats(user_id: int):
    return ChatbotService().get_sessions(user_id)

@router.get("/sessions/{session_id}")
async def get_chat(session_id: str, user_id: int):
    session = ChatbotService().get_session(session_id, user_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session

@router.put("/sessions/{session_id}")
async def rename_chat(session_id: str, user_id: int = Form(...), new_title: str = Form(...)):
    updated = ChatbotService().rename_session(session_id, user_id, new_title)
    if not updated:
        raise HTTPException(status_code=404, detail="Session not found")
    return updated

@router.delete("/sessions/{session_id}")
async def delete_chat(session_id: str, user_id: int):
    success = ChatbotService().delete_session(session_id, user_id)
    if not success:
        raise HTTPException(status_code=404, detail="Session not found")
    return {"detail": "Session deleted"}

@router.post("/sessions/{session_id}/messages")
async def send_message(session_id: str, user_id: int = Form(...), message: str = Form(...)):
    try:
        return ChatbotService().send_message(session_id, user_id, message)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/sessions/{session_id}/messages")
async def get_messages(session_id: str, user_id: int):
    try:
        msgs = ChatbotService().get_messages(session_id, user_id)
        return {"messages": msgs}
    except ValueError:
        raise HTTPException(status_code=404, detail="Session not found")

@router.post("/sessions/{session_id}/upload")
async def upload_context(session_id: str, user_id: int = Form(...), file: UploadFile = File(...)):
    success = ChatbotService().upload_context_file(session_id, user_id, file)
    if not success:
        raise HTTPException(status_code=400, detail="Upload failed")
    return {"detail": "File uploaded"}