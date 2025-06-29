import os
import re
from openai import OpenAI
from config import MODEL, FIELD_QUERIES, FINAL_PROMPT
from dotenv import load_dotenv
from embeddings_utils import chunk_text, embed_chunks, retrieve_top_k
from Data.azure_blob_store import save_embeddings, load_embeddings 

load_dotenv()
client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
)

def gpt_analyzer(long_text, generic_name, therapeutic_area):
    """Analyzes long text using GPT-4o, chunking it into semantic sections and embedding them for retrieval"""
    print("Chunking and embedding text")
    chunks = chunk_text(long_text)
    chunk_embeddings = embed_chunks(chunks)
    save_embeddings(chunk_embeddings, drug_name=generic_name, therapeutic_area=therapeutic_area)
    index, metadata = load_embeddings()

    
    # top 5 chunks
    formatted_field_queries = {field: query.format(drug_name=generic_name) for field, query in FIELD_QUERIES.items()}
    full_chunk_map = {}
    for field, query in formatted_field_queries.items():
        print(f"\n🔍 Retrieving top chunks for field: {field}")
        top_chunks = retrieve_top_k(index, metadata, query, k=5)
        print(f"Retrieved {len(top_chunks)} chunks for '{field}'")

        combined_text = ""
        for i, chunk in enumerate(top_chunks):
            combined_text += f"Chunk {i+1}:\n{chunk['text']}\n\n"

        full_chunk_map[field] = combined_text.strip()

    combined_fields_text = ""
    for field, text in full_chunk_map.items():
        combined_fields_text += f"\n### {field} Chunks:\n{text}\n"

    full_prompt = FINAL_PROMPT.format(text=combined_fields_text, drug_name=generic_name)

    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": full_prompt},
            ],
            temperature=0.2,
        )
        output = response.choices[0].message.content
        print(f"Final analysis output:\n{output}\n")
        return re.sub(r"^```(?:json)?|```$", "", output.strip(), flags=re.MULTILINE).strip()
    except Exception as e:
        print(f"Final summarization failed: {e}")
        return None
