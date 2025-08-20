from typing import Optional, List
from pydantic import BaseModel, ConfigDict

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
    
    model_config = ConfigDict(from_attributes=True)
