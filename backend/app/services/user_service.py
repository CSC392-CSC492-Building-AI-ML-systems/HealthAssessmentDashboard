from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from fastapi import HTTPException
from typing import Optional

from app.models.user import User
from app.models.user_preferences import UserPreferences
from app.models.organization import Organization
from app.schemas.user import UserUpdate
from app.schemas.user_preferences import UserPreferencesCreate


class UserService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_user_profile(self, user_id: int) -> User:
        """Get user profile with organization details"""
        try:
            result = await self.db.execute(
                select(User)
                .options(selectinload(User.organization))
                .where(User.id == user_id)
            )
            user = result.scalar_one_or_none()
            
            if not user:
                raise HTTPException(status_code=404, detail="User not found")
            
            return user
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail="Failed to fetch user profile")

    async def update_user_profile(self, user_id: int, user_update: UserUpdate) -> User:
        """Update user profile"""
        try:
            # Get current user from database
            result = await self.db.execute(
                select(User).where(User.id == user_id)
            )
            db_user = result.scalar_one_or_none()
            
            if not db_user:
                raise HTTPException(status_code=404, detail="User not found")
            
            # If organization_id is provided, verify it exists
            if user_update.organization_id is not None:
                org_result = await self.db.execute(
                    select(Organization).where(Organization.id == user_update.organization_id)
                )
                organization = org_result.scalar_one_or_none()
                if not organization:
                    raise HTTPException(status_code=400, detail="Organization not found")
            
            # Update only provided fields
            update_data = user_update.model_dump(exclude_unset=True)
            for field, value in update_data.items():
                setattr(db_user, field, value)
            
            await self.db.commit()
            await self.db.refresh(db_user)
            
            # Return user with organization details
            result = await self.db.execute(
                select(User)
                .options(selectinload(User.organization))
                .where(User.id == db_user.id)
            )
            updated_user = result.scalar_one()
            
            return updated_user
        except HTTPException:
            raise
        except Exception as e:
            await self.db.rollback()
            raise HTTPException(status_code=500, detail="Failed to update user profile")

    async def get_user_preferences(self, user_id: int) -> UserPreferences:
        """Get user preferences, creating default ones if none exist"""
        try:
            result = await self.db.execute(
                select(UserPreferences).where(UserPreferences.user_id == user_id)
            )
            preferences = result.scalar_one_or_none()
            
            if not preferences:
                # Create default preferences if none exist
                preferences = UserPreferences(user_id=user_id)
                self.db.add(preferences)
                await self.db.commit()
                await self.db.refresh(preferences)
            
            return preferences
        except Exception as e:
            raise HTTPException(status_code=500, detail="Failed to fetch user preferences")

    async def create_or_update_preferences(self, user_id: int, preferences: UserPreferencesCreate) -> UserPreferences:
        """Create or update user preferences"""
        try:
            # Check if preferences already exist
            result = await self.db.execute(
                select(UserPreferences).where(UserPreferences.user_id == user_id)
            )
            db_preferences = result.scalar_one_or_none()
            
            if db_preferences:
                # Update existing preferences
                update_data = preferences.model_dump(exclude_unset=True)
                for field, value in update_data.items():
                    setattr(db_preferences, field, value)
            else:
                # Create new preferences
                db_preferences = UserPreferences(
                    user_id=user_id,
                    **preferences.model_dump()
                )
                self.db.add(db_preferences)
            
            await self.db.commit()
            await self.db.refresh(db_preferences)
            return db_preferences
        except Exception as e:
            await self.db.rollback()
            raise HTTPException(status_code=500, detail="Failed to save user preferences")