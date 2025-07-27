import pytest
from unittest.mock import MagicMock

from app.models.enums import IntentEnum
from app.services.chatbot_service import ChatbotService


@pytest.mark.asyncio
async def test_call_tools_execution_order(monkeypatch):
    # Arrange: force the intent classifier to return a specific intent list.
    monkeypatch.setattr(
        "app.services.chatbot_service.intent_classifier",
        lambda q: [IntentEnum.USER_VECTORDB, IntentEnum.PRICE_REC_SERVICE],
    )

    service = ChatbotService(db=MagicMock())

    # Act
    responses = await service.call_tools("What is the recommended price for Drug X?")

    # Assert the order and presence of responses
    assert [r["intent"] for r in responses] == [
        IntentEnum.USER_VECTORDB,
        IntentEnum.PRICE_REC_SERVICE,
    ]

    # Additional sanity checks on structure
    assert isinstance(responses[0]["response"], list)  # metadata list from retriever
    assert "prediction" in responses[1]["response"]  # output from price rec service 