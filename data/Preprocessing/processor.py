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
    # 1) chunk + embed
    pages = chunk_text(long_text)  # each has source/page/text
    embeddings = embed_chunks(pages)

    # 2) save into FAISS+Azure
    save_embeddings(
        embeddings,
        drug_name=generic_name,
        therapeutic_area=therapeutic_area
    )

    # 3) reload index + metadata
    index, metadata = load_embeddings()

    # 4) for each HTA field, retrieve & assemble
    formatted = {
        field: q.format(drug_name=generic_name)
        for field, q in FIELD_QUERIES.items()
    }

    full_section_map = {}
    for field, q in formatted.items():
        top = retrieve_top_k(index, metadata, q, k=5)
        snippets = []
        for i, m in enumerate(top, 1):
            snippets.append(
                f"Chunk {i} (page {m['page']}, section {m['section_title']}):\n{m['text']}\n"
            )
        full_section_map[field] = "\n".join(snippets)

    # 5) build final prompt
    combined = "\n\n".join(
        f"### {fld}:\n{txt}" for fld, txt in full_section_map.items()
    )
    prompt = FINAL_PROMPT.format(text=combined, drug_name=generic_name)

    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.2,
        )
        output = response.choices[0].message.content
        print(f"Final analysis output:\n{output}\n")
        return re.sub(r"^```(?:json)?|```$", "", output.strip(), flags=re.MULTILINE).strip()
    except Exception as e:
        print(f"Final summarization failed: {e}")
        return None
