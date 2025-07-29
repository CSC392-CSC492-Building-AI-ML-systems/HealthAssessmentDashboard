from typing import List
import json, os
from openai import OpenAI, OpenAIError
from dotenv import load_dotenv
from app.models.enums import IntentEnum

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

_SYSTEM_PROMPT = (
    "You are an intent classification assistant for a pharma chatbot. "
    "Possible intents are: "
    "\"VECTORDB\", \"PRICE_REC_SERVICE\", \"TIMELINE_REC_SERVICE\". "
    "Return only a JSON array of one or more of those strings. "
    "If none apply, return []. Do not add any other text."
)

def intent_classifier(query: str) -> List[IntentEnum]:
    """Classify the intent of a user query."""
    if not query or not query.strip():
        return []

    msgs = [
        {"role": "system", "content": _SYSTEM_PROMPT},
        {"role": "user", "content": f"User query: {query}\nIntents:"},
    ]

    try:
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=msgs,
            temperature=0.0,
            max_tokens=30,
        )
    except OpenAIError as e:
        raise RuntimeError(f"OpenAI classify failed: {e}") from e

    # Get the response
    raw = (resp.choices[0].message.content or "").strip()

    # Parse the response
    try:
        intents = json.loads(raw)
        if not isinstance(intents, list):
            intents = [intents]
    except json.JSONDecodeError:
        intents = [raw]

    allowed = {e.value for e in IntentEnum}
    cleaned = sorted({intent for intent in intents if isinstance(intent, str) and intent in allowed})

    return [IntentEnum(intent) for intent in cleaned]
