
from typing import Optional
from pydantic import BaseModel


class StartChatRequest(BaseModel):
    user_id: int
    title: Optional[str] = "N/A"

class RenameChatRequest(BaseModel):
    user_id: int
    new_title: str

class SendMessageResponse(BaseModel):
    status: str
    message: dict

class ChatbotResponse(BaseModel):
    response: dict

class UploadContextResponse(BaseModel):
    status: str
    filename: str

class RenameChatResponse(BaseModel):
    status: str
    new_title: str

class DeleteChatResponse(BaseModel):
    status: str