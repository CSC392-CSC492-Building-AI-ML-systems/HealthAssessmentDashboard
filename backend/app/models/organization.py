from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base, TimestampMixin, PKMixin

class Organization(Base, PKMixin, TimestampMixin):
    __tablename__ = "organizations"

    name: Mapped[str] = mapped_column(unique=True, index=True)
    description: Mapped[str | None]
    location: Mapped[str | None]

    users = relationship("User", back_populates="organization")