from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, UploadFile
from typing import List, Optional
import uuid
from pathlib import Path

from app.models.drug import Drug, DrugFile
from app.schemas.drug import DrugCreate, DrugUpdate, DrugRead, DrugListItem
from app.services.vectorDBServices.file_processing_service import FileProcessingService
from app.services.vectorDBServices.azure_blob_service import AzureBlobService
from app.services.vectorDBServices.vector_db_service import VectorDBService

class DrugService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.file_processor = FileProcessingService()
        self.blob_service = AzureBlobService()
        self.vector_db = VectorDBService()

    async def get_user_drugs_list(self, user_id: int) -> List[DrugListItem]:
        """Get simplified list of drugs for a user"""
        result = await self.db.execute(
            select(Drug).where(Drug.user_id == user_id).order_by(Drug.created_at.desc())
        )
        drugs = result.scalars().all()
        return [DrugListItem.from_orm(drug) for drug in drugs]

    async def get_drug(self, user_id: int, drug_id: int) -> DrugRead:
        """Get a specific drug by ID with full details"""
        result = await self.db.execute(
            select(Drug).where(Drug.id == drug_id, Drug.user_id == user_id)
        )
        drug = result.scalar_one_or_none()
        
        if not drug:
            raise HTTPException(status_code=404, detail="Drug not found")
        
        return DrugRead.from_orm(drug)

    async def create_drug(self, user_id: int, drug_create: DrugCreate, files: Optional[List[UploadFile]] = None) -> DrugRead:
        """Create a new drug with optional PDF uploads"""
        # Ensure user has a FAISS vector index
        await self.vector_db.create_user_index(user_id)
        
        # Create the drug record
        drug_data = drug_create.dict()
        
        drug = Drug(
            user_id=user_id,
            **drug_data
        )
        
        self.db.add(drug)
        await self.db.flush()  # Get the ID without committing
        
        # Process PDF files if provided
        if files:
            await self._process_drug_files(user_id, drug, files)
        
        await self.db.commit()
        await self.db.refresh(drug)
        
        return DrugRead.from_orm(drug)

    async def update_drug(self, user_id: int, drug_id: int, drug_update: DrugUpdate, files: Optional[List[UploadFile]] = None) -> DrugRead:
        """Update a drug with optional new PDF uploads"""
        result = await self.db.execute(
            select(Drug).where(Drug.id == drug_id, Drug.user_id == user_id)
        )
        drug = result.scalar_one_or_none()
        
        if not drug:
            raise HTTPException(status_code=404, detail="Drug not found")
        
        # Update drug fields
        update_data = drug_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(drug, field, value)
        
        # Process new PDF files if provided
        if files:
            await self._process_drug_files(user_id, drug, files)
        
        await self.db.commit()
        await self.db.refresh(drug)
        
        return DrugRead.from_orm(drug)

    async def delete_drug(self, user_id: int, drug_id: int):
        """Delete a drug and its associated files from blob storage and FAISS vector DB"""
        result = await self.db.execute(
            select(Drug).where(Drug.id == drug_id, Drug.user_id == user_id)
        )
        drug = result.scalar_one_or_none()
        
        if not drug:
            raise HTTPException(status_code=404, detail="Drug not found")
        
        # Delete associated files from blob storage
        file_result = await self.db.execute(
            select(DrugFile).where(DrugFile.drug_id == drug_id)
        )
        files = file_result.scalars().all()
        
        for file in files:
            # Delete from blob storage
            if file.blob_url:
                await self.blob_service.delete_blob(file.filename)
            
            # Delete from FAISS vector database
            await self.vector_db.delete_file_documents(user_id, file.id)
        
        # Delete all drug documents from FAISS vector DB
        await self.vector_db.delete_drug_documents(user_id, drug_id)
        
        # Delete the drug (cascade will handle drug_files)
        await self.db.delete(drug)
        await self.db.commit()

    async def get_drug_files(self, user_id: int, drug_id: int):
        """Get all PDF files associated with a drug"""
        # Verify drug belongs to user
        result = await self.db.execute(
            select(Drug).where(Drug.id == drug_id, Drug.user_id == user_id)
        )
        drug = result.scalar_one_or_none()
        
        if not drug:
            raise HTTPException(status_code=404, detail="Drug not found")
        
        file_result = await self.db.execute(
            select(DrugFile).where(DrugFile.drug_id == drug_id)
        )
        files = file_result.scalars().all()
        
        return [
            {
                "id": f.id, 
                "filename": f.original_filename, 
                "url": f.blob_url,
                "file_type": f.file_type,
                "chunk_count": f.chunk_count,
                "processing_status": f.processing_status,
                "upload_date": f.created_at
            } for f in files
        ]

    async def search_drug_documents(self, user_id: int, query: str, drug_id: Optional[int] = None, top_k: int = 10):
        """Search through user's drug documents using FAISS vector similarity"""
        return await self.vector_db.search_user_documents(user_id, query, drug_id, top_k)

    async def _process_drug_files(self, user_id: int, drug: Drug, files: List[UploadFile]):
        """Process and upload PDF files for a drug to blob storage and FAISS vector DB"""
        for file in files:
            if file.size == 0:
                continue
                
            # Generate unique filename
            file_extension = Path(file.filename).suffix
            unique_filename = f"{user_id}_{drug.id}_{uuid.uuid4()}{file_extension}"
            
            # Create file record first
            drug_file = DrugFile(
                drug_id=drug.id,
                user_id=user_id,
                filename=unique_filename,
                original_filename=file.filename,
                file_size=file.size,
                content_type=file.content_type,
                file_type="pdf",
                processing_status="processing"
            )
            
            self.db.add(drug_file)
            await self.db.flush()  # Get the file ID
            
            try:
                # Read file content
                content = await file.read()
                
                # Upload to blob storage
                blob_url = await self.blob_service.upload_blob(
                    unique_filename, content, file.content_type
                )
                drug_file.blob_url = blob_url
                
                # Process PDF file (chunk and embed)
                chunks, embeddings = await self.file_processor.process_file(
                    content, file.filename, drug.id
                )
                
                # Prepare drug data for FAISS vector DB
                drug_data = {
                    "id": drug.id,
                    "title": drug.title,
                    "therapeutic_area": drug.therapeutic_area or "",
                    "drug_type": drug.drug_type or "",
                    "submission_pathway": drug.submission_pathway or ""
                }
                
                file_data = {
                    "id": drug_file.id,
                    "original_filename": drug_file.original_filename
                }
                
                # Add to FAISS vector database
                vector_ids = await self.vector_db.add_document_chunks(
                    user_id, chunks, embeddings, drug_data, file_data
                )
                
                # Update file record with vector DB info
                drug_file.vector_ids = vector_ids
                drug_file.chunk_count = len(chunks)
                drug_file.processing_status = "completed"
                
            except Exception as e:
                print(f"Error processing file {file.filename}: {e}")
                drug_file.processing_status = "failed"
                raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")