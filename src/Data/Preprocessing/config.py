import os

# Directories
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PDF_DIR = os.path.join(BASE_DIR, "Data", "pdfs")
OUTPUT_DIR = os.path.join(BASE_DIR, "Data", "analyzedData")
INPUT_CSV = os.path.join(
    BASE_DIR, "Data", "scrapedData", "cdaDownloads", "cda_amc_data.csv"
)

# Configuration for PDF Processing
MODEL = "gpt-4"
SUMMARY_PROMPT_TEMPLATE = """
You are an assistant that extracts structured data from drug recommendation documents.

Given the following text from a drug recommendation PDF, summarize it into a dictionary format with these fields:
- Drug Name
- Brand Name
- Generic Name
- Therapeutic Area
- Use Case / Indication
- Price Recommendation
- Timeline of Approval (Submission Date, Recommendation Date)
- Key Conditions or Restrictions

Here is the extracted text:
{text}
"""
