from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, String, JSON, Text
from app.models.base import Base, PKMixin, TimestampMixin

class UserPreferences(Base, PKMixin, TimestampMixin):
    __tablename__ = "user_preferences"
    
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"), unique=True, nullable=False
    )
    user = relationship("User", uselist=False, back_populates="user_preferences")

    # Store therapeutic areas as JSON array
    therapeutic_areas: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    
    # Custom preferences as text
    custom_preferences: Mapped[str | None] = mapped_column(Text, nullable=True)
    
    # Legacy field for backward compatibility
    news_preferences: Mapped[str | None] = mapped_column(String, nullable=True)