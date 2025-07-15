from typing import List
from openai import OpenAI
from dotenv import load_dotenv
from data.Preprocessing.config import EMBEDDING_MODEL
load_dotenv()
client = OpenAI(api_key=__import__("os").getenv("OPENAI_API_KEY"))

# intent enums
CDA_VECTORDB = "CDA_VECTORDB"
USER_VECTORDB = "USER_VECTORDB"
PRICE_REC_SERVICE = "PRICE_REC_SERVICE"
TIMELINE_REC_SERVICE = "TIMELINE_REC_SERVICE"

def intent_classifier(query: str) -> List[str]:

    # Preprocess query

    # Build prompt

    # Call GPT-4o-mini

    # Postprocess response

    # Return intents





    return ["a", "b", "c"]






