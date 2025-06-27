from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Table, Column, ForeignKey, String, Integer
from app.models.base import Base, PKMixin

class UserPreferences(Base, PKMixin):
    __tablename__ = "user_preferences"
    
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"), unique=True, nullable=False
    )
    user = relationship("User", uselist=False, back_populates="user_preferences")

    news_preferences: Mapped[str] = mapped_column(String)