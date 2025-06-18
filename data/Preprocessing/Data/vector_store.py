import os
import pickle
import uuid
import faiss
import numpy as np
from typing import List
from config import VECTOR_DIR, UNIFIED_INDEX_PATH, UNIFIED_METADATA_PATH

os.makedirs(VECTOR_DIR, exist_ok=True)

def get_project_dir(project_id: str):
    project_dir = os.path.join(VECTOR_DIR, project_id)
    os.makedirs(project_dir, exist_ok=True)
    return project_dir

def get_index_path(project_id: str):
    return os.path.join(get_project_dir(project_id), "index")

def get_metadata_path(project_id: str):
    return os.path.join(get_project_dir(project_id), "meta.pkl")

def save_embeddings(chunk_embeddings: List[dict], drug_name: str, therapeutic_area: str):
    """Saves unified embeddings across all drugs"""
    print(f"Saving unified embeddings")

    dim = len(chunk_embeddings[0]['embedding'])
    
    if os.path.exists(UNIFIED_INDEX_PATH):
        index = faiss.read_index(UNIFIED_INDEX_PATH)
        with open(UNIFIED_METADATA_PATH, "rb") as f:
            metadata = pickle.load(f)
    else:
        index = faiss.IndexFlatL2(dim)
        metadata = []

    vectors = []
    for i, entry in enumerate(chunk_embeddings):
        vector = np.array(entry["embedding"]).astype("float32")
        vectors.append(vector)
        metadata.append({
            "id": str(uuid.uuid4()),
            "text": entry["text"],
            "section_title": entry["text"]["section_title"],
            "drug_name": drug_name,
            "therapeutic_area": therapeutic_area,
            "chunk_index": i
        })

    vectors_np = np.vstack(vectors)
    index.add(vectors_np)

    faiss.write_index(index, UNIFIED_INDEX_PATH)
    with open(UNIFIED_METADATA_PATH, "wb") as f:
        pickle.dump(metadata, f)

    print(f"Unified index now has {index.ntotal} vectors.")

def load_embeddings():
    """Loads unified embeddings and metadata"""
    print(f"Loading embeddings for project")

    if not os.path.exists(UNIFIED_INDEX_PATH) or not os.path.exists(UNIFIED_METADATA_PATH):
        raise FileNotFoundError("Unified index or metadata not found.")
    
    index = faiss.read_index(UNIFIED_INDEX_PATH)
    with open(UNIFIED_METADATA_PATH, "rb") as f:
        metadata = pickle.load(f)
    return index, metadata