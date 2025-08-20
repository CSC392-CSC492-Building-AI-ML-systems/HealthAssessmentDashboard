from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Text, UniqueConstraint
from app.models.base import Base, TimestampMixin, PKMixin

class Organization(Base, PKMixin, TimestampMixin):
    __tablename__ = "organizations"

    name: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    province: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    location: Mapped[str | None] = mapped_column(String(255), nullable=True)

    __table_args__ = (
        UniqueConstraint('name', 'province', name='uq_organization_name_province'),
    )

    users = relationship("User", back_populates="organization")