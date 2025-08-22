from typing import List
import json, os
from openai import OpenAI, OpenAIError  # keep if used elsewhere
from dotenv import load_dotenv
from app.models.enums import IntentEnum

import cohere

load_dotenv()

co = None
_MODEL_ID = os.getenv("INTENT_CLASSIFIER_MODEL_ID")

def _get_client():    
    global co
    if co is None:
       co = cohere.Client(os.getenv("COHERE_API_KEY"))
    return co

def intent_classifier(query: str) -> List[IntentEnum]:
    print("INTENT CLASSIFIER")
    if not query or not query.strip():
        return []
    try:
        # Classify the query using the intent classifier model
        response = _get_client().classify(
             model=_MODEL_ID,
             inputs=[query.strip()]
        )
        print("CLASSIFICATION: ", response)
    except Exception as e:
        raise RuntimeError(f"Cohere classify failed: {e}") from e

    # If no classifications are returned, return an empty list
    if not response.classifications:
        return []

    # Get the top prediction from the response
    classification = response.classifications[0]
    threshold = 0.5

    labels = classification.labels
    allowed = {e.value for e in IntentEnum}

    filtered_labels = [
        IntentEnum(label)
        for label, val in labels.items()
        if val.confidence >= threshold and label in allowed
    ]

    return filtered_labels