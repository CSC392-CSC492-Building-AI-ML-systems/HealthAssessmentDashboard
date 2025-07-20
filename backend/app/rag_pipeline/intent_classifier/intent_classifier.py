from typing import List

import json
import os
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

from app.models.enums import IntentEnum

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Training examples
_MODULE_DIR = Path(__file__).resolve().parent
_EXAMPLES_PATH = _MODULE_DIR / "intent_examples_400.jsonl"

_EXAMPLES: list[dict]
if _EXAMPLES_PATH.exists():
    with open(_EXAMPLES_PATH, "r", encoding="utf-8") as fh:
        _EXAMPLES = [json.loads(line) for line in fh if line.strip()]
else:
    _EXAMPLES = []

_SYSTEM_PROMPT = (
    "You are an intent classification assistant.  A user query may relate to "
    "one or more of the following intents: CDA_VECTORDB, USER_VECTORDB, "
    "PRICE_REC_SERVICE, TIMELINE_REC_SERVICE.  Only reply with a JSON array of "
    "one or more of those intent strings (e.g. [\"CDA_VECTORDB\"]).  Do not "
    "include any additional keys or commentary.  If none apply, reply with []."
)


def _build_few_shot_messages() -> List[dict]:
    """Convert the loaded examples into chat messages for few-shot prompting."""
    messages: List[dict] = []
    for ex in _EXAMPLES:
        messages.append({"role": "user", "content": ex["query"]}) # query
        messages.append({"role": "assistant", "content": json.dumps(ex["intents"])} ) # response
    return messages


_FEW_SHOT_MESSAGES = _build_few_shot_messages()

def intent_classifier(query: str) -> List[IntentEnum]:
    """Classify query into a list of IntentEnum values using GPT-4o-mini (Modify if needed)."""

    if not query:
        return []

    if not client.api_key:
        raise RuntimeError("OPENAI_API_KEY not set; cannot classify intents.")

    messages = [{"role": "system", "content": _SYSTEM_PROMPT}] + _FEW_SHOT_MESSAGES
    messages.append({"role": "user", "content": query})

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        max_tokens=16,
        temperature=0.0,
    )

    raw = response.choices[0].message.content.strip()
    labels = json.loads(raw)

    return [IntentEnum(label) for label in labels]






