from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from app.db.sqlite import get_db
from app.schemas.organization import OrganizationCreate, OrganizationRead, OrganizationUpdate
from app.services.auth_service import get_current_user
from app.services.organization_service import OrganizationService
from app.models.user import User

router = APIRouter()

# Helper function to get organization service
async def get_organization_service(db: AsyncSession = Depends(get_db)) -> OrganizationService:
    return OrganizationService(db)

@router.post("/", response_model=OrganizationRead)
async def create_organization(
    organization: OrganizationCreate,
    current_user: User = Depends(get_current_user),
    organization_service: OrganizationService = Depends(get_organization_service)
):
    """Create a new organization"""
    return await organization_service.create_organization(organization)

@router.get("/", response_model=List[OrganizationRead])
async def get_organizations(
    organization_service: OrganizationService = Depends(get_organization_service)
):
    """Get all organizations"""
    return await organization_service.get_organizations()

@router.get("/search", response_model=List[OrganizationRead])
async def search_organizations(
    q: Optional[str] = Query(None, description="Search query for organization name"),
    province: Optional[str] = Query(None, description="Filter by province"),
    limit: int = Query(20, ge=1, le=100),
    organization_service: OrganizationService = Depends(get_organization_service)
):
    """Search organizations by name and optionally filter by province"""
    return await organization_service.search_organizations(query=q, province=province, limit=limit)

@router.get("/{organization_id}", response_model=OrganizationRead)
async def get_organization(
    organization_id: int,
    organization_service: OrganizationService = Depends(get_organization_service)
):
    """Get a specific organization by ID"""
    return await organization_service.get_organization_by_id(organization_id)

@router.put("/{organization_id}", response_model=OrganizationRead)
async def update_organization(
    organization_id: int,
    organization_update: OrganizationUpdate,
    current_user: User = Depends(get_current_user),
    organization_service: OrganizationService = Depends(get_organization_service)
):
    """Update an organization"""
    return await organization_service.update_organization(organization_id, organization_update)

@router.delete("/{organization_id}")
async def delete_organization(
    organization_id: int,
    current_user: User = Depends(get_current_user),
    organization_service: OrganizationService = Depends(get_organization_service)
):
    """Delete an organization"""
    await organization_service.delete_organization(organization_id)
    return {"message": "Organization deleted successfully"}
