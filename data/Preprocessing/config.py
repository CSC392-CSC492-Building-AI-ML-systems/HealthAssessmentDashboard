import os

# Directories
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PDF_DIR = os.path.join(BASE_DIR, "Data", "pdfs")
OUTPUT_DIR = os.path.join(BASE_DIR, "Data", "analyzedData")
INPUT_CSV = os.path.join(
    BASE_DIR, "Data", "scrapedData", "cdaDownloads", "cda_amc_cleaned.csv"
)
EMBEDDING_MODEL = "text-embedding-3-small"
EMBEDDING_DIR = os.path.join(BASE_DIR, "Data", "embeddings")
VECTOR_DIR = os.path.join(BASE_DIR, "Data", "vectorDB")


# PDF processing config
MODEL = "gpt-4o"

SUMMARY_PROMPT_TEMPLATE = """
You are an assistant extracting answers. Do not include any explanation or commentary.
Extract the following field from the text:
{field}

Text:
{text}

Answer:
"""

FINAL_PROMPT = """
You are an assistant combining extracted answers into a structured JSON. Do not include any explanation or commentary.
The drug you are analyzing is {drug_name}.

Merge and deduplicate them into a single structured output with the following fields and types:
- "Brand Name": string
- "Use Case / Indication": string (max 50 words, patient group + treatment intent)
- "Price Recommendation": object with keys:  
    - "min": float or null  
    - "max": float or null  
    Notes:
      - From the document, extract any specific price information or cost analysis for the recommended drug, {drug_name}.
      - Only include prices that are directly associated with {drug_name} — ignore any prices or cost comparisons related to other drugs.
      - Focus on values such as the expected cost per patient, cost per treatment cycle, or overall cost for {drug_name}. 
      - If only one price is listed, use it as both min and max. If a price range is listed, extract the minimum and maximum.
      - Return only numeric values (in dollars) if available.
      - If no price is mentioned, set both min and max to `null`.
      - DO NOT write strings like "A reduction in price" or "Not specified".
- "Key Conditions or Restrictions": string (max 50 words, eligibility, clinical conditions)

Here are the extracted fields:
{text}
"""

FIELD_QUERIES = {
    "Brand Name": "What is the brand name of {drug_name}?",
    "Use Case / Indication": "What is the use case or indication for {drug_name}?",
    "Price Recommendation": (
        "What is the expected drug cost per patient, per cycle, or overall, as mentioned in economic evaluations for {drug_name}, "
        "including wholesale or reimbursement prices, cost comparisons to alternatives, and incremental cost values? "
        "Include any specific dollar values, such as $X per 28-day cycle, and statements on whether the drug increases "
        "or decreases cost compared to other treatments."
    ),
    "Key Conditions or Restrictions": "What are the key conditions or restrictions for using {drug_name}?"
}