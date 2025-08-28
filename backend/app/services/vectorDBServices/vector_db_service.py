import faiss
import numpy as np
import json
import uuid
import pickle
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path
import asyncio
import aiofiles

from app.core.config import settings
from app.services.vectorDBServices.azure_blob_service import AzureBlobService 
from app.services.vectorDBServices.embedding_service import EmbeddingService

class VectorDBService:
    def __init__(self):
        self.blob_service = AzureBlobService()
        self.embedding_service = EmbeddingService()
        self.embedding_dim = 1536  # OpenAI ada-002 embedding dimension
        
    def _get_user_vector_path(self, user_id: int) -> str:
        """Generate unique vector DB path for each user"""
        return f"user-{user_id}-drug-vectors"
    
    def _get_user_metadata_path(self, user_id: int) -> str:
        """Generate unique metadata path for each user"""
        return f"user-{user_id}-drug-metadata"

    async def _load_user_vector_db(self, user_id: int) -> tuple[faiss.IndexFlatIP, Dict[str, Any]]:
        """Load user's FAISS index and metadata from Azure Blob Storage"""
        vector_path = self._get_user_vector_path(user_id)
        metadata_path = self._get_user_metadata_path(user_id)
        
        try:
            # Download existing vector DB
            vector_data = await self.blob_service.download_blob(f"{vector_path}.index")
            metadata_data = await self.blob_service.download_blob(f"{metadata_path}.json")
            
            # Load FAISS index from bytes
            temp_vector_file = f"/tmp/{vector_path}.index"
            async with aiofiles.open(temp_vector_file, 'wb') as f:
                await f.write(vector_data)
            
            index = faiss.read_index(temp_vector_file)
            
            # Load metadata
            metadata = json.loads(metadata_data.decode('utf-8'))
            
            # Clean up temp file
            Path(temp_vector_file).unlink(missing_ok=True)
            
            return index, metadata
            
        except Exception as e:
            print(f"No existing vector DB found for user {user_id}, creating new one: {e}")
            # Create new index and metadata
            index = faiss.IndexFlatIP(self.embedding_dim)
            metadata = {
                "user_id": user_id,
                "documents": {},  # document_id -> document_info
                "vector_to_doc": {},  # vector_index -> document_id
                "created_at": datetime.utcnow().isoformat(),
                "last_updated": datetime.utcnow().isoformat(),
                "total_vectors": 0
            }
            return index, metadata

    async def _save_user_vector_db(self, user_id: int, index: faiss.IndexFlatIP, metadata: Dict[str, Any]) -> bool:
        """Save user's FAISS index and metadata to Azure Blob Storage"""
        vector_path = self._get_user_vector_path(user_id)
        metadata_path = self._get_user_metadata_path(user_id)
        
        try:
            # Save FAISS index to temp file
            temp_vector_file = f"/tmp/{vector_path}.index"
            faiss.write_index(index, temp_vector_file)
            
            # Read index file as bytes
            async with aiofiles.open(temp_vector_file, 'rb') as f:
                vector_data = await f.read()
            
            # Upload vector index to blob storage
            await self.blob_service.upload_blob(
                f"{vector_path}.index", 
                vector_data, 
                "application/octet-stream"
            )
            
            # Update metadata timestamp
            metadata["last_updated"] = datetime.utcnow().isoformat()
            metadata["total_vectors"] = index.ntotal
            
            # Upload metadata to blob storage
            metadata_json = json.dumps(metadata, indent=2).encode('utf-8')
            await self.blob_service.upload_blob(
                f"{metadata_path}.json", 
                metadata_json, 
                "application/json"
            )
            
            # Clean up temp file
            Path(temp_vector_file).unlink(missing_ok=True)
            
            return True
            
        except Exception as e:
            print(f"Error saving vector DB for user {user_id}: {e}")
            return False

    async def create_user_index(self, user_id: int) -> bool:
        """Create a new FAISS index for a user if it doesn't exist"""
        try:
            # This will create a new index if one doesn't exist
            index, metadata = await self._load_user_vector_db(user_id)
            
            # Save the new index if it was just created
            if metadata["total_vectors"] == 0:
                await self._save_user_vector_db(user_id, index, metadata)
            
            return True
        except Exception as e:
            print(f"Error creating index for user {user_id}: {e}")
            return False

    async def add_document_chunks(self, user_id: int, chunks: List[Dict[str, Any]], embeddings: List[List[float]], 
                                drug_data: Dict[str, Any], file_data: Dict[str, Any]) -> List[str]:
        """Add document chunks with embeddings to user's FAISS index"""
        try:
            # Load user's vector DB
            index, metadata = await self._load_user_vector_db(user_id)
            
            embeddings_array = np.array(embeddings, dtype=np.float32)
            faiss.normalize_L2(embeddings_array)
            
            vector_ids = []
            current_vector_count = index.ntotal
            
            # Prepare document metadata
            for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
                doc_id = str(uuid.uuid4())
                vector_ids.append(doc_id)
                vector_index = current_vector_count + i
                
                # Store document metadata
                metadata["documents"][doc_id] = {
                    "vector_index": vector_index,
                    "content": chunk["text"],
                    "drug_id": drug_data["id"],
                    "drug_title": drug_data["title"],
                    "file_id": file_data["id"],
                    "filename": file_data["original_filename"],
                    "chunk_index": i,
                    "page_number": chunk.get("page_number", 0),
                    "user_id": user_id,
                    "created_at": datetime.utcnow().isoformat(),
                    "therapeutic_area": drug_data.get("therapeutic_area", ""),
                    "drug_type": drug_data.get("drug_type", ""),
                    "submission_pathway": drug_data.get("submission_pathway", ""),
                    "word_count": chunk.get("word_count", 0),
                    "char_count": chunk.get("char_count", 0)
                }
                
                # Map vector index to document ID
                metadata["vector_to_doc"][str(vector_index)] = doc_id
            
            # Add vectors to FAISS index
            index.add(embeddings_array)
            
            # Save updated index and metadata
            await self._save_user_vector_db(user_id, index, metadata)
            
            return vector_ids
            
        except Exception as e:
            print(f"Error adding documents to FAISS index: {e}")
            raise

    async def search_user_documents(self, user_id: int, query: str, drug_id: Optional[int] = None, 
                                  top_k: int = 10) -> List[Dict[str, Any]]:
        """Search user's documents using FAISS vector similarity"""
        try:
            # Load user's vector DB
            index, metadata = await self._load_user_vector_db(user_id)
            
            if index.ntotal == 0:
                return []
            
            # Embedding for the query
            query_embedding = await self.embedding_service.generate_embedding(query)
            
            query_vector = np.array([query_embedding], dtype=np.float32)
            faiss.normalize_L2(query_vector)
            
            search_k = min(index.ntotal, top_k * 3)  
            scores, vector_indices = index.search(query_vector, search_k)
            
            # Process results and apply filters
            search_results = []
            for score, vector_idx in zip(scores[0], vector_indices[0]):
                if vector_idx == -1:  # FAISS returns -1 for empty slots
                    continue
                    
                doc_id = metadata["vector_to_doc"].get(str(vector_idx))
                if not doc_id:
                    continue
                    
                doc_info = metadata["documents"].get(doc_id)
                if not doc_info:
                    continue
                
                # Apply drug_id filter if specified
                if drug_id and doc_info["drug_id"] != drug_id:
                    continue
                
                search_results.append({
                    "content": doc_info["content"],
                    "drug_id": doc_info["drug_id"],
                    "drug_title": doc_info["drug_title"],
                    "filename": doc_info["filename"],
                    "score": float(score),  # Cosine similarity score
                    "chunk_index": doc_info["chunk_index"],
                    "page_number": doc_info.get("page_number", 0),
                    "therapeutic_area": doc_info.get("therapeutic_area", ""),
                    "drug_type": doc_info.get("drug_type", ""),
                    "created_at": doc_info.get("created_at", "")
                })
                
                if len(search_results) >= top_k:
                    break
            
            return search_results
            
        except Exception as e:
            print(f"Error searching documents: {e}")
            return []

    async def delete_drug_documents(self, user_id: int, drug_id: int) -> bool:
        """Delete all documents related to a specific drug"""
        try:
            # Load user's vector DB
            index, metadata = await self._load_user_vector_db(user_id)
            
            # Find documents to delete
            docs_to_delete = []
            for doc_id, doc_info in metadata["documents"].items():
                if doc_info["drug_id"] == drug_id:
                    docs_to_delete.append(doc_id)
            
            if not docs_to_delete:
                return True
            
            # Remove documents from metadata
            vector_indices_to_remove = []
            for doc_id in docs_to_delete:
                doc_info = metadata["documents"][doc_id]
                vector_idx = doc_info["vector_index"]
                vector_indices_to_remove.append(vector_idx)
                
                # Remove from metadata
                del metadata["documents"][doc_id]
                del metadata["vector_to_doc"][str(vector_idx)]
            
            # Rebuild FAISS index without deleted vectors
            await self._rebuild_index_without_vectors(user_id, index, metadata, vector_indices_to_remove)
            
            return True
            
        except Exception as e:
            print(f"Error deleting drug documents: {e}")
            return False

    async def delete_file_documents(self, user_id: int, file_id: int) -> bool:
        """Delete all documents related to a specific file"""
        try:
            # Load user's vector DB
            index, metadata = await self._load_user_vector_db(user_id)
            
            # Find documents to delete
            docs_to_delete = []
            for doc_id, doc_info in metadata["documents"].items():
                if doc_info["file_id"] == file_id:
                    docs_to_delete.append(doc_id)
            
            if not docs_to_delete:
                return True
            
            # Remove documents from metadata
            vector_indices_to_remove = []
            for doc_id in docs_to_delete:
                doc_info = metadata["documents"][doc_id]
                vector_idx = doc_info["vector_index"]
                vector_indices_to_remove.append(vector_idx)
                
                # Remove from metadata
                del metadata["documents"][doc_id]
                del metadata["vector_to_doc"][str(vector_idx)]
            
            # Rebuild FAISS index without deleted vectors
            await self._rebuild_index_without_vectors(user_id, index, metadata, vector_indices_to_remove)
            
            return True
            
        except Exception as e:
            print(f"Error deleting file documents: {e}")
            return False

    async def _rebuild_index_without_vectors(self, user_id: int, old_index: faiss.IndexFlatIP, 
                                           metadata: Dict[str, Any], vector_indices_to_remove: List[int]):
        """Rebuild FAISS index excluding specified vector indices"""
        try:
            # Get all vectors from old index
            all_vectors = old_index.reconstruct_n(0, old_index.ntotal)
            
            # Create mask for vectors to keep
            keep_mask = np.ones(old_index.ntotal, dtype=bool)
            for idx in vector_indices_to_remove:
                if idx < len(keep_mask):
                    keep_mask[idx] = False
            
            # Keep only non-deleted vectors
            kept_vectors = all_vectors[keep_mask]
            
            # Create new index
            new_index = faiss.IndexFlatIP(self.embedding_dim)
            if len(kept_vectors) > 0:
                new_index.add(kept_vectors)
            
            # Update vector indices in metadata
            new_metadata = metadata.copy()
            new_metadata["vector_to_doc"] = {}
            
            new_vector_idx = 0
            for old_vector_idx in range(old_index.ntotal):
                if keep_mask[old_vector_idx]:
                    # Find document ID for this vector
                    doc_id = metadata["vector_to_doc"].get(str(old_vector_idx))
                    if doc_id and doc_id in new_metadata["documents"]:
                        # Update vector index in document metadata
                        new_metadata["documents"][doc_id]["vector_index"] = new_vector_idx
                        new_metadata["vector_to_doc"][str(new_vector_idx)] = doc_id
                        new_vector_idx += 1
            
            # Save rebuilt index
            await self._save_user_vector_db(user_id, new_index, new_metadata)
            
        except Exception as e:
            print(f"Error rebuilding index: {e}")
            raise