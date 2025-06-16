import os
import json
import re
import tiktoken
import numpy as np
from openai import OpenAI
from dotenv import load_dotenv
from config import EMBEDDING_MODEL, EMBEDDING_DIR

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
enc = tiktoken.encoding_for_model(EMBEDDING_MODEL)

def count_tokens(text):
    return len(enc.encode(text))

def chunk_text(blocks, max_tokens=800, overlap=100):
    chunks = []
    current_chunk = []
    current_header = "Untitled Section"

    for block in blocks:
        if re.match(r"^[A-Z][A-Z\s\d:]{3,}$", block) or re.match(r"^\d+\.\s+[A-Z]", block):
            if current_chunk:
                chunk_text = " ".join(current_chunk).strip()
                if count_tokens(chunk_text) > max_tokens:
                    words = chunk_text.split()
                    for i in range(0, len(words), max_tokens - overlap):
                        subchunk = " ".join(words[i:i + max_tokens])
                        chunks.append({"text": subchunk, "section_title": current_header})
                else:
                    chunks.append({"text": chunk_text, "section_title": current_header})
            current_header = block.strip()
            current_chunk = []
        else:
            current_chunk.append(block)

    if current_chunk:
        chunks.append({"text": " ".join(current_chunk).strip(), "section_title": current_header})
    
    print(f"Created {len(chunks)} semantic chunks with headers.", flush=True)
    return chunks

def embed_text(text: str) -> np.ndarray:
    if not isinstance(text, str):
        raise ValueError("Text must be a string.")
    
    if not text.strip():
        raise ValueError("Text is empty.")

    num_tokens = count_tokens(text)
    if num_tokens > 8191: 
        raise ValueError(f"Text exceeds token limit: {num_tokens} tokens.")

    response = client.embeddings.create(
        input=[text],
        model=EMBEDDING_MODEL
    )
    print(f"Embedding created for text: {text[:30]}...", flush=True)
    return np.array(response.data[0].embedding)

def embed_chunks(chunks: list[str]) -> list[dict]:    
    embedded = []
    for i, chunk in enumerate(chunks):
        try:
            embedding = embed_text(chunk['text'])
            embedded.append({
                "text": chunk,
                "embedding": embedding,
            })
        except Exception as e:
            print(f"Skipping chunk {i} due to error: {e}")
    return embedded

def retrieve_top_k(index, metadata, query_text, k=4) -> list[str]:
    query_vec = embed_text(query_text).astype("float32").reshape(1, -1)
    istances, indices = index.search(query_vec, k)
    top_texts = [metadata[i]["text"] for i in indices[0] if i < len(metadata)]
    return top_texts

def save_embeddings(project_id: str, chunk_embeddings: list[dict]):
    path = os.path.join(EMBEDDING_DIR, f"{project_id}.json")
    with open(path, "w") as f:
        json.dump(chunk_embeddings, f, indent=2)

def load_embeddings(project_id: str) -> list[dict]:
    path = os.path.join(EMBEDDING_DIR, f"{project_id}.json")
    with open(path) as f:
        return json.load(f)
