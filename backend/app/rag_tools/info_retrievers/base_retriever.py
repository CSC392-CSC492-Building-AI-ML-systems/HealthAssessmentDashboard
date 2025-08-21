from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Dict, Any, Optional

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