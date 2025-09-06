# backend/app/schemas/organization.py
from __future__ import annotations

from typing import Optional, List, TYPE_CHECKING
from pydantic import BaseModel, ConfigDict, Field

if TYPE_CHECKING:
    from app.schemas.drug import DrugListItem


class OrganizationBase(BaseModel):
    name: str
    province: str
    description: Optional[str] = None
    location: Optional[str] = None


class OrganizationCreate(OrganizationBase):
    pass


class OrganizationUpdate(BaseModel):
    name: Optional[str] = None
    province: Optional[str] = None
    description: Optional[str] = None
    location: Optional[str] = None


class OrganizationRead(OrganizationBase):
    id: int
    drugs: List["DrugListItem"] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)
