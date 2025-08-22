import importlib
import types
from typing import List

import pytest

from app.models.enums import IntentEnum


def _make_stub_client(top_prediction: str):
    """Create a stub Cohere client that returns a classify() result."""
    response = types.SimpleNamespace(
        classifications=[types.SimpleNamespace(prediction=top_prediction, labels={top_prediction: types.SimpleNamespace(confidence=1.0)} )]
    )

    class _StubClient:
        def classify(self, *args, **kwargs):
            return response

    return _StubClient()


@pytest.fixture()
def ic_module():
    """Return the intent_classifier module (imported fresh for each test)."""
    return importlib.import_module("app.rag_tools.intent_classifier.intent_classifier")


def test_empty_query_returns_empty_list(ic_module):
    assert ic_module.intent_classifier("") == []
    assert ic_module.intent_classifier("   ") == []


@pytest.mark.parametrize(
    "top_prediction,expected",
    [
        ("PRICE_REC_SERVICE", {IntentEnum.PRICE_REC_SERVICE}),
        ("TIMELINE_REC_SERVICE", {IntentEnum.TIMELINE_REC_SERVICE}),
        ("UNKNOWN", set()),  # should be ignored
    ],
)
def test_intent_classification(monkeypatch, ic_module, top_prediction, expected):
    # Patch the cohere client used inside the classifier so we don't hit the real API.
    stub_client = _make_stub_client(top_prediction)
    monkeypatch.setattr(ic_module, "co", stub_client)

    result: List[IntentEnum] = ic_module.intent_classifier("dummy query")

    assert set(result) == expected

    # Ensure the result list is sorted by value.
    assert result == sorted(result, key=lambda x: x.value)
