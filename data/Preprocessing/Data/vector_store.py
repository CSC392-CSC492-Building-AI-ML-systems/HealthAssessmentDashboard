import os
import pickle
import uuid
import faiss
import numpy as np
from config import VECTOR_DIR

os.makedirs(VECTOR_DIR, exist_ok=True)

def get_project_dir(project_id: str):
    project_dir = os.path.join(VECTOR_DIR, project_id)
    os.makedirs(project_dir, exist_ok=True)
    return project_dir

def get_index_path(project_id: str):
    return os.path.join(get_project_dir(project_id), "index")

def get_metadata_path(project_id: str):
    return os.path.join(get_project_dir(project_id), "meta.pkl")

def save_embeddings(project_id: str, chunk_embeddings: list[dict]):
    print(f"Saving embeddings for project: {project_id}")
    
    dim = len(chunk_embeddings[0]['embedding'])
    index = faiss.IndexFlatL2(dim)

    vectors = []
    metadata = []

    for entry in chunk_embeddings:
        vector = np.array(entry["embedding"]).astype("float32")
        vectors.append(vector)
        metadata.append({
            "id": str(uuid.uuid4()),
            "text": entry["text"]
        })

    vectors_np = np.vstack(vectors)
    index.add(vectors_np)

    faiss.write_index(index, get_index_path(project_id))
    
    with open(get_metadata_path(project_id), "wb") as f:
        pickle.dump(metadata, f)
    
    print(f"Saved {len(vectors)} vectors.")

def load_embeddings(project_id: str):
    print(f"Loading embeddings for project: {project_id}")
    index_path = get_index_path(project_id)
    meta_path = get_metadata_path(project_id)

    if not os.path.exists(index_path) or not os.path.exists(meta_path):
        raise FileNotFoundError("Embedding index or metadata not found.")

    index = faiss.read_index(index_path)
    
    with open(meta_path, "rb") as f:
        metadata = pickle.load(f)

    return index, metadata
