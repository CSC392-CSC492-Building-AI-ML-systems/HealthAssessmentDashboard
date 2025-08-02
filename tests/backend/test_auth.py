import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_signup_200(client: AsyncClient, test_user):
    response = await client.post("/auth/signup", json=test_user)
    assert response.status_code == 200

    data = response.json()
    assert data["token_type"] == "bearer"
    assert "access_token" in data and data["access_token"]
    assert client.cookies.get("refresh_token") is not None


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

    login_payload = {"username": test_user["email"], "password": test_user["password"]}
    response = await client.post("/auth/login", data=login_payload)
    assert response.status_code == 200

    data = response.json()
    assert data["token_type"] == "bearer"
    assert "access_token" in data and data["access_token"]
    assert client.cookies.get("refresh_token") is not None


@pytest.mark.asyncio
async def test_login_401_invalid_credentials(client: AsyncClient, test_user):
    # Register the user first
    await client.post("/auth/signup", json=test_user)

    # Test wrong password
    login_payload = {"username": test_user["email"], "password": "wrongpassword"}
    response = await client.post("/auth/login", data=login_payload)
    assert response.status_code == 401
    assert "incorrect email or password" in response.json()["detail"].lower()

    # Test non-existent email
    login_payload = {"username": "nonexistent@example.com", "password": test_user["password"]}
    response = await client.post("/auth/login", data=login_payload)
    assert response.status_code == 401
    assert "incorrect email or password" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_refresh_200(client: AsyncClient, test_user):
    # Register + login to create the initial refresh token
    await client.post("/auth/signup", json=test_user)
    await client.post(
        "/auth/login",
        data={"username": test_user["email"], "password": test_user["password"]}
    )

    old_refresh_token = client.cookies.get("refresh_token")
    assert old_refresh_token, "Login should set the initial refresh token cookie"

    response = await client.post("/auth/refresh")
    assert response.status_code == 200

    data = response.json()
    assert data["token_type"] == "bearer"
    assert "access_token" in data and data["access_token"]

    # Should rotate the refresh token
    new_refresh_token = client.cookies.get("refresh_token")
    assert new_refresh_token and new_refresh_token != old_refresh_token


@pytest.mark.asyncio
async def test_refresh_401_no_token(client: AsyncClient):
    response = await client.post("/auth/refresh")
    assert response.status_code == 401
    assert "refresh token missing" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_refresh_401_invalid_token(client: AsyncClient):
    # Set an invalid refresh token cookie
    client.cookies.set("refresh_token", "invalid.token.here", path="/auth/refresh")
    response = await client.post("/auth/refresh")
    assert response.status_code == 401
    assert "invalid refresh token" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_logout_200(client: AsyncClient, test_user):
    # Register + login so that a refresh token is set
    await client.post("/auth/signup", json=test_user)
    await client.post(
        "/auth/login",
        data={"username": test_user["email"], "password": test_user["password"]}
    )

    assert client.cookies.get("refresh_token") is not None

    response = await client.post("/auth/logout")
    assert response.status_code == 200
    assert response.json().get("message") == "Successfully logged out"
    assert client.cookies.get("refresh_token") is None


@pytest.mark.asyncio
async def test_logout_200_without_token(client: AsyncClient):
    """Logout should succeed even if there's no refresh token."""
    response = await client.post("/auth/logout")
    assert response.status_code == 200
    assert response.json().get("message") == "Successfully logged out" 