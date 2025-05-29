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
You are an assistant that combines partial summaries of a drug recommendation report into one structured summary.

Each summary below corresponds to a chunk of the same drug's documents. Merge and deduplicate them into a single structured output with the following fields:
- Drug Name
- Brand Name
- Generic Name
- Therapeutic Area
- Use Case / Indication
- Price Recommendation
- Timeline of Approval (Submission Date, Recommendation Date)
- Key Conditions or Restrictions

Partial Summaries:
{chr(10).join(partial_summaries)}
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
