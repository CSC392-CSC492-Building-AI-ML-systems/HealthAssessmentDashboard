"""
Minimal Vector Database Retriever.
Implements a simple interface for extracting relevant information from a vector database of a given "source"
--------
IMPLEMENTED SOURCES:
- CDA VECTORDB: All PDFs scraped and uploaded to Azure Blob from the CDA-AMC database.
- User VECTORDB: All PDFs uploaded by the given User (via user_id) onto the dashboard for all drugs they manage.
"""
import os
import faiss
import numpy as np
from typing import List, Optional
from .base_retriever import BaseRetriever, RetrievalResult
from app.models.enums import DatabaseEnum

# Import LangChain components, fall back to direct implementations
try:
    from langchain_community.vectorstores.faiss import FAISS
    from langchain_openai import OpenAIEmbeddings

    LANGCHAIN_AVAILABLE = True
except ImportError:
    FAISS = None
    OpenAIEmbeddings = None
    LANGCHAIN_AVAILABLE = False

from app.rag_tools.info_retrievers.utils import load_embeddings
from app.rag_tools.info_retrievers.config import EMBEDDING_MODEL

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None


class VectorDBRetriever(BaseRetriever):
    """
    Generic retriever for both CDA and User vector databases.
    Uses LangChain if available, falls back to direct FAISS implementation.
    """

    def __init__(self, source: DatabaseEnum):
        """
        source: "CDA" or "USER"
        """
        self.embedding_model = EMBEDDING_MODEL
        self._vectorstore = None
        self._index = None
        self._metadata = None
        self._index_loaded = False
        self.source = source

    def _ensure_index_loaded(self, user_id: int = None):
        if self._index_loaded:
            return
        try:
            if self.source == DatabaseEnum.USER_VECTORDB and user_id is not None:
                faiss_index, metadata = load_embeddings(user_id)
            else:
                faiss_index, metadata = load_embeddings()

            if LANGCHAIN_AVAILABLE and FAISS is not None:
                embeddings = OpenAIEmbeddings(model=self.embedding_model)
                self._vectorstore = FAISS(
                    embedding_function=embeddings,
                    index=faiss_index,
                    docstore=None,
                    index_to_docstore_id=None
                )
            else:
                self._index = faiss_index

            self._metadata = metadata
            self._index_loaded = True

        except Exception as e:
            if LANGCHAIN_AVAILABLE:
                self._vectorstore = None
            else:
                self._index = faiss.IndexFlatL2(1536)
            self._metadata = []
            self._index_loaded = True

    def retrieve(self, query: str, user_id: int = None, top_k: int = 3) -> List[RetrievalResult]:
        self._ensure_index_loaded(user_id)

        if not query.strip():
            return []

        try:
            if LANGCHAIN_AVAILABLE and self._vectorstore is not None:
                docs_and_scores = self._vectorstore.similarity_search_with_score(query, k=top_k)
                return [
                    RetrievalResult(
                        text=doc.page_content,
                        metadata=doc.metadata if hasattr(doc, 'metadata') else {},
                        score=float(1.0 - score),
                        rank=rank + 1,
                        database=self.source
                    )
                    for rank, (doc, score) in enumerate(docs_and_scores)
                ]

            elif self._index is not None and self._index.ntotal > 0:
                query_embedding = self._get_embedding(query)
                if query_embedding is None:
                    return []

                query_embedding = query_embedding.reshape(1, -1).astype(np.float32)
                distances, indices = self._index.search(query_embedding, top_k)

                results = []
                for rank, (distance, idx) in enumerate(zip(distances[0], indices[0])):
                    if idx >= 0 and idx < len(self._metadata):
                        metadata = self._metadata[idx] if self._metadata else {}
                        text = metadata.get('text',
                                            metadata.get('content', metadata.get('page_content', str(metadata))))
                        results.append(
                            RetrievalResult(
                                text=text,
                                metadata=metadata,
                                score=float(1.0 - distance),
                                rank=rank + 1,
                                database=f"{self.source}_VECTORDB"
                            )
                        )

                return results

            else:
                return []

        except Exception:
            return []

    def _get_embedding(self, text: str) -> Optional[np.ndarray]:
        if OpenAI is None or not os.getenv("OPENAI_API_KEY"):
            return np.random.rand(1536).astype(np.float32)

        try:
            client = OpenAI()
            response = client.embeddings.create(
                model=self.embedding_model,
                input=text.strip()
            )
            return np.array(response.data[0].embedding, dtype=np.float32)
        except Exception:
            return np.random.rand(1536).astype(np.float32)
