from fastapi import UploadFile
from app.models.user import User
from app.models.chat_message import ChatMessage
from app.models.chat_history import ChatHistory
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from app.rag_pipeline.intent_classifier.intent_classifier import intent_classifier
from typing import List, Dict, Any
from app.models.enums import IntentEnum
from app.services.agent_tools import (
    cda_retriever,
    user_retriever,
    price_rec_service,
    timeline_rec_service,
)



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
    
    async def call_tools(self, query: str) -> List[Dict[str, Any]]:
        """Route *query* to the appropriate tools based on classified intents.

        The function executes the following high-level flow:

            1. Use the intent classifier to detect which tools are required.
            2. For each intent, invoke the matching tool in the correct order.
               • USER_VECTORDB and/or CDA_VECTORDB are retrievers returning
                 metadata (list of dictionaries).
               • PRICE_REC_SERVICE is an ML service that depends on metadata
                 returned from a retriever; therefore it is executed after
                 the relevant retriever to build its input.
               • TIMELINE_REC_SERVICE is independent and can be called at any
                 point.
            3. Collect every individual tool response inside *responses*.
            4. Return the list of responses.

        The return value is a list of dictionaries, each having the shape:
            {
                "intent": IntentEnum value,
                "response": <tool-specific output>,
            }
        """
        # 1) Classify the query.
        intents = intent_classifier(query)
        if not intents:
            return []  # nothing to do

        # 2) Establish order of execution of the tools
        ordered_intents = [
            IntentEnum.USER_VECTORDB,
            IntentEnum.CDA_VECTORDB,
            IntentEnum.PRICE_REC_SERVICE,
            IntentEnum.TIMELINE_REC_SERVICE,
        ]
        execution_plan = [i for i in ordered_intents if i in intents]

        responses: List[Dict[str, Any]] = []
        user_metadata: List[Dict[str, Any]] | None = None
        cda_metadata: List[Dict[str, Any]] | None = None

        for intent in execution_plan:
            if intent == IntentEnum.USER_VECTORDB:
                user_metadata = user_retriever.query(query)
                responses.append({"intent": intent, "response": user_metadata})

            elif intent == IntentEnum.CDA_VECTORDB:
                cda_metadata = cda_retriever.query(query)
                responses.append({"intent": intent, "response": cda_metadata})

            elif intent == IntentEnum.PRICE_REC_SERVICE:
                # Metadata from the USER vector-DB; fall back to CDA if USER is not available
                data_source = user_metadata or cda_metadata or {}
                # TODO: Structure the data_source into the structure expected by the ML model.
                prediction = price_rec_service.predict({"metadata": data_source})
                responses.append({"intent": intent, "response": prediction})

            elif intent == IntentEnum.TIMELINE_REC_SERVICE:
                timeline_data = timeline_rec_service.query(query)
                responses.append({"intent": intent, "response": timeline_data})

        return responses
        
