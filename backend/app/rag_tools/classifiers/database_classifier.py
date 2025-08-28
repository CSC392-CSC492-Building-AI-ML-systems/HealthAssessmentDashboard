from typing import List
import json, os
from openai import OpenAI, OpenAIError
from dotenv import load_dotenv
from app.models.enums import DatabaseEnum

load_dotenv()

load_dotenv()
client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
)


def database_classifier(query: str) -> DatabaseEnum:
    # ELECTED NOT TO USE THIS, BUT KEEPING IT HERE SINCE IT COULD BE MORE EFFICIENT IF IT CAN BE EXECUTED WITH
    # LITTLE TO NO RESOURCES
    if not query or not query.strip():
        return []

