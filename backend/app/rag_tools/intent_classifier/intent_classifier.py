from typing import List
import json, os
from openai import OpenAI, OpenAIError  # keep if used elsewhere
from dotenv import load_dotenv
from app.models.enums import IntentEnum

import cohere

load_dotenv()

co = cohere.Client(os.getenv("COHERE_API_KEY"))
_MODEL_ID = os.getenv("INTENT_CLASSIFIER_MODEL_ID")

def intent_classifier(query: str) -> List[IntentEnum]:
    if not query or not query.strip():
        return []
    try:
        # Classify the query using the intent classifier model
        response = co.classify(
            model=_MODEL_ID,
            inputs=[query.strip()]
        )
    except Exception as e:
        raise RuntimeError(f"Cohere classify failed: {e}") from e

    # If no classifications are returned, return an empty list
    if not response.classifications:
        return []

    # Get the top prediction from the response
    top = response.classifications[0].prediction
    allowed = {e.value for e in IntentEnum}
    return [IntentEnum(top)] if isinstance(top, str) and top in allowed else []