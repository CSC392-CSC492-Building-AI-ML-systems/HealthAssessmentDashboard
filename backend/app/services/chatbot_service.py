from fastapi import UploadFile
from app.models.user import User
from app.models.chat_message import ChatMessage
from app.models.chat_history import ChatHistory
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete


class ChatbotService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def _get_user(self, user_id: int) -> User:
        """Helper to get and validate user existence."""
        result = await self.db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if not user:
            raise ValueError("User not found")
        return user

    async def _get_session(self, session_id: int, user_id: int) -> ChatHistory:
        """Helper to get and validate chat session existence."""
        result = await self.db.execute(
            select(ChatHistory).where(
                ChatHistory.id == session_id,
                ChatHistory.user_id == user_id
            )
        )
        session = result.scalar_one_or_none()
        if not session:
            raise ValueError("Session not found")
        return session

    async def create_chat(self, user_id: int, title: str):
        """Create a new chat session for a user"""
        # Validate user exists
        await self._get_user(user_id)
        
        chat = ChatHistory(chat_summary=title, user_id=user_id)
        self.db.add(chat)
        await self.db.commit()
        await self.db.refresh(chat)
        return chat

    async def get_sessions(self, user_id: int):
        """Retrieve all chat sessions for a specific user"""
        # Validate user exists
        await self._get_user(user_id)

        result = await self.db.execute(
            select(ChatHistory).where(ChatHistory.user_id == user_id)
        )
        return result.scalars().all()

    async def get_session(self, session_id: int, user_id: int):
        """Retrieve a specific chat session by session_id and user_id"""
        # Validate user exists
        await self._get_user(user_id)
        
        # Get and validate session
        return await self._get_session(session_id, user_id)

    async def rename_session(self, session_id: int, user_id: int, new_title: str):
        """Rename a chat session by updating its title"""
        # Validate both user and session exist
        await self._get_user(user_id)
        await self._get_session(session_id, user_id)

        result = await self.db.execute(
            update(ChatHistory)
            .where(ChatHistory.id == session_id, ChatHistory.user_id == user_id)
            .values(chat_summary=new_title)
            .execution_options(synchronize_session="fetch")
        )
        await self.db.commit()
        return result.rowcount > 0

    async def delete_session(self, session_id: int, user_id: int):
        """Delete a chat session by session_id and user_id"""
        # Validate both user and session exist
        await self._get_user(user_id)
        await self._get_session(session_id, user_id)

        result = await self.db.execute(
            delete(ChatHistory).where(ChatHistory.id == session_id, ChatHistory.user_id == user_id)
        )
        await self.db.commit()
        return result.rowcount > 0

    async def send_message(self, session_id: int, user_id: int, message: str):
        """Send a message in a chat session and return the bot's response"""
        # Validate both user and session exist
        await self._get_user(user_id)
        session = await self._get_session(session_id, user_id)

        user_msg = ChatMessage(
            role="USER",
            content=message,
            chat_history_id=session_id
        )
        self.db.add(user_msg)

        # TODO: Implement actual bot response logic involves implementing the 
        # RAG pipeline and LLM response generation - OUR-45

        bot_msg = ChatMessage(
            role="ASSISTANT",
            content=f"Bot received: '{message}'",
            chat_history_id=session_id
        )
        self.db.add(bot_msg)
        await self.db.commit()

        return {"user_message": user_msg.content, "bot_response": bot_msg.content}

    async def get_messages(self, session_id: int, user_id: int):
        """Retrieve all messages in a chat session"""
        # Validate both user and session exist
        await self._get_user(user_id)
        await self._get_session(session_id, user_id)

        result = await self.db.execute(
            select(ChatMessage)
            .where(ChatMessage.chat_history_id == session_id)
            .order_by(ChatMessage.created_at)
        )
        return result.scalars().all()

    async def upload_context_file(self, session_id: int, user_id: int, file: UploadFile) -> bool:
        """Upload a context file for a chat session"""
        # Validate both user and session exist
        await self._get_user(user_id)
        await self._get_session(session_id, user_id)

        # Save the file and optionally extract content or embeddings
        return True  # Placeholder