import pytest
from httpx import AsyncClient

REFRESH_COOKIE_NAME = "refresh_token"
REFRESH_COOKIE_PATH = "/auth/refresh"


def _get_refresh_cookie_value(client: AsyncClient):
    for c in client.cookies.jar:
        if c.name == REFRESH_COOKIE_NAME and c.path == REFRESH_COOKIE_PATH:
            return c.value
    return None


@pytest.mark.asyncio
async def test_signup_200(client: AsyncClient, test_user):
    response = await client.post("/auth/signup", json=test_user)
    assert response.status_code == 200
    data = response.json()
    assert data["token_type"] == "bearer"
    assert data.get("access_token")
    assert _get_refresh_cookie_value(client) is not None


@pytest.mark.asyncio
async def test_signup_400_duplicate_email(client: AsyncClient, test_user):
    # First signup should succeed
    await client.post("/auth/signup", json=test_user)
    
    # Second signup with same email should fail
    response = await client.post("/auth/signup", json=test_user)
    assert response.status_code == 400
    assert "email already registered" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_signup_422_missing_fields(client: AsyncClient, test_user):
    # Test missing email
    invalid_user = test_user.copy()
    invalid_user.pop("email")
    response = await client.post("/auth/signup", json=invalid_user)
    assert response.status_code == 422

    # Test missing password
    invalid_user = test_user.copy()
    invalid_user.pop("password")
    response = await client.post("/auth/signup", json=invalid_user)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_login_200(client: AsyncClient, test_user):
    # First register the user
    await client.post("/auth/signup", json=test_user)
    response = await client.post("/auth/login", data={"username": test_user["email"], "password": test_user["password"]})
    assert response.status_code == 200
    data = response.json()
    assert data["token_type"] == "bearer"
    assert data.get("access_token")
    assert _get_refresh_cookie_value(client) is not None


@pytest.mark.asyncio
async def test_login_401_invalid_credentials(client: AsyncClient, test_user):
    # Register the user first
    await client.post("/auth/signup", json=test_user)

    # Test wrong password
    response = await client.post("/auth/login", data={"username": test_user["email"], "password": "wrongpassword"})
    assert response.status_code == 401
    assert "incorrect email or password" in response.json()["detail"].lower()

    # Test non-existent email
    response = await client.post("/auth/login", data={"username": "nonexistent@example.com", "password": test_user["password"]})
    assert response.status_code == 401
    assert "incorrect email or password" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_refresh_200(client: AsyncClient, test_user):
    # Register + login to create the initial refresh token
    await client.post("/auth/signup", json=test_user)
    await client.post("/auth/login", data={"username": test_user["email"], "password": test_user["password"]})
    old_refresh = _get_refresh_cookie_value(client)
    assert old_refresh
    response = await client.post("/auth/refresh")
    assert response.status_code == 200
    data = response.json()
    assert data["token_type"] == "bearer"
    # Should rotate the refresh token
    assert data.get("access_token")
    new_refresh = _get_refresh_cookie_value(client)
    assert new_refresh and new_refresh != old_refresh


@pytest.mark.asyncio
async def test_refresh_multiple_rotations(client: AsyncClient, test_user):
    await client.post("/auth/signup", json=test_user)
    await client.post("/auth/login", data={"username": test_user["email"], "password": test_user["password"]})
    seen = set()
    for _ in range(3):
        current = _get_refresh_cookie_value(client)
        assert current and current not in seen
        seen.add(current)
        resp = await client.post("/auth/refresh")
        assert resp.status_code == 200


@pytest.mark.asyncio
async def test_refresh_401_no_token(client: AsyncClient):
    response = await client.post("/auth/refresh")
    assert response.status_code == 401
    assert "refresh token missing" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_refresh_401_invalid_token(client: AsyncClient):
    # Set an invalid refresh token cookie
    client.cookies.set(REFRESH_COOKIE_NAME, "invalid.token.here", path=REFRESH_COOKIE_PATH)
    response = await client.post("/auth/refresh")
    assert response.status_code == 401
    assert "invalid refresh token" in response.json()["detail"].lower()
    # Should be cleared by server (value is empty string "")
    set_cookie = response.headers["set-cookie"].lower()
    assert set_cookie.startswith("refresh_token=")
    assert '=""' in set_cookie  # empty cookie value



@pytest.mark.asyncio
async def test_refresh_401_cookie_wrong_path_not_sent(client: AsyncClient):
    client.cookies.set(REFRESH_COOKIE_NAME, "somevalue", path="/other")
    response = await client.post("/auth/refresh")
    assert response.status_code == 401
    assert "refresh token missing" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_logout_200(client: AsyncClient, test_user):
    # Register + login so that a refresh token is set
    await client.post("/auth/signup", json=test_user)
    await client.post("/auth/login", data={"username": test_user["email"], "password": test_user["password"]})
    assert _get_refresh_cookie_value(client) is not None
    response = await client.post("/auth/logout")
    assert response.status_code == 200
    assert response.json().get("message") == "Successfully logged out"
    assert _get_refresh_cookie_value(client) is None


@pytest.mark.asyncio
async def test_logout_200_without_token(client: AsyncClient):
    """Logout should succeed even if there's no refresh token."""
    response = await client.post("/auth/logout")
    assert response.status_code == 200
    assert response.json().get("message") == "Successfully logged out"
