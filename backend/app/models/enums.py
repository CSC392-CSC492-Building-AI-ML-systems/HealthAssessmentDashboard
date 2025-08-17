from enum import Enum

class ChatRole(str, Enum):
    USER = "USER"
    ASSISTANT = "ASSISTANT"

class IntentEnum(str, Enum):
    """Intents recognised by the RAG pipeline.

    A single user query can map to multiple intents. The enum values are
    intentionally kept identical to the string representation expected by the
    downstream services.
    """
    VECTORDB = "VECTORDB"
    PRICE_REC_SERVICE = "PRICE_REC_SERVICE"
    TIMELINE_REC_SERVICE = "TIMELINE_REC_SERVICE"

class DatabaseEnum(str, Enum):
    """Database types for vector retrieval.
    
    Specifies which vector database to query for information retrieval.
    """
    CDA_VECTORDB = "CDA_VECTORDB"
    USER_VECTORDB = "USER_VECTORDB"