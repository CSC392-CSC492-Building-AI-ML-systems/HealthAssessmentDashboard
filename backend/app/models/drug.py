from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON, Float, Date
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.models.base import Base, TimestampMixin, PKMixin

class Drug(Base, PKMixin, TimestampMixin):
    __tablename__ = "drugs"

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # BRIEF fields
    title = Column(String(255), nullable=False)
    generic_name = Column(String(255))
    project_number = Column(String(100))
    therapeutic_area = Column(String(255))
    submission_date = Column(Date)
    
    # DETAILS fields
    dosage_form = Column(String(255))
    din = Column(String(50))  # Drug Identification Number
    
    # ML PARAMETERS fields
    therapeutic_value = Column(String(255))
    cost_effectiveness = Column(Float) # ICER/QALY info
    manufacturer_price = Column(Float)
    reimbursement_restrictions = Column(Text)
    drug_type = Column(String(100))  # Biologic, rare disease, oncology
    submission_pathway = Column(String(100))  # Standard, priority, conditional
    
    # Additional metadata
    notes = Column(Text)

    # Relationships
    user = relationship("User", back_populates="drugs")
    files = relationship("DrugFile", back_populates="drug", cascade="all, delete-orphan")

class DrugFile(Base):
    __tablename__ = "drug_files"

    id = Column(Integer, primary_key=True, index=True)
    drug_id = Column(Integer, ForeignKey("drugs.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    filename = Column(String(255), nullable=False)
    original_filename = Column(String(255), nullable=False)
    file_size = Column(Integer)
    content_type = Column(String(100))
    blob_url = Column(String(500))
    vector_ids = Column(JSON)  # Store vector database IDs for this file's chunks
    chunk_count = Column(Integer, default=0)  # Number of chunks created
    file_type = Column(String(50), default="pdf")
    processing_status = Column(String(50), default="pending")  # pending, processing, completed, failed
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    drug = relationship("Drug", back_populates="files")
    user = relationship("User")