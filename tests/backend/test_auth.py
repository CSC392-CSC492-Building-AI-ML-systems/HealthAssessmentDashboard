import pytest


@pytest.mark.asyncio
async def test_signup_success(client, test_user):
    response = await client.post("/auth/signup", json=test_user)
    assert response.status_code == 200

    data = response.json()
    assert data["token_type"] == "bearer"
    assert "access_token" in data and data["access_token"]

    # The refresh token is stored as an httpOnly cookie. Ensure it was set.
    assert client.cookies.get("refresh_token") is not None


@pytest.mark.asyncio
async def test_login_success(client, test_user):
    # First register the user so that it exists in the DB.
    await client.post("/auth/signup", json=test_user)

    # Perform the login using form data as required by OAuth2PasswordRequestForm.
    login_payload = {"username": test_user["email"], "password": test_user["password"]}
    response = await client.post("/auth/login", data=login_payload)
    assert response.status_code == 200

    data = response.json()
    assert data["token_type"] == "bearer"
    assert "access_token" in data and data["access_token"]

    # A refresh token cookie should be part of the response.
    assert client.cookies.get("refresh_token") is not None


@pytest.mark.asyncio
async def test_refresh_success(client, test_user):
    # Register + login to create the initial refresh token cookie.
    await client.post("/auth/signup", json=test_user)
    await client.post("/auth/login", data={"username": test_user["email"], "password": test_user["password"]})

    old_refresh_token = client.cookies.get("refresh_token")
    assert old_refresh_token, "Login should set the initial refresh token cookie"

    # Call the refresh endpoint; the same client instance will automatically
    # include the cookie in the request.
    response = await client.post("/auth/refresh")
    assert response.status_code == 200

    data = response.json()
    assert data["token_type"] == "bearer"
    assert "access_token" in data and data["access_token"]

    # The refresh endpoint should rotate the refresh token.
    new_refresh_token = client.cookies.get("refresh_token")
    assert new_refresh_token and new_refresh_token != old_refresh_token


@pytest.mark.asyncio
async def test_logout_success(client, test_user):
    # Register + login so that a refresh token is set.
    await client.post("/auth/signup", json=test_user)
    await client.post("/auth/login", data={"username": test_user["email"], "password": test_user["password"]})

    assert client.cookies.get("refresh_token") is not None, "Refresh token should be present before logout"

    response = await client.post("/auth/logout")
    assert response.status_code == 200
    assert response.json().get("message") == "Successfully logged out"

    # The client cookie jar should no longer hold the refresh token.
    assert client.cookies.get("refresh_token") is None 