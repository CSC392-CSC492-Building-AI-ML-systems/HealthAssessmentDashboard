from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr, ConfigDict
from app.schemas.organization import OrganizationCreate

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

class UserRead(UserBase):
    id: int
    created_at: datetime
    updated_at: datetime
    organization: Optional[OrganizationCreate] = None

    model_config = ConfigDict(from_attributes=True)
