import pytest
from httpx import AsyncClient

from app.models.user import User


async def _create_user(session, email="chatuser@example.com") -> User:
    """Helper that creates and returns a persisted User instance."""
    user = User(
        email=email,
        first_name="Chat",
        last_name="User",
        password_hash="hashedpassword",
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user


@pytest.mark.asyncio
async def test_create_chat_200(client: AsyncClient, _session):
    user = await _create_user(_session, email="create_chat@example.com")
    resp = await client.post(
        "/chat/sessions",
        data={"user_id": str(user.id), "title": "My first chat"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data.get("chat_summary") == "My first chat"
    assert data.get("user_id") == user.id
    assert "id" in data
    assert "created_at" in data


@pytest.mark.asyncio
async def test_create_chat_400_missing_fields(client: AsyncClient):
    # Missing user_id
    resp = await client.post("/chat/sessions", data={"title": "Test"})
    assert resp.status_code == 422

    # Missing title
    resp = await client.post("/chat/sessions", data={"user_id": "1"})
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_create_chat_404_invalid_user(client: AsyncClient):
    resp = await client.post(
        "/chat/sessions",
        data={"user_id": "999999", "title": "Invalid user"},
    )
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_list_chats_200(client: AsyncClient, _session):
    user = await _create_user(_session, email="list_chat@example.com")
    other_user = await _create_user(_session, email="other_list@example.com")

    # Create chats for both users
    for title in ["Chat A", "Chat B"]:
        await client.post("/chat/sessions", data={"user_id": str(user.id), "title": title})
    await client.post("/chat/sessions", data={"user_id": str(other_user.id), "title": "Other's Chat"})

    resp = await client.get(f"/chat/sessions?user_id={user.id}")
    assert resp.status_code == 200

    sessions = resp.json()
    assert isinstance(sessions, list)
    assert len(sessions) == 2  # Should only see their own chats
    titles = {s["chat_summary"] for s in sessions}
    assert titles == {"Chat A", "Chat B"}


@pytest.mark.asyncio
async def test_list_chats_404_invalid_user(client: AsyncClient):
    resp = await client.get("/chat/sessions?user_id=999999")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_get_chat_200(client: AsyncClient, _session):
    user = await _create_user(_session, email="get_chat@example.com")
    create_resp = await client.post(
        "/chat/sessions", data={"user_id": str(user.id), "title": "Specific Chat"}
    )
    session_id = create_resp.json()["id"]

    resp = await client.get(f"/chat/sessions/{session_id}?user_id={user.id}")
    assert resp.status_code == 200
    data = resp.json()
    assert data["id"] == session_id
    assert data["chat_summary"] == "Specific Chat"
    assert data["user_id"] == user.id


@pytest.mark.asyncio
async def test_get_chat_404_not_found(client: AsyncClient, _session):
    user = await _create_user(_session, email="get_404@example.com")
    resp = await client.get(f"/chat/sessions/99999?user_id={user.id}")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_get_chat_403_unauthorized(client: AsyncClient, _session):
    # Create a chat session owned by user1
    user1 = await _create_user(_session, email="user1@example.com")
    user2 = await _create_user(_session, email="user2@example.com")
    
    create_resp = await client.post(
        "/chat/sessions", data={"user_id": str(user1.id), "title": "User1's Chat"}
    )
    session_id = create_resp.json()["id"]

    # Try to access it as user2
    resp = await client.get(f"/chat/sessions/{session_id}?user_id={user2.id}")
    assert resp.status_code == 404  # We return 404 for security (don't leak existence)


@pytest.mark.asyncio
async def test_rename_chat_200(client: AsyncClient, _session):
    user = await _create_user(_session, email="rename_chat@example.com")
    create_resp = await client.post(
        "/chat/sessions", data={"user_id": str(user.id), "title": "Old Title"}
    )
    session_id = create_resp.json()["id"]

    resp = await client.put(
        f"/chat/sessions/{session_id}",
        data={"user_id": str(user.id), "new_title": "New Title"},
    )
    assert resp.status_code == 200
    assert resp.json().get("detail") == "Session renamed"

    verify_resp = await client.get(f"/chat/sessions/{session_id}?user_id={user.id}")
    assert verify_resp.status_code == 200
    assert verify_resp.json()["chat_summary"] == "New Title"


@pytest.mark.asyncio
async def test_rename_chat_404_not_found(client: AsyncClient, _session):
    user = await _create_user(_session, email="rename_404@example.com")
    resp = await client.put(
        "/chat/sessions/99999",
        data={"user_id": str(user.id), "new_title": "New Title"},
    )
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_delete_chat_200(client: AsyncClient, _session):
    user = await _create_user(_session, email="delete_chat@example.com")
    create_resp = await client.post(
        "/chat/sessions", data={"user_id": str(user.id), "title": "To be deleted"}
    )
    session_id = create_resp.json()["id"]

    resp = await client.delete(f"/chat/sessions/{session_id}?user_id={user.id}")
    assert resp.status_code == 200
    assert resp.json().get("detail") == "Session deleted"

    not_found_resp = await client.get(f"/chat/sessions/{session_id}?user_id={user.id}")
    assert not_found_resp.status_code == 404


@pytest.mark.asyncio
async def test_delete_chat_404_not_found(client: AsyncClient, _session):
    user = await _create_user(_session, email="delete_404@example.com")
    resp = await client.delete(f"/chat/sessions/99999?user_id={user.id}")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_send_and_get_messages_200(client: AsyncClient, _session):
    user = await _create_user(_session, email="messages_chat@example.com")
    create_resp = await client.post(
        "/chat/sessions", data={"user_id": str(user.id), "title": "Messages Chat"}
    )
    session_id = create_resp.json()["id"]

    # Test sending messages
    messages = ["Hello", "How are you?"]
    for msg in messages:
        send_resp = await client.post(
            f"/chat/sessions/{session_id}/messages",
            data={"user_id": str(user.id), "message": msg},
        )
        assert send_resp.status_code == 200
        body = send_resp.json()
        assert body["user_message"] == msg
        assert body["bot_response"].startswith("Bot received")

    # Test retrieving messages
    resp = await client.get(f"/chat/sessions/{session_id}/messages?user_id={user.id}")
    assert resp.status_code == 200
    messages_payload = resp.json()
    assert "messages" in messages_payload
    
    # Should have 4 messages (2 user + 2 bot responses)
    msgs = messages_payload["messages"]
    assert len(msgs) == 4
    
    # Verify message order and content
    assert msgs[0]["role"] == "USER"
    assert msgs[0]["content"] == "Hello"
    assert msgs[1]["role"] == "ASSISTANT"
    assert msgs[2]["role"] == "USER"
    assert msgs[2]["content"] == "How are you?"
    assert msgs[3]["role"] == "ASSISTANT"


@pytest.mark.asyncio
async def test_send_message_404_invalid_session(client: AsyncClient, _session):
    user = await _create_user(_session, email="send_404@example.com")
    resp = await client.post(
        "/chat/sessions/99999/messages",
        data={"user_id": str(user.id), "message": "Hello"},
    )
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_get_messages_404_invalid_session(client: AsyncClient, _session):
    user = await _create_user(_session, email="get_msgs_404@example.com")
    resp = await client.get(f"/chat/sessions/99999/messages?user_id={user.id}")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_upload_context_200(client: AsyncClient, _session):
    user = await _create_user(_session, email="upload_chat@example.com")
    create_resp = await client.post(
        "/chat/sessions", data={"user_id": str(user.id), "title": "Upload Chat"}
    )
    session_id = create_resp.json()["id"]

    file_content = b"some context data"
    files = {"file": ("context.txt", file_content, "text/plain")}
    data = {"user_id": str(user.id)}

    resp = await client.post(
        f"/chat/sessions/{session_id}/upload", data=data, files=files
    )
    assert resp.status_code == 200
    assert resp.json().get("detail") == "File uploaded"


@pytest.mark.asyncio
async def test_upload_context_404_invalid_session(client: AsyncClient, _session):
    user = await _create_user(_session, email="upload_404@example.com")
    file_content = b"some context data"
    files = {"file": ("context.txt", file_content, "text/plain")}
    data = {"user_id": str(user.id)}

    resp = await client.post("/chat/sessions/99999/upload", data=data, files=files)
    assert resp.status_code == 404 