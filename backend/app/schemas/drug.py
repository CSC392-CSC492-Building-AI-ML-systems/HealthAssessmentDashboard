from datetime import date
from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict

class DrugBase(BaseModel):
    generic_name: str
    brand_name: str
    title: str
    indication: str
    conditions: List[str] = Field(default_factory=list)
    sub_date: date
    rec_date: Optional[date] = None
    price_rec: Optional[str] = None
    organization_id: Optional[int] = None

class DrugCreate(DrugBase):
    pass

class DrugRead(DrugBase):
    id: int

    model_config = ConfigDict(from_attributes=True)
