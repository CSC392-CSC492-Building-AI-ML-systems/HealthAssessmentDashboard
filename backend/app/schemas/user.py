from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr, ConfigDict
from app.schemas.organization import OrganizationRead

"""
Base: Base model
Create: Client provides
Read: Client receives
"""

class UserBase(BaseModel):
    email: EmailStr
    first_name: str
    last_name: str
    organization_id: Optional[int] = None

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    organization_id: Optional[int] = None

class UserRead(UserBase):
    id: int
    created_at: datetime
    updated_at: datetime
    organization: Optional[OrganizationRead] = None

    model_config = ConfigDict(from_attributes=True)
