import importlib
import types
from typing import List

import pytest

from app.models.enums import IntentEnum


def _make_stub_client(response_content: str):
    """Create a stub OpenAI client that returns the given content."""

    # Build a minimal response object that mirrors the structure we access in the real OpenAI response
    response = types.SimpleNamespace(
        choices=[
            types.SimpleNamespace(
                message=types.SimpleNamespace(content=response_content)
            )
        ]
    )

    class _StubCompletions:
        def create(self, *args, **kwargs):
            return response

    class _StubChat:
        def __init__(self):
            self.completions = _StubCompletions()

    class _StubClient:
        def __init__(self):
            self.chat = _StubChat()

    return _StubClient()


@pytest.fixture()
def ic_module():
    """Return the intent_classifier module (imported fresh for each test)."""
    return importlib.import_module("app.rag_pipeline.intent_classifier.intent_classifier")


def test_empty_query_returns_empty_list(ic_module):
    assert ic_module.intent_classifier("") == []
    assert ic_module.intent_classifier("   ") == []


@pytest.mark.parametrize(
    "mock_response,expected",
    [
        ("[\"PRICE_REC_SERVICE\"]", {IntentEnum.PRICE_REC_SERVICE}),
        (
            "[\"PRICE_REC_SERVICE\", \"TIMELINE_REC_SERVICE\"]",
            {IntentEnum.PRICE_REC_SERVICE, IntentEnum.TIMELINE_REC_SERVICE},
        ),
        (
            "[\"PRICE_REC_SERVICE\", \"UNKNOWN\"]",  # unknown should be ignored
            {IntentEnum.PRICE_REC_SERVICE},
        ),
    ],
)

def test_intent_classification(monkeypatch, ic_module, mock_response, expected):
    # Patch the OpenAI client used inside the classifier so we don't hit the real API.
    stub_client = _make_stub_client(mock_response)
    monkeypatch.setattr(ic_module, "client", stub_client)

    result: List[IntentEnum] = ic_module.intent_classifier("dummy query")

    assert set(result) == expected

    # Ensure the result list is sorted lexicographically by value, as implemented.
    assert result == sorted(result, key=lambda x: x.value) 