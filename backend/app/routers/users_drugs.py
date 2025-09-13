from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Body, Request
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
import json

from app.models.user import User
from app.db.sqlite import get_sqlite_db
from app.db.supabase import get_db
from app.schemas.drug import DrugCreate, DrugRead, DrugUpdate, DrugListItem
from app.services.auth_service import get_current_user
from app.services.drug_service import DrugService

router = APIRouter()

# Helper function to get drug service
async def get_drug_service(db: AsyncSession = Depends(get_db)) -> DrugService:
    return DrugService(db)

# Get user's drugs
@router.get("/", response_model=List[DrugListItem])
async def get_user_drugs(
    current_user: User = Depends(get_current_user),
    drug_service: DrugService = Depends(get_drug_service)
):
    """Get all drugs for the current user (simplified list)"""
    return await drug_service.get_user_drugs_list(current_user.id)

# Create a new drug
@router.post("/", response_model=DrugRead)
async def create_drug(
    drug_data: str = Form(...),
    files: Optional[List[UploadFile]] = File(None),
    current_user: User = Depends(get_current_user),
    drug_service: DrugService = Depends(get_drug_service),
):
    """Create a new drug with optional PDF uploads"""
    print("drug_data received:", drug_data)
    try:
        print(drug_data)
        drug_create = DrugCreate.parse_raw(drug_data)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid drug data: {str(e)}")

    # Validate file types (prioritize PDFs)
    if files:
        for file in files:
            if not file.filename.lower().endswith('.pdf'):
                raise HTTPException(
                    status_code=400,
                    detail=f"Only PDF files are currently supported. Received: {file.filename}"
                )
    print("CREATING DRUG")
    return await drug_service.create_drug(current_user.id, drug_create, files)

# Get specific drug with full details
@router.get("/{drug_id}", response_model=DrugRead)
async def get_drug(
    drug_id: int,
    current_user: User = Depends(get_current_user),
    drug_service: DrugService = Depends(get_drug_service)
):
    """Get a specific drug by ID with full details"""
    return await drug_service.get_drug(current_user.id, drug_id)

# Update drug
@router.put("/{drug_id}", response_model=DrugRead)
async def update_drug(
    drug_id: int,
    drug_data: str = Form(...),
    files: Optional[List[UploadFile]] = File(None),
    current_user: User = Depends(get_current_user),
    drug_service: DrugService = Depends(get_drug_service)
):
    """Update a drug with optional new PDF uploads"""
    try:
        drug_update = DrugUpdate.parse_raw(drug_data)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid drug data: {str(e)}")
    
    # Validate file types
    if files:
        for file in files:
            if not file.filename.lower().endswith('.pdf'):
                raise HTTPException(
                    status_code=400, 
                    detail=f"Only PDF files are currently supported. Received: {file.filename}"
                )
    
    return await drug_service.update_drug(current_user.id, drug_id, drug_update, files)

# Delete drug
@router.delete("/{drug_id}")
async def delete_drug(
    drug_id: int,
    current_user: User = Depends(get_current_user),
    drug_service: DrugService = Depends(get_drug_service)
):
    """Delete a drug and its associated files"""
    await drug_service.delete_drug(current_user.id, drug_id)
    return {"message": "Drug deleted successfully"}

# Get drug files
@router.get("/{drug_id}/files")
async def get_drug_files(
    drug_id: int,
    current_user: User = Depends(get_current_user),
    drug_service: DrugService = Depends(get_drug_service)
):
    """Get all PDF files associated with a drug"""
    return await drug_service.get_drug_files(current_user.id, drug_id)