from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException

from app.models.organization import Organization
from app.schemas.organization import OrganizationCreate, OrganizationUpdate


class OrganizationService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_organization(self, organization_data: OrganizationCreate) -> Organization:
        """Create a new organization"""
        try:
            # Check if organization with same name and province already exists
            existing_org = await self._get_by_name_and_province(
                organization_data.name, 
                organization_data.province
            )
            
            if existing_org:
                raise HTTPException(
                    status_code=400,
                    detail="Organization with this name already exists in this province"
                )
            
            db_organization = Organization(**organization_data.model_dump())
            self.db.add(db_organization)
            await self.db.commit()
            await self.db.refresh(db_organization)
            return db_organization
        except HTTPException:
            raise
        except IntegrityError as e:
            await self.db.rollback()
            if "uq_organization_name_province" in str(e.orig):
                raise HTTPException(
                    status_code=400,
                    detail="Organization with this name already exists in this province"
                )
            raise HTTPException(status_code=500, detail="Database integrity error")
        except Exception as e:
            await self.db.rollback()
            raise HTTPException(status_code=500, detail="Failed to create organization")

    async def get_organizations(self) -> List[Organization]:
        """Get all organizations"""
        try:
            result = await self.db.execute(
                select(Organization)
                .order_by(Organization.name)
            )
            return result.scalars().all()
        except Exception as e:
            raise HTTPException(status_code=500, detail="Failed to fetch organizations")

    async def search_organizations(
        self, 
        query: Optional[str] = None, 
        province: Optional[str] = None, 
        limit: int = 20
    ) -> List[Organization]:
        """Search organizations by name and optionally filter by province"""
        try:
            db_query = select(Organization)
            
            conditions = []
            if query:
                conditions.append(Organization.name.ilike(f"%{query}%"))
            if province:
                conditions.append(Organization.province == province)
            
            if conditions:
                db_query = db_query.where(and_(*conditions))
            
            db_query = db_query.order_by(Organization.name).limit(limit)
            
            result = await self.db.execute(db_query)
            return result.scalars().all()
        except Exception as e:
            raise HTTPException(status_code=500, detail="Failed to search organizations")

    async def get_organization_by_id(self, organization_id: int) -> Organization:
        """Get a specific organization by ID"""
        try:
            result = await self.db.execute(
                select(Organization).where(Organization.id == organization_id)
            )
            organization = result.scalar_one_or_none()
            
            if not organization:
                raise HTTPException(status_code=404, detail="Organization not found")
            
            return organization
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail="Failed to fetch organization")

    async def update_organization(
        self, 
        organization_id: int, 
        organization_update: OrganizationUpdate
    ) -> Organization:
        """Update an organization"""
        try:
            result = await self.db.execute(
                select(Organization).where(Organization.id == organization_id)
            )
            db_organization = result.scalar_one_or_none()
            
            if not db_organization:
                raise HTTPException(status_code=404, detail="Organization not found")
            
            # Update only provided fields
            update_data = organization_update.model_dump(exclude_unset=True)
            for field, value in update_data.items():
                setattr(db_organization, field, value)
            
            await self.db.commit()
            await self.db.refresh(db_organization)
            return db_organization
        except HTTPException:
            raise
        except Exception as e:
            await self.db.rollback()
            raise HTTPException(status_code=500, detail="Failed to update organization")

    async def delete_organization(self, organization_id: int) -> bool:
        """Delete an organization"""
        try:
            result = await self.db.execute(
                select(Organization).where(Organization.id == organization_id)
            )
            db_organization = result.scalar_one_or_none()
            
            if not db_organization:
                raise HTTPException(status_code=404, detail="Organization not found")
            
            await self.db.delete(db_organization)
            await self.db.commit()
            return True
        except HTTPException:
            raise
        except Exception as e:
            await self.db.rollback()
            raise HTTPException(status_code=500, detail="Failed to delete organization")

    async def _get_by_name_and_province(self, name: str, province: str) -> Optional[Organization]:
        """Helper method to get organization by name and province"""
        result = await self.db.execute(
            select(Organization).where(
                and_(
                    Organization.name == name,
                    Organization.province == province
                )
            )
        )
        return result.scalar_one_or_none()
