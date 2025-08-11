
"""
Vector Database Retriever interface for extracting information from a database.
"""

from typing import List, Dict, Any, Optional
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from app.models.enums import DatabaseEnum
from .cda_retriever import CDARetriever

@dataclass
class RetrievalResult:
    """Structured result from vector database retrieval."""
    text: str
    metadata: Dict[str, Any]
    score: float
    rank: int
    database: str

class BaseRetriever(ABC):
    """Abstract base class for vector database retrievers."""
    @abstractmethod
    def retrieve(self, query: str, top_k: int = 10) -> List[RetrievalResult]:
        """Retrieve relevant information from the database given a user query."""
        pass

class VectorDBRetriever:
    """
    Main interface for extracting information from a vector database given a user query.

    Retrieval strategy:
    - Uses semantic search (OpenAI embeddings + FAISS vector search)
    - Returns top-k most relevant results
    """
    _retrievers: Dict[DatabaseEnum, BaseRetriever] = {}

    @classmethod
    def get_retriever(cls, database: DatabaseEnum) -> BaseRetriever:
        if database not in cls._retrievers:
            if database == DatabaseEnum.CDA_VECTORDB:
                cls._retrievers[database] = CDARetriever()
            else:
                raise NotImplementedError(f"Retriever for {database} not implemented.")
        return cls._retrievers[database]

    @classmethod
    def query(cls, query_text: str, database: DatabaseEnum, top_k: int = 10) -> List[RetrievalResult]:
        """
        Main entry point for vector database querying for RAG pipeline.
        Example usage: VectorDBRetriever.query("give me the Canadian-registered use-case for regorafenib", CDA_VECTORDB)
        """
        retriever = cls.get_retriever(database)
        return retriever.retrieve(query_text, top_k=top_k)
