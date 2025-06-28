from typing import Optional, List
from pydantic import BaseModel, ConfigDict

class OrganizationBase(BaseModel):
    name: str
    description: Optional[str] = None
    location: Optional[str] = None

class OrganizationCreate(OrganizationBase):
    pass             

class OrganizationRead(OrganizationBase):
    id: int
    
    model_config = ConfigDict(from_attributes=True)
