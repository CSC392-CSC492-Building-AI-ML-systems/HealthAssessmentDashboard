from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class ChatSessionBase(BaseModel):
    title: Optional[str] = None

class ChatSessionCreate(ChatSessionBase):
    user_id: int

class ChatSessionResponse(ChatSessionBase):
    session_id: str
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

class ChatSessionUpdate(BaseModel):
    title: str

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    user_message: str
    bot_response: str

class Message(BaseModel):
    role: str
    content: str

class ChatHistory(BaseModel):
    messages: List[Message]