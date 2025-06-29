import uuid
from datetime import datetime
from fastapi import UploadFile
from typing import List, Optional
from pymongo.collection import Collection
from app.db.mongo import get_mongo_client
from app.core.config import settings

class ChatbotService:
    def __init__(self):
        self.collection: Collection = get_mongo_client()[settings.mongo_db]["chat_sessions"]

    def create_chat(self, user_id: int, title: str) -> dict:
        session_id = str(uuid.uuid4())
        doc = {
            "session_id": session_id,
            "user_id": user_id,
            "title": title,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "messages": []
        }
        self.collection.insert_one(doc)
        return doc

    def get_sessions(self, user_id: int) -> List[dict]:
        """Retrieve all chat sessions for a specific user"""
        return list(self.collection.find({"user_id": user_id}))

    def get_session(self, session_id: str, user_id: int) -> Optional[dict]:
        """Retrieve a specific chat session by session_id and user_id"""
        return self.collection.find_one({"session_id": session_id, "user_id": user_id})

    def rename_session(self, session_id: str, user_id: int, new_title: str) -> Optional[dict]:
        """Rename a chat session by updating its title"""
        result = self.collection.update_one(
            {"session_id": session_id, "user_id": user_id},
            {"$set": {"title": new_title, "updated_at": datetime.utcnow()}}
        )
        if result.modified_count == 0:
            return None
        return self.get_session(session_id, user_id)

    def delete_session(self, session_id: str, user_id: int) -> bool:
        """Delete a chat session by session_id and user_id"""
        result = self.collection.delete_one({"session_id": session_id, "user_id": user_id})
        return result.deleted_count > 0

    def send_message(self, session_id: str, user_id: int, message: str) -> dict:
        """Send a message in a chat session and return the bot's response"""
        session = self.get_session(session_id, user_id)
        if not session:
            raise ValueError("Session not found")

        user_msg = {
            "role": "user",
            "content": message,
            "timestamp": datetime.utcnow()
        }
        self.collection.update_one(
            {"session_id": session_id, "user_id": user_id},
            {"$push": {"messages": user_msg}}
        )

        # TODO: Implement actual bot response logic involves implementing the 
        # RAG pipeline and LLM response generation - OUR-45
        
        bot_msg = {
            "role": "assistant",
            "content": f"Bot received: '{message}'",
            "timestamp": datetime.utcnow()
        }
        self.collection.update_one(
            {"session_id": session_id, "user_id": user_id},
            {"$push": {"messages": bot_msg}}
        )

        return {"user_message": user_msg["content"], "bot_response": bot_msg["content"]}

    def get_messages(self, session_id: str, user_id: int) -> List[dict]:
        """Retrieve all messages in a chat session"""
        session = self.get_session(session_id, user_id)
        if not session:
            raise ValueError("Session not found")
        return session.get("messages", [])

    def upload_context_file(self, session_id: str, user_id: int, file: UploadFile) -> bool:
        """Upload a context file for a chat session"""
        # Save the file and optionally extract content or embeddings
        return True  # Placeholder