import re
import tiktoken
import numpy as np
from openai import OpenAI
from dotenv import load_dotenv
from config import EMBEDDING_MODEL

load_dotenv()
client = OpenAI(api_key=__import__("os").getenv("OPENAI_API_KEY"))
enc = tiktoken.encoding_for_model(EMBEDDING_MODEL)

# Model limits
MAX_EMBED_TOKENS = 8191
EMBED_OVERLAP    = 100

def count_tokens(text: str) -> int:
    return len(enc.encode(text))

def chunk_text(blocks, max_tokens=650, overlap=50):
    """
    Splits a list of {'source','page','text'} dicts into semantic chunks
    of <= max_tokens tokens, with an overlap of `overlap` tokens.
    """
    chunks = []
    current_tokens = []
    current_meta   = {}
    current_header = "Untitled Section"

    def flush_chunk():
        if not current_tokens:
            return
        text = enc.decode(current_tokens)
        chunks.append({
            **current_meta,
            "section_title": current_header,
            "text": text
        })

    for block in blocks:
        header = block["text"]
        is_header = bool(re.match(r"^[A-Z][A-Z\s\d:]{3,}$", header) or
                         re.match(r"^\d+\.\s+[A-Z]", header))
        if is_header:
            # flush previous chunk
            flush_chunk()
            # start new
            current_header = header
            current_tokens = []
            current_meta   = {"source": block["source"], "page": block["page"]}
            continue

        # tokenize this line
        line_tokens = enc.encode(block["text"] + " ")
        if not current_meta:
            current_meta = {"source": block["source"], "page": block["page"]}

        # if adding would exceed, flush with overlap
        if len(current_tokens) + len(line_tokens) > max_tokens:
            # keep last `overlap` tokens as the start of the next chunk
            overlap_tokens = current_tokens[-overlap:]
            flush_chunk()
            current_tokens = overlap_tokens

        current_tokens.extend(line_tokens)

    # final flush
    flush_chunk()
    print(f"Created {len(chunks)} chunks (≈{max_tokens} tokens each).", flush=True)
    return chunks

def embed_text(text: str) -> np.ndarray:
    """Embeds a single text string, ensuring it's under the token limit."""
    if not text.strip():
        raise ValueError("Text must be non-empty.")
    tok_count = count_tokens(text)
    if tok_count > MAX_EMBED_TOKENS:
        raise ValueError(f"Text exceeds token limit ({tok_count} > {MAX_EMBED_TOKENS}).")

    resp = client.embeddings.create(input=[text], model=EMBEDDING_MODEL)
    return np.array(resp.data[0].embedding, dtype="float32")

def embed_chunks(chunks):
    """
    Embeds each chunk safely. Since chunk_text guarantees 
    token ≤ max_tokens, we don’t need to re-split here.
    """
    embedded = []
    for idx, c in enumerate(chunks):
        try:
            vec = embed_text(c["text"])
            embedded.append({**c, "embedding": vec})
        except Exception as e:
            print(f"[embed_chunks] skip chunk {idx}: {e}", flush=True)
    return embedded

def retrieve_top_k(index, metadata, query_text, k=5):
    """
    Retrieves the top-k most similar chunks from FAISS.
    Returns a list of metadata dicts augmented with 'score'.
    """
    q_vec = embed_text(query_text).reshape(1, -1)
    distances, indices = index.search(q_vec, k)
    results = []
    for dist, idx in zip(distances[0], indices[0]):
        if 0 <= idx < len(metadata):
            m = metadata[idx].copy()
            m["score"] = float(dist)
            results.append(m)
    return results
