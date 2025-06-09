import os
from openai import OpenAI
from config import MODEL, SUMMARY_PROMPT_TEMPLATE
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
)


def gpt_analyzer(long_text):
    MAX_PER_CHUNK = 10000
    chunks = [
        long_text[i : i + MAX_PER_CHUNK]
        for i in range(0, len(long_text), MAX_PER_CHUNK)
    ]

    partial_summaries = []

    for i, chunk in enumerate(chunks):
        print(f"🧠 Summarizing chunk {i+1}/{len(chunks)}...")
        prompt = SUMMARY_PROMPT_TEMPLATE.format(text=chunk)
        try:
            response = client.chat.completions.create(
                model=MODEL,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.2,
            )
            summary = response.choices[0].message.content
            partial_summaries.append(summary)
        except Exception as e:
            print(f"Chunk {i+1} failed: {e}")

    if not partial_summaries:
        return None

    # Final summary combining all partial summaries
    final_prompt = f"""
You are an assistant that combines partial summaries of a drug recommendation report into one structured summary and extracts structured data from the summaries.

Each summary below corresponds to a chunk of the same drug's documents. Merge and deduplicate them into a single structured output with the following fields and types:
- "Brand Name": string
- "Use Case / Indication": string (max 50 words, patient group + treatment intent)
- "Price Recommendation": object with keys:  
    - "min": float or null  
    - "max": float or null  
    Notes:
      - If only one price is found, set both min and max to that value.
      - If no price is mentioned, set both min and max to `null`.
      - DO NOT write strings like "A reduction in price" or "Not specified".
- "Submission Date": string (in YYYY-MM-DD format)
   If day is not available, use the first of the month.
- "Recommendation Date": string (in YYYY-MM-DD format)
   If day is not available, use the first of the month.
- "Key Conditions or Restrictions": string (max 50 words, eligibility, clinical conditions)

Partial Summaries:
{chr(10).join(partial_summaries)}

Only return the JSON object. Do not include any explanation or commentary.
"""

    try:
        print("📦 Combining chunk summaries into final summary...")
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": final_prompt},
            ],
            temperature=0.2,
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Final combination failed: {e}")
        return None
