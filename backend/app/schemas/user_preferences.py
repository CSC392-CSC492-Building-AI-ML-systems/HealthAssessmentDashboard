from pydantic import BaseModel, ConfigDict
from typing import Optional, List

class UserPreferencesBase(BaseModel):
    news_preferences: Optional[str] = None
    therapeutic_areas: Optional[List[str]] = None

class UserPreferencesCreate(UserPreferencesBase):
    pass

class UserPreferencesRead(UserPreferencesBase):
    id: int
    user_id: int

    model_config = ConfigDict(from_attributes=True)
