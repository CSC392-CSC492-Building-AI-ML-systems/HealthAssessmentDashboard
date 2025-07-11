from enum import StrEnum
from sqlalchemy import ForeignKey, String, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base, PKMixin, TimestampMixin
from app.models.enums import ChatRole

class ChatMessage(Base, PKMixin, TimestampMixin):
    __tablename__ = "chat_message"

    role: Mapped[ChatRole] = mapped_column(
        Enum(ChatRole, name="chat_role_enum", create_constraint=True, native_enum=False),
        nullable=False,
        doc="Role of the message sender: 'USER' or 'ASSISTANT'"
    )
    content: Mapped[str] = mapped_column(String(100), nullable=False)
    chat_history_id: Mapped[int] = mapped_column(ForeignKey("chat_history.id"), nullable=False)

    chat_history = relationship("ChatHistory", back_populates="messages")
