"""
Vector Database Retriever interface for extracting information from a database.
"""

from typing import List, Dict, Any, Optional
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from app.models.enums import DatabaseEnum
from .cda_retriever import CDARetriever
import asyncio

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
    - Federated search across all available databases with global score-based ranking
    - Returns top-k most relevant results regardless of source database
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
    def query_single_database(cls, query_text: str, database: DatabaseEnum, top_k: int = 10) -> List[RetrievalResult]:
        """
        Query a specific database. Used internally by the main query() method.
        """
        retriever = cls.get_retriever(database)
        return retriever.retrieve(query_text, top_k=top_k)

    @classmethod
    def query(cls, query_text: str, database: DatabaseEnum = None, top_k: int = 10, score_threshold: float = 0.0) -> List[RetrievalResult]:
        """
        Main entry point for vector database querying for RAG pipeline.
        
        Implements federated search by default:
        - If database is specified: queries only that database
        - If database is None: queries all available databases and returns global top-k
        
        Args:
            query_text: The user's query
            database: Specific database to query (None for federated search across all)
            top_k: Number of top results to return
            score_threshold: Minimum similarity score to include (filters irrelevant chunks)
        
        Example usage: 
            VectorDBRetriever.query("give me the Canadian-registered use-case for regorafenib")  # Federated search
            VectorDBRetriever.query("regorafenib", DatabaseEnum.CDA_VECTORDB)  # Single database
        """
        if database is not None:
            return cls.query_single_database(query_text, database, top_k)
        
        all_results = []
        
        # Query all databases
        for database_enum in DatabaseEnum:
            try:
                db_results = cls.query_single_database(query_text, database_enum, top_k=max(top_k * 2, 20))
                
                # Filter by score
                filtered_results = [
                    result for result in db_results 
                    if result.score >= score_threshold
                ]
                
                all_results.extend(filtered_results)              
            except NotImplementedError:
                continue
            except Exception as e:
                continue
        
        # Sort all by similarity score descending
        all_results.sort(key=lambda x: x.score, reverse=True)
        
        # Top-k results
        return all_results[:top_k]

    @classmethod
    async def query_async(cls, query_text: str, database: DatabaseEnum = None, top_k: int = 10, score_threshold: float = 0.0) -> List[RetrievalResult]:
        """
        Async version of query() for better performance with federated search.
        
        Queries all databases in parallel rather than sequentially when database=None.
        """
        if database is not None:
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(
                None, 
                lambda: cls.query_single_database(query_text, database, top_k)
            )
        
        async def query_database(database_enum: DatabaseEnum):
            """Helper to query a single database asynchronously."""
            try:
                loop = asyncio.get_event_loop()
                results = await loop.run_in_executor(
                    None, 
                    lambda: cls.query_single_database(query_text, database_enum, max(top_k * 2, 20))
                )
                
                # Filter by score threshold
                return [
                    result for result in results 
                    if result.score >= score_threshold
                ]
                
            except NotImplementedError:
                return []
            except Exception as e:
                return []
        
        tasks = [query_database(db_enum) for db_enum in DatabaseEnum]
        results_lists = await asyncio.gather(*tasks)
        
        all_results = []
        for results_list in results_lists:
            all_results.extend(results_list)
        
        all_results.sort(key=lambda x: x.score, reverse=True)
        return all_results[:top_k]

    @classmethod
    def get_available_databases(cls) -> List[DatabaseEnum]:
        """Return list of databases that are currently implemented."""
        available = []
        for database_enum in DatabaseEnum:
            try:
                cls.get_retriever(database_enum)
                available.append(database_enum)
            except NotImplementedError:
                continue
        return available