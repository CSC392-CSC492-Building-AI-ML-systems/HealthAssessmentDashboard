import json
import os
import pickle
import uuid
import faiss
import numpy as np
from datetime import datetime
from typing import List
from openai import OpenAI
from dotenv import load_dotenv
load_dotenv()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

from app.rag_tools.info_retrievers.config import (
    UNIFIED_INDEX_PATH,
    UNIFIED_METADATA_PATH,
    EMBEDDING_MODEL_DIM,
)
from azure.storage.blob import BlobServiceClient

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Azure Blob Storage Setup
blob_service_client = BlobServiceClient.from_connection_string(os.getenv("AZURE_STORAGE_CONNECTION_STRING"))
container_client = blob_service_client.get_container_client(os.getenv("AZURE_CONTAINER_NAME"))

# Global FAISS index and metadata in memory - it won't fill memory unless we pick large batch sizes
# so stick to 100 or less
_global_faiss_index = None
_global_metadata = None

def download_blob(blob_name: str, download_path: str):
    print("Getting blob client")
    blob_client = container_client.get_blob_client(blob_name)
    print("Got blob client")
    with open(download_path, "wb") as f:
        print("DOWNLOADING")
        f.write(blob_client.download_blob().readall())


def blob_exists(blob_name: str) -> bool:
    return any(b.name == blob_name for b in container_client.list_blobs(name_starts_with=blob_name))


def load_embeddings():
    """
    Load FAISS index and metadata from Azure blob storage once.
    If already loaded in memory, return the global index and metadata.
    """
    global _global_faiss_index, _global_metadata

    if _global_faiss_index is not None and _global_metadata is not None:
        print(f"Using cached in-memory FAISS index with {_global_faiss_index.ntotal} vectors.", flush=True)
        return _global_faiss_index, _global_metadata

    print("Loading FAISS index and metadata from Azure", flush=True)

    UNIFIED_INDEX_PATH = os.path.join(BASE_DIR, "unified.index")
    UNIFIED_METADATA_PATH = os.path.join(BASE_DIR, "unified_meta.pkl")

    # download_blob("unified.index", UNIFIED_INDEX_PATH)
    # download_blob("unified_meta.pkl", UNIFIED_METADATA_PATH)

    # Download blobs if they exist
    print(blob_exists("unified.index"))
    print(blob_exists("unified_meta.pkl"))
    print(UNIFIED_INDEX_PATH)
    print(UNIFIED_METADATA_PATH)

    _global_faiss_index = faiss.read_index(UNIFIED_INDEX_PATH)
    with open(UNIFIED_METADATA_PATH, "rb") as f:
        _global_metadata = pickle.load(f)

    print(f"Loaded {_global_faiss_index.ntotal} vectors from FAISS index.", flush=True)
    return _global_faiss_index, _global_metadata