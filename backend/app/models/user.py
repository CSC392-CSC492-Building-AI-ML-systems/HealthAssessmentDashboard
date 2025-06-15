from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey
from app.models.base import Base, TimestampMixin, PKMixin

class User(Base, PKMixin, TimestampMixin):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(unique=True, index=True)
    first_name: Mapped[str]
    last_name: Mapped[str]
    password_hash: Mapped[str]

    organization_id: Mapped[int | None] = mapped_column(
        ForeignKey("organizations.id"), index=True
    )
    organization = relationship("Organization", back_populates="users")

    preferences = relationship(
        "UserPreferences", uselist=False, back_populates="user", cascade="all, delete"
    )

    chats = relationship("ChatHistory", back_populates="user", cascade="all, delete")
