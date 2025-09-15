from fastapi import UploadFile
from app.models.user import User
from app.models.chat_message import ChatMessage
from app.models.chat_history import ChatHistory
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from app.rag_tools.classifiers.intent_classifier import intent_classifier
from typing import List, Dict, Any, Optional, Tuple
from app.models.enums import IntentEnum
# from app.services.agent_tools import (
#     price_rec_service,
#     timeline_rec_service,
# )
from app.rag_tools.info_retrievers.retriever_service import RetrieverService
from app.rag_tools.info_retrievers.base_retriever import RetrievalResult
# STEP 3 Imports
from app.rag_tools.normalizer import normalize_tool_responses
from app.rag_tools.llm_response_formatter import reformat
from app.core.config import settings
from jose import JWTError, jwt
from app.models.enums import DatabaseEnum


# Configure JWT
SECRET_KEY = settings.jwt_secret_key
ALGORITHM = "HS256"


class ChatbotService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.retriever_service = RetrieverService()

    async def _get_user(self, user_id: int) -> User:
        """Helper to get and validate user existence."""
        print(user_id)
        print("TYPE", type(user_id))
        print("CASTING")
        user_id = int(user_id)
        print("TYPE POST-CAST", type(user_id))
        print("EXECUTING GET USER")
        result = await self.db.execute(select(User).where(User.id == user_id))
        print("EXECUTED GET USER")
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

    async def _get_database(self) -> DatabaseEnum:
        # NOT IMPLEMENTED
        # FOR NOW, SINCE WE CAN'T CLASSIFY BETWEEN USER AND CDA VECTORDB, JUST GET THE CDA VECTORDB
        return DatabaseEnum.CDA_VECTORDB

    async def create_chat(self, user_id: int, title: str):
        """Create a new chat session for a user"""
        # Validate user exists
        await self._get_user(user_id)
        
        chat = ChatHistory(chat_summary=title, user_id=user_id)
        self.db.add(chat)
        await self.db.commit()
        await self.db.refresh(chat)
        print(chat.__dict__)
        return chat

    async def get_sessions(self, user_id: int):
        await self._get_user(user_id)
        result = await self.db.execute(
            select(ChatHistory).where(ChatHistory.user_id == user_id)
        )
        chats = result.scalars().all()

        # Return only id and chat_summary
        return chats

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

    async def verify_token(self, token: str, token_type: str) -> Optional[int]:
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            if payload.get("type") != token_type:
                return None
            user_id = int(payload.get("sub"))
            return user_id
        except JWTError:
            return None

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

        # Current RAG pipeline attempt:
        try:
            # STEP 2
            tool_responses = await self.call_tools(message, user_id)
            print("TOOL RESPONSES")
            print(tool_responses)
            # STEP 3.1: normalizer (passes the same user message as 'query')
            data_dict, prediction = normalize_tool_responses(message, tool_responses)
            print("RETURNED DATA_DICT", data_dict)
            # STEP 3.2: format final LLM answer
            final_text = reformat(message, data_dict, prediction)
        except Exception:
            final_text = ("Sorry, I couldn’t generate a complete answer just now. "
                        "Please try again in a moment.")

        bot_msg = ChatMessage(
            role="ASSISTANT",
            content=final_text,
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
    
    async def call_tools(self, query: str, user_id: int) -> List[Dict[str, Any]]:
        """Route *query* to the appropriate tools based on classified intents.

        The function executes the following high-level flow:

            1. Use the intent classifier to detect which tools are required.
            2. For each intent, invoke the matching tool in the correct order.
               • VECTORDB is a retriever returning metadata (list of dictionaries).
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
        print("Getting intents")
        intents = intent_classifier(query)
        intents = [IntentEnum.VECTORDB]
        print("Got intents", intents)
        intents = [IntentEnum.VECTORDB]
        if not intents:
            return []

        # 2) Establish order of execution of the tools
        ordered_intents = [
            IntentEnum.VECTORDB,
            IntentEnum.PRICE_REC_SERVICE,
            IntentEnum.TIMELINE_REC_SERVICE,
        ]
        execution_plan = [i for i in ordered_intents if i in intents]

        responses: List[Dict[str, Any]] = []
        metadata: List[Dict[str, Any]] | None = None

        for intent in execution_plan:
            if intent == IntentEnum.VECTORDB:
                print("GETTING METADATA")

                # GET CORRECT VECTORDB
                # database_enum = await self._get_database()
                # EDIT: ELECTED TO SELECT TOP k FROM EACH SOURCE AND PASS TO LLM

                # IF INFO CANNOT BE FOUND FROM ONE OF THE SOURCES, IT WILL RETURN NO CHUNKS AND THE OTHER SOURCE'S DATA
                # WILL BE USED INSTEAD AS THE PASSED metadata

                metadata = []

                sources = {
                    "CDA": await self._retrieve_cda_metadata(query),
                    "USER": await self._retrieve_user_metadata(query, user_id),
                }

                for source_name, source_data in sources.items():
                    if source_data:
                        print(f"{source_name} METADATA RECEIVED")
                        metadata.extend(source_data)
                    else:
                        print(f"{source_name} METADATA EMPTY")

                print("METADATA: ", metadata)
                responses.append({"intent": intent, "response": metadata})
            #
            # elif intent == IntentEnum.PRICE_REC_SERVICE:
            #     # Metadata from the USER vector-DB
            #     meta_data = metadata or {}
            #     # TODO: Structure the metadata into the structure expected by the ML model.
            #     prediction = price_rec_service.predict({"metadata": meta_data})
            #     responses.append({"intent": intent, "response": prediction})
            #
            # elif intent == IntentEnum.TIMELINE_REC_SERVICE:
            #     timeline_data = timeline_rec_service.query(query)
            #     responses.append({"intent": intent, "response": timeline_data})

        return responses

    async def _retrieve_cda_metadata(self, query: str) -> List[RetrievalResult]:
        cda_retriever = await self.retriever_service.get_retriever(DatabaseEnum.CDA_VECTORDB)
        print("CDA RETRIEVER INVOKED")
        cda_metadata = cda_retriever.retrieve(query)

        return cda_metadata

    async def _retrieve_user_metadata(self, query: str, user_id: int) -> List[RetrievalResult]:
        user_retriever = await self.retriever_service.get_retriever(DatabaseEnum.USER_VECTORDB)
        print("USER RETRIEVER INVOKED")
        user_metadata = user_retriever.retrieve(query, user_id)

        return user_metadata
