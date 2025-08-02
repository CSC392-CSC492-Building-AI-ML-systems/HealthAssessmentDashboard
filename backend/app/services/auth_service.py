import uuid
from datetime import datetime, timedelta
from typing import Optional
from passlib.context import CryptContext
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status, Depends, Cookie
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.models.user import User
from app.schemas.user import UserCreate
from app.core.config import settings
from app.db.sqlite import get_db

# Configure password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Configure JWT
SECRET_KEY = settings.jwt_secret_key
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

class AuthService:
    def __init__(self, db: AsyncSession):
        self._db = db

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str) -> str:
        return pwd_context.hash(password)

    async def authenticate_user(self, email: str, password: str) -> Optional[User]:
        result = await self._db.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()
        
        # User doesn't exist
        if not user:
            return None
        # Incorrect password
        if not self.verify_password(password, user.password_hash):
            return None
        return user

    def create_token(self, data: dict, expires_delta: Optional[timedelta] = None) -> str:
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=15)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt

    def create_access_token(self, user_id: int) -> str:
        return self.create_token(
            {"sub": str(user_id), "type": "access"},
            timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        )

    def create_refresh_token(self, user_id: int) -> str:
        return self.create_token(
            {
                "sub": str(user_id),
                "type": "refresh",
                "jti": str(uuid.uuid4()),  # ensures a unique token every time
            },
            timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS),
        )

    async def create_user(self, user_data: UserCreate) -> User:
        # Check if user already exists
        result = await self._db.execute(select(User).where(User.email == user_data.email))
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )

        # Create user
        hashed_password = self.get_password_hash(user_data.password)
        db_user = User(
            email=user_data.email,
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            password_hash=hashed_password,
            organization_id=user_data.organization_id
        )
        
        self._db.add(db_user)
        await self._db.commit()
        await self._db.refresh(db_user)
        
        return db_user

    def verify_token(self, token: str, token_type: str) -> Optional[int]:
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            if payload.get("type") != token_type:
                return None
            user_id = int(payload.get("sub"))
            return user_id
        except JWTError:
            return None


# Dependency to get the current user from JWT token
security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> User:
    """Get current user from JWT token"""
    auth_service = AuthService(db)
    user_id = auth_service.verify_token(credentials.credentials, "access")
    
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user
