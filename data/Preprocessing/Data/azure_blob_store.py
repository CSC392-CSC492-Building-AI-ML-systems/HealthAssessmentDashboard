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

from config import (
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

def init_index(dim: int, path: str):
    index = faiss.IndexFlatL2(dim)
    faiss.write_index(index, path)
    return index

def upload_blob(file_path: str, blob_name: str):
    with open(file_path, "rb") as data:
        container_client.upload_blob(blob_name, data, overwrite=True)

def download_blob(blob_name: str, download_path: str):
    blob_client = container_client.get_blob_client(blob_name)
    with open(download_path, "wb") as f:
        f.write(blob_client.download_blob().readall())

def blob_exists(blob_name: str) -> bool:
    return any(blob.name == blob_name for blob in container_client.list_blobs(name_starts_with=blob_name))


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

    # Download blobs if they exist
    if not blob_exists("unified.index") or not blob_exists("unified_meta.pkl"):
        print("No existing unified index found in Azure, initializing new empty FAISS index.", flush=True)
        _global_faiss_index = init_index(EMBEDDING_MODEL_DIM, UNIFIED_INDEX_PATH)
        _global_metadata = []
        return _global_faiss_index, _global_metadata

    download_blob("unified.index", UNIFIED_INDEX_PATH)
    download_blob("unified_meta.pkl", UNIFIED_METADATA_PATH)

    _global_faiss_index = faiss.read_index(UNIFIED_INDEX_PATH)
    with open(UNIFIED_METADATA_PATH, "rb") as f:
        _global_metadata = pickle.load(f)

    print(f"Loaded {_global_faiss_index.ntotal} vectors from FAISS index.", flush=True)
    return _global_faiss_index, _global_metadata


def save_embeddings(chunk_embeddings: List[dict], drug_name: str, therapeutic_area: str, batch_size: int = 10):
    """
    Append new chunk embeddings into the global in-memory index and metadata.
    Flush to Azure only manually or when batch_size is reached in other context.
    """
    global _global_faiss_index, _global_metadata

    if not chunk_embeddings:
        print("No embeddings to save.", flush=True)
        return

    if _global_faiss_index is None or _global_metadata is None:
        load_embeddings()

    dim = len(chunk_embeddings[0]["embedding"])
    if _global_faiss_index.d != dim:
        raise ValueError(f"Embedding dimension mismatch: expected {_global_faiss_index.d}, got {dim}")

    vectors = []
    for i, entry in enumerate(chunk_embeddings):
        vector = np.array(entry["embedding"]).astype("float32")
        vectors.append(vector)
        _global_metadata.append({
            "id": str(uuid.uuid4()),
            "text": entry["text"],
            "section_title": entry["text"].get("section_title", ""),
            "drug_name": drug_name,
            "therapeutic_area": therapeutic_area,
            "chunk_index": i
        })

    vectors_np = np.vstack(vectors)
    _global_faiss_index.add(vectors_np)
    print(f"Appended {len(chunk_embeddings)} chunks to in-memory FAISS index. Total now: {_global_faiss_index.ntotal}", flush=True)


def flush_embeddings_to_azure():
    """
    Flush the in-memory FAISS index and metadata to Azure blobs.
    """
    global _global_faiss_index, _global_metadata

    if _global_faiss_index is None or _global_metadata is None:
        print("No embeddings to flush.", flush=True)
        return

    # Save locally
    faiss.write_index(_global_faiss_index, UNIFIED_INDEX_PATH)
    with open(UNIFIED_METADATA_PATH, "wb") as f:
        pickle.dump(_global_metadata, f)

    # Upload to Azure
    upload_blob(UNIFIED_INDEX_PATH, "unified.index")
    upload_blob(UNIFIED_METADATA_PATH, "unified_meta.pkl")

    print(f"Flushed {_global_faiss_index.ntotal} vectors and metadata to Azure.", flush=True)

def upload_jsonl_to_blob(summaries, blob_name="summaries.jsonl"):
    """Uploads a list of summaries to an Azure Blob Storage container as a JSONL file"""

    blob_client = container_client.get_blob_client(blob_name)

    if blob_client.exists():
        with open("temp_existing.jsonl", "wb") as f:
            f.write(blob_client.download_blob().readall())
    else:
        open("temp_existing.jsonl", "w").close()

    with open("temp_existing.jsonl", "a", encoding="utf-8") as f:
        for summary in summaries:
            f.write(json.dumps(summary, ensure_ascii=False) + "\n")

    with open("temp_existing.jsonl", "rb") as data:
        blob_client.upload_blob(data, overwrite=True)

    print(f"Appended {len(summaries)} summaries to {blob_name}")


