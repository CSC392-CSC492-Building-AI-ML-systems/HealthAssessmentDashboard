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
    BASE_DIR
)
from azure.storage.blob import BlobServiceClient

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Azure Blob Storage Setup
blob_service_client = BlobServiceClient.from_connection_string(os.getenv("AZURE_STORAGE_CONNECTION_STRING"))
container_client = blob_service_client.get_container_client(os.getenv("AZURE_CONTAINER_NAME"))

# Global FAISS index and metadata in memory - it won't fill memory unless we pick large batch sizes
# so stick to 100 or less
_global_cda_faiss_index = None
_global_cda_metadata = None

_global_user_faiss_index = None
_global_user_metadata = None


def download_blob(blob_name: str, download_path: str):
    print("Getting blob client")
    blob_client = container_client.get_blob_client(blob_name)
    print("Got blob client")
    with open(download_path, "wb") as f:
        print("DOWNLOADING")
        f.write(blob_client.download_blob().readall())


def blob_exists(blob_name: str) -> bool:
    return any(b.name == blob_name for b in container_client.list_blobs(name_starts_with=blob_name))


def load_embeddings(user_id: int = None):
    """
    Load FAISS index and metadata from local disk if available.
    If not found, download from Azure Blob Storage, then load.
    Returns the FAISS index and metadata.
    """
    global _global_cda_faiss_index, _global_cda_metadata
    global _global_user_faiss_index, _global_user_metadata

    # CHECK IF ALREADY CACHED IN THE GLOBAL VARS
    if user_id:
        if _global_user_faiss_index is not None and _global_user_metadata is not None:
            print(f"Using cached in-memory FAISS index with {_global_user_faiss_index.ntotal} vectors.", flush=True)
            return _global_user_faiss_index, _global_user_metadata
    else:
        if _global_cda_faiss_index is not None and _global_cda_metadata is not None:
            print(f"Using cached in-memory FAISS index with {_global_cda_faiss_index.ntotal} vectors.", flush=True)
            return _global_cda_faiss_index, _global_cda_metadata

    print("Loading FAISS index and metadata...", flush=True)

    # SELECT THE CORRECT VECTORDB
    if user_id:
        print("USING USER'S VECTORDB")
        index_filename = f"unified_{user_id}.index"
        metadata_filename = f"unified_meta_{user_id}.pkl"
        index_global_var = "_global_user_faiss_index"
        meta_global_var = "_global_user_metadata"
    else:
        print("USING CDA VECTORDB")
        index_filename = "unified.index"
        metadata_filename = "unified_meta.pkl"
        index_global_var = "_global_cda_faiss_index"
        meta_global_var = "_global_cda_metadata"

    index_path = os.path.join(BASE_DIR, index_filename)
    metadata_path = os.path.join(BASE_DIR, metadata_filename)

    # CHECK IF THE INDEX FILE EXISTS LOCALLY
    try:
        faiss_index = faiss.read_index(index_path, faiss.IO_FLAG_MMAP)
        with open(metadata_path, "rb") as f:
            metadata = pickle.load(f)
        print(f"Loaded {faiss_index.ntotal} vectors from local FAISS index.", flush=True)
    except Exception as e:
        print(f"Local files missing or corrupted ({e}), downloading from Azure...", flush=True)

        # IF IT DOESN'T EXIST, DOWNLOAD IT FROM THE Azure Blob
        if blob_exists(index_filename) and blob_exists(metadata_filename):
            download_blob(index_filename, index_path)
            download_blob(metadata_filename, metadata_path)
        else:
            raise FileNotFoundError(f"Neither local nor blob files exist for {index_filename}/{metadata_filename}")

        # LOAD AGAIN ONCE DOWNLOADED
        faiss_index = faiss.read_index(index_path)
        with open(metadata_path, "rb") as f:
            metadata = pickle.load(f)
        print(f"Loaded {faiss_index.ntotal} vectors from downloaded FAISS index.", flush=True)

    UNIFIED_INDEX_PATH = os.path.join(BASE_DIR, "unified.index")
    UNIFIED_METADATA_PATH = os.path.join(BASE_DIR, "unified_meta.pkl")

    # download_blob("unified.index", UNIFIED_INDEX_PATH)
    # download_blob("unified_meta.pkl", UNIFIED_METADATA_PATH)

    # Download blobs if they exist
    print(blob_exists("unified.index"))
    print(blob_exists("unified_meta.pkl"))
    print(UNIFIED_INDEX_PATH)
    print(UNIFIED_METADATA_PATH)
    # CACHE TO THE CORRECT GLOBALS VIA GLOBAL VARS
    globals()[index_global_var] = faiss_index
    globals()[meta_global_var] = metadata

    return faiss_index, metadata