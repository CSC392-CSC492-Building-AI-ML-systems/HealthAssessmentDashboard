# simple_icer_runner.py
import os
import json
from utils import download_pdfs, text_from_pdfs
from Data.icer_extractor import extract_icer
from config import PDF_DIR

def extract_from_pdfs(urls, drug_name, allow_llm=False):
    """Download PDFs, extract text, and run ICER extractor."""
    os.makedirs(PDF_DIR, exist_ok=True)

    # Control env for ICER
    os.environ["ICER_ALLOW_LLM"] = "1" if allow_llm else "0"
    os.environ.setdefault("OPENAI_MODEL_ICER", "gpt-4o-mini")
    os.environ.setdefault("ICER_MAX_CHUNKS", "4")

    # Download
    files = download_pdfs(urls, project_number="tmp")
    if not files:
        return {"drug": drug_name, "pdfs": [], "status": "download_failed"}

    # Text extraction
    blocks = text_from_pdfs(files)
    combined_text = "\n".join(b["text"] for b in blocks)

    # Run ICER extraction
    res = extract_icer(drug_name, combined_text)

    return {"drug": drug_name, "pdfs": files, **res}


if __name__ == "__main__":
    # Example test run
    test_urls = [
        "https://www.cda-amc.ca/sites/default/files/DRR/2025/SR0807-Opzelura_Recommendation.pdf"
    ]
    out = extract_from_pdfs(test_urls, drug_name="Ruxolitinib", allow_llm=True)
    print(json.dumps(out, indent=2, ensure_ascii=False))
