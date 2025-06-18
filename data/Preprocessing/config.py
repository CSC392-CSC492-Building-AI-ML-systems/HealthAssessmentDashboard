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
UNIFIED_INDEX_PATH = os.path.join(VECTOR_DIR, "unified.index")
UNIFIED_METADATA_PATH = os.path.join(VECTOR_DIR, "unified_meta.pkl")


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
      - Extract specific price information or cost analysis for drug: {drug_name}.
      - Only include prices that are directly associated with {drug_name} — ignore any prices or cost comparisons related to other drugs.
      - Focus on values such as the expected cost per patient, cost per treatment cycle, or overall cost for {drug_name}. 
      - If only one price is listed, use it as both min and max. If a price range is listed, extract the minimum and maximum.
      - Return only numeric values (in dollars) if available.
      - If no price is mentioned, set both min and max to `null`.
- "Key Conditions or Restrictions": string (max 50 words, eligibility, clinical conditions)
- "Treatment Cycle Duration": integer (duration in days)
    Notes:
        - Extract the duration of one treatment cycle of {drug_name}, or the overall treatment course length and convert to number of days.
        - If duration is given in weeks or years, convert it to days (e.g. 1 year = 365 days, 1 week = 7 days).
        - If no explicit cycle duration is mentioned but annual cost is given (e.g. "$xyz annually"), assume treatment cycle duration is 365 days. If only monthly or weekly pricing is given, assume 30 or 7 days respectively. If no time-based cost or duration info is found, set to `null`.

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
        "What is the duration of one treatment cycle of {drug_name} (in days or weeks), or the overall treatment course length."
    ),
    "Key Conditions or Restrictions": "What are the key conditions or restrictions for using {drug_name}?",
    "Treatment Cycle Duration": (
        "What is the duration of one treatment cycle of {drug_name} (in days, weeks or years), or the overall treatment course length?"
        "If pricing is provided as annual cost, assume 365 days. If monthly, assume 30 days. If weekly, assume 7 days."
        "Return the duration as an integer number of days only."
    )
}