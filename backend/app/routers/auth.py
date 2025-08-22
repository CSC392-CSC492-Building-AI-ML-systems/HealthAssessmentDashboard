from fastapi import APIRouter, Depends, HTTPException, status, Response
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.responses import JSONResponse

from app.db.sqlite import get_db
from app.schemas.user import UserCreate, UserRead
from app.services.auth_service import AuthService
from app.core.config import settings
from fastapi import Cookie
from app.core.config import settings

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

# Cookie settings
REFRESH_TOKEN_KEY = "refresh_token"
COOKIE_MAX_AGE = settings.jwt_refresh_token_expire_days * 24 * 60 * 60  # Convert days to seconds

# Helper function to get auth service
async def get_auth_service(db: AsyncSession = Depends(get_db)) -> AuthService:
    return AuthService(db)

def set_auth_cookies(response: Response, access_token: str, refresh_token: str) -> None:
    """Helper function to set authentication cookies"""
    response.set_cookie(
        key=REFRESH_TOKEN_KEY,
        value=refresh_token,
        httponly=settings.cookie_httponly,
        secure=settings.cookie_secure,
        samesite=settings.cookie_samesite,
        max_age=COOKIE_MAX_AGE,
        path="/auth/refresh"
    )

def clear_auth_cookies(response: Response) -> None:
    """Helper function to clear authentication cookies"""
    response.delete_cookie(
        key=REFRESH_TOKEN_KEY,
        path="/auth/refresh"
    )

def serialize_user_data(user) -> dict:
    """Helper function to serialize user data for response"""
    return {
        "id": user.id,
        "email": user.email,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "organization_id": user.organization_id
    }

@router.post("/signup", response_model=dict)
async def signup(
    user_data: UserCreate,
    auth_service: AuthService = Depends(get_auth_service)
):
    """Register a new user and return access and refresh tokens."""
    user = await auth_service.create_user(user_data)
    
    # Create token pair
    tokens = auth_service.create_token_pair(user.id)
    
    response = JSONResponse(
        content={
            "access_token": tokens.access_token,
            "token_type": "bearer",
            "user": serialize_user_data(user)
        }
    )
    
    set_auth_cookies(response, tokens.access_token, tokens.refresh_token)
    return response


@router.post("/login")
async def login(
    response: Response,
    form_data: OAuth2PasswordRequestForm = Depends(),
    auth_service: AuthService = Depends(get_auth_service)
):
    """Authenticate user and return access token and set refresh token cookie."""
    user = await auth_service.authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create token pair
    tokens = auth_service.create_token_pair(user.id)
    
    # Set refresh token as httpOnly cookie
    set_auth_cookies(response, tokens.access_token, tokens.refresh_token)
    
    return {
        "access_token": tokens.access_token,
        "token_type": "bearer",
        "user": serialize_user_data(user)
    }

@router.post("/refresh")
async def refresh_token(
    response: Response,
    refresh_token: str = Cookie(None, alias=REFRESH_TOKEN_KEY),
    auth_service: AuthService = Depends(get_auth_service)
):
    """Get a new access token using the refresh token from httpOnly cookie."""
    if not refresh_token:
        clear_auth_cookies(response)
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"detail": "Refresh token missing"},
            headers=response.headers,
        )

    user_id = auth_service.verify_token(refresh_token, "refresh")
    if not user_id:
        clear_auth_cookies(response)
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"detail": "Invalid refresh token"},
            headers=response.headers,
        )

    # Generate new tokens
    new_access_token = auth_service.create_access_token(user_id)
    new_refresh_token = auth_service.create_refresh_token(user_id)

    # Set new cookies
    set_auth_cookies(response, new_access_token, new_refresh_token)

    return {"access_token": new_access_token, "token_type": "bearer"}

@router.post("/logout")
async def logout(response: Response):
    """Clear the refresh token cookie."""
    clear_auth_cookies(response)
    return {"message": "Successfully logged out"}
