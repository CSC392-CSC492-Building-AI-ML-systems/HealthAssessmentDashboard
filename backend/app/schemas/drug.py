from pydantic import BaseModel, field_validator
from typing import Optional, List, Dict, Any
from datetime import datetime, date
from enum import Enum
from app.schemas.organization import OrganizationRead

class DrugType(str, Enum):
    BIOLOGIC = "biologic"
    RARE_DISEASE = "rare_disease"
    ONCOLOGY = "oncology"
    STANDARD = "standard"

class SubmissionPathway(str, Enum):
    STANDARD = "standard"
    PRIORITY = "priority"
    CONDITIONAL = "conditional"

class DrugFileRead(BaseModel):
    id: int
    filename: str
    original_filename: str
    file_size: Optional[int] = None
    content_type: Optional[str] = None
    blob_url: Optional[str] = None
    file_type: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

class DrugBase(BaseModel):
    # BRIEF fields
    title: str
    generic_name: Optional[str] = None
    project_number: Optional[str] = None
    therapeutic_area: Optional[str] = None
    submission_date: Optional[date] = None
    
    # DETAILS fields
    dosage_form: Optional[str] = None
    din: Optional[str] = None
    
    # ML PARAMETERS fields
    therapeutic_value: Optional[str] = None
    cost_effectiveness: Optional[float] = None
    manufacturer_price: Optional[float] = None
    reimbursement_restrictions: Optional[str] = None
    drug_type: Optional[DrugType] = None
    submission_pathway: Optional[SubmissionPathway] = None
    
    # Additional fields
    notes: Optional[str] = None

class DrugCreate(DrugBase):
    @field_validator('cost_effectiveness', 'manufacturer_price')
    @classmethod
    def validate_positive_numbers(cls, v):
        if v is not None and v < 0:
            raise ValueError('Value must be positive')
        return v

class DrugUpdate(DrugBase):
    title: Optional[str] = None

class DrugRead(DrugBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    files: List[DrugFileRead] = []
    organizations: List[OrganizationRead] = []

    class Config:
        from_attributes = True

class DrugListItem(BaseModel):
    """Simplified drug model for listing"""
    id: int
    title: str
    generic_name: Optional[str] = None
    therapeutic_area: Optional[str] = None
    submission_date: Optional[date] = None
    drug_type: Optional[str] = None
    submission_pathway: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True