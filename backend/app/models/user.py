from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, String
from app.models.base import Base, TimestampMixin, PKMixin

class User(Base, PKMixin, TimestampMixin):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(unique=True, index=True, nullable=False)
    first_name: Mapped[str] = mapped_column(String)
    last_name: Mapped[str] = mapped_column(String)
    password_hash: Mapped[str] = mapped_column(String)

    organization_id: Mapped[int | None] = mapped_column(
        ForeignKey("organizations.id"), index=True
    )
    organization = relationship("Organization", back_populates="users")

    # FOR NOW, A USER HAS ONE UserPreferences OBJECT; COULD CHANGE LATER IF PREFERENCES ARE MORE INTRICATE THAN A STRING SUMMARY
    user_preferences = relationship(
        "UserPreferences", uselist=False, back_populates="user", cascade="all, delete"
    )
    chat_histories = relationship("ChatHistory", back_populates="user", cascade="all, delete-orphan")

    # BEFORE WE PROPERLY IMPLEMENT ORGANIZATIONS, USERS HOLD THEIR OWN drugs
    drugs = relationship("Drug", back_populates="user", cascade="all, delete-orphan")

