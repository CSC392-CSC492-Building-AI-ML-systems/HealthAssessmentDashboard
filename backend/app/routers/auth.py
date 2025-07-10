from fastapi import APIRouter, Depends, HTTPException, status, Response
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.responses import JSONResponse

from app.db.sqlite import get_db
from app.schemas.user import UserCreate, UserRead
from app.services.auth_service import AuthService
from fastapi import Cookie
from app.core.config import settings

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

# Cookie settings
REFRESH_TOKEN_KEY = "refresh_token"
COOKIE_MAX_AGE = 60 * 60 * 24 * 7  # 7 days

# Helper function to get auth service
async def get_auth_service(db: AsyncSession = Depends(get_db)) -> AuthService:
    async with db as session:
        return AuthService(session)

@router.post("/signup", response_model=dict)
async def signup(
    user_data: UserCreate,
    auth_service: AuthService = Depends(get_auth_service)
):
    """Register a new user and return access and refresh tokens."""
    user = await auth_service.create_user(user_data)
    
    access_token = auth_service.create_access_token(user.id)
    refresh_token = auth_service.create_refresh_token(user.id)
    
    response = JSONResponse(
        content={
            "access_token": access_token,
            "token_type": "bearer"
        }
    )
    response.set_cookie(
        key=REFRESH_TOKEN_KEY,
        value=refresh_token,
        httponly=True,
        secure=settings.COOKIE_SECURE,
        samesite="strict",  # CSRF protection
        max_age=COOKIE_MAX_AGE,
        path="/auth/refresh"  # Only sent to refresh endpoint
    )
    
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
    
    access_token = auth_service.create_access_token(user.id)
    refresh_token = auth_service.create_refresh_token(user.id)
    
    # Set refresh token as httpOnly cookie
    response.set_cookie(
        key=REFRESH_TOKEN_KEY,
        value=refresh_token,
        httponly=True,
        secure=settings.COOKIE_SECURE,
        samesite="strict",  # CSRF protection
        max_age=COOKIE_MAX_AGE,
        path="/auth/refresh"  # Only sent to refresh endpoint
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }

@router.post("/refresh")
async def refresh_token(
    response: Response,
    refresh_token: str = Cookie(None, alias=REFRESH_TOKEN_KEY),
    auth_service: AuthService = Depends(get_auth_service)
):
    """Get a new access token using the refresh token from httpOnly cookie."""
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token missing",
        )

    user_id = auth_service.verify_token(refresh_token, "refresh")
    if not user_id:
        response.delete_cookie(REFRESH_TOKEN_KEY)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )
    
    # Generate new tokens
    access_token = auth_service.create_access_token(user_id)
    new_refresh_token = auth_service.create_refresh_token(user_id)
    
    # Update refresh token cookie
    response.set_cookie(
        key=REFRESH_TOKEN_KEY,
        value=new_refresh_token,
        httponly=True,
        secure=settings.COOKIE_SECURE,
        samesite="strict",
        max_age=COOKIE_MAX_AGE,
        path="/auth/refresh"
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }

@router.post("/logout")
async def logout(response: Response):
    """Clear the refresh token cookie."""
    response.delete_cookie(
        key=REFRESH_TOKEN_KEY,
        path="/auth/refresh"
    )
    return {"message": "Successfully logged out"}
