from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.models.user import User
from app.db.sqlite import get_sqlite_db
from app.db.supabase import get_db
from app.schemas.user import UserRead, UserUpdate
from app.schemas.user_preferences import UserPreferencesCreate, UserPreferencesRead
from app.services.auth_service import get_current_user
from app.services.user_service import UserService

router = APIRouter()

# Helper function to get user service
async def get_user_service(db: AsyncSession = Depends(get_db)) -> UserService:
    return UserService(db)

# Get current user profile
@router.get("/aboutme", response_model=UserRead)
async def get_current_user_profile(
    current_user: User = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service)
):
    """Get the current user's profile with organization details"""
    return await user_service.get_user_profile(current_user.id)

# Update current user profile
@router.put("/aboutme", response_model=UserRead)
async def update_current_user(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service)
):
    """Update the current user's profile"""
    return await user_service.update_user_profile(current_user.id, user_update)

# Get current user's preferences
@router.get("/preferences", response_model=UserPreferencesRead)
async def get_user_preferences(
    current_user: User = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service)
):
    """Get the current user's preferences"""
    return await user_service.get_user_preferences(current_user.id)

# Create or update user preferences
@router.post("/preferences", response_model=UserPreferencesRead)
async def create_or_update_user_preferences(
    preferences: UserPreferencesCreate,
    current_user: User = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service)
):
    """Create or update the current user's preferences"""
    return await user_service.create_or_update_preferences(current_user.id, preferences)