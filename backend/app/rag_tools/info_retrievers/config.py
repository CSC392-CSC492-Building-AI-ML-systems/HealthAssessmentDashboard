import os

# Directories
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PDF_DIR = os.path.join(BASE_DIR, "Data", "pdfs")
OUTPUT_DIR = os.path.join(BASE_DIR, "Data", "analyzedData")
INPUT_CSV = os.path.join(
    BASE_DIR, "Data", "scrapedData", "cdaDownloads", "cda_amc_cleaned.csv"
)
EMBEDDING_MODEL = "text-embedding-3-small"
EMBEDDING_MODEL_DIM = 1536
UNIFIED_INDEX_PATH = os.path.join(BASE_DIR, "unified.index")
UNIFIED_METADATA_PATH = os.path.join(BASE_DIR, "unified_meta.pkl")
AZURE_OUTPUT_BLOB_NAME = "summaries_batch.jsonl"
AZURE_OUTPUT_LOCAL_TEMP = "summaries_batch.jsonl"

# PDF processing config
MODEL = "gpt-4o"