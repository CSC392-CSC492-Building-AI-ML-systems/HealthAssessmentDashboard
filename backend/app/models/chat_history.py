from sqlalchemy import ForeignKey, String, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base, PKMixin, TimestampMixin

class ChatHistory(Base, PKMixin, TimestampMixin):
    __tablename__ = "chat_history"

    chat_summary: Mapped[str] = mapped_column(String, nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)

    user = relationship("User", back_populates="chat_histories")
    messages = relationship("ChatMessage", back_populates="chat_history", cascade="all, delete-orphan")
