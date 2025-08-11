
"""
Minimal CDA (Canadian Drug Agency) Vector Database Retriever.
Implements a simple interface for extracting relevant information from the CDA vector database.
"""

import numpy as np
import faiss
from typing import List
import logging
from .vectordb_retriever import BaseRetriever, RetrievalResult

# Import LangChain components, fall back to direct implementations
try:
    from langchain_community.vectorstores.faiss import FAISS
    from langchain_openai import OpenAIEmbeddings
    LANGCHAIN_AVAILABLE = True
except ImportError:
    FAISS = None
    OpenAIEmbeddings = None
    LANGCHAIN_AVAILABLE = False

try:
    from data.Preprocessing.Data.azure_blob_store import load_embeddings
    from data.Preprocessing.config import EMBEDDING_MODEL
except ImportError as e:
    logging.error(f"Failed to import required modules: {e}")
    load_embeddings = None
    EMBEDDING_MODEL = "text-embedding-3-small"

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None


class CDARetriever(BaseRetriever):
    """
    Retriever for CDA (Canadian Drug Agency) vector database.
    Uses LangChain if available, falls back to direct FAISS implementation.
    Easily extensible for hybrid, rerank, or other strategies in the future.
    """
    def __init__(self):
        self.embedding_model = EMBEDDING_MODEL
        self._vectorstore = None
        self._index = None
        self._metadata = None
        self._index_loaded = False

    def _ensure_index_loaded(self):
        if self._index_loaded:
            return
        try:
            if load_embeddings is None:
                if LANGCHAIN_AVAILABLE:
                    self._vectorstore = None
                else:
                    self._index = faiss.IndexFlatL2(1536)  # Default dimension
                self._metadata = []
            else:
                faiss_index, metadata = load_embeddings()
                if LANGCHAIN_AVAILABLE and FAISS is not None:
                    # Use LangChain FAISS wrapper
                    embeddings = OpenAIEmbeddings(model=self.embedding_model)
                    self._vectorstore = FAISS(
                        embedding_function=embeddings, 
                        index=faiss_index, 
                        docstore=None, 
                        index_to_docstore_id=None
                    )
                else:
                    # Use direct FAISS
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

    def _get_embedding(self, text: str) -> np.ndarray:
        """Get embedding for text using OpenAI's embedding model (fallback method)."""
        if OpenAI is None:
            return np.random.rand(1536).astype(np.float32)
        
        try:
            client = OpenAI()
            response = client.embeddings.create(
                model=self.embedding_model,
                input=text.strip()
            )
            embedding = np.array(response.data[0].embedding, dtype=np.float32)
            return embedding
        except Exception as e:
            return np.random.rand(1536).astype(np.float32)

    def retrieve(self, query: str, top_k: int = 10) -> List[RetrievalResult]:
        """
        Retrieve relevant information from the CDA vector database given a user query.
        Uses LangChain FAISS if available, falls back to direct FAISS implementation.
        """
        self._ensure_index_loaded()
        if not query.strip():
            return []

        try:
            if LANGCHAIN_AVAILABLE and self._vectorstore is not None:
                docs_and_scores = self._vectorstore.similarity_search_with_score(query, k=top_k)
                results = []
                for i, (doc, score) in enumerate(docs_and_scores):
                    # Handle both Document objects and fallback to metadata
                    if hasattr(doc, 'metadata') and hasattr(doc, 'page_content'):
                        text = doc.page_content
                        metadata = doc.metadata
                    elif self._metadata and i < len(self._metadata):
                        text = self._metadata[i].get('text', '')
                        metadata = self._metadata[i]
                    else:
                        continue

                    result = RetrievalResult(
                        text=text,
                        metadata={k: metadata.get(k, '') for k in ['drug_name', 'therapeutic_area', 'source', 'page', 'section_title', 'id']},
                        score=float(score),
                        rank=i + 1,
                        database="CDA_VECTORDB"
                    )
                    results.append(result)
                return results
            
            elif self._index is not None and self._index.ntotal > 0:
                # Use direct FAISS implementation
                query_embedding = self._get_embedding(query)
                query_vector = query_embedding.reshape(1, -1)
                scores, indices = self._index.search(query_vector, min(top_k, self._index.ntotal))
                
                results = []
                for i, (score, idx) in enumerate(zip(scores[0], indices[0])):
                    if idx < 0 or idx >= len(self._metadata):
                        continue
                    metadata = self._metadata[idx]
                    similarity_score = float(1.0 / (1.0 + score))  # Convert L2 distance to similarity
                    result = RetrievalResult(
                        text=metadata.get('text', ''),
                        metadata={k: metadata.get(k, '') for k in ['drug_name', 'therapeutic_area', 'source', 'page', 'section_title', 'id']},
                        score=similarity_score,
                        rank=i + 1,
                        database="CDA_VECTORDB"
                    )
                    results.append(result)
                return results
            
            else:
                return []

        except Exception as e:
            return []