from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Text, UniqueConstraint
from app.models.base import Base, TimestampMixin, PKMixin
from app.models.drug import organization_drug_association
from typing import Optional

class Organization(Base, PKMixin, TimestampMixin):
    __tablename__ = "organizations"

    name: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    province: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    location: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    __table_args__ = (
        UniqueConstraint('name', 'province', name='uq_organization_name_province'),
    )

    # users = relationship("User", back_populates="organization")
    drugs = relationship("Drug", secondary=organization_drug_association, back_populates="organizations")