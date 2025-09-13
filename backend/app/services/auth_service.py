from datetime import datetime, timedelta, timezone
from typing import Optional, Tuple
import uuid
from passlib.context import CryptContext
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status, Depends, Cookie
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dataclasses import dataclass
from fastapi.security import OAuth2PasswordBearer

from app.models.user import User
from app.schemas.user import UserCreate
from app.core.config import settings
from app.db.sqlite import get_sqlite_db
from app.db.supabase import get_db

# Configure password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Configure JWT
SECRET_KEY = settings.jwt_secret_key
ALGORITHM = settings.jwt_algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = settings.jwt_access_token_expire_minutes
REFRESH_TOKEN_EXPIRE_DAYS = settings.jwt_refresh_token_expire_days

@dataclass
class TokenConfig:
    """Configuration for token creation"""
    access_token_minutes: int = ACCESS_TOKEN_EXPIRE_MINUTES
    refresh_token_days: int = REFRESH_TOKEN_EXPIRE_DAYS
    algorithm: str = ALGORITHM
    secret_key: str = SECRET_KEY

@dataclass
class TokenPair:
    """Pair of access and refresh tokens"""
    access_token: str
    refresh_token: str

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")

class AuthService:
    def __init__(self, db: AsyncSession, config: Optional[TokenConfig] = None):
        self._db = db
        self._config = config or TokenConfig()

    # Verify a user's password
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a plain password against its hash"""
        return pwd_context.verify(plain_password, hashed_password)

    # Generate a password hash
    def get_password_hash(self, password: str) -> str:
        """Generate password hash"""
        return pwd_context.hash(password)

    # Authenticate user with email and password
    async def authenticate_user(self, email: str, password: str) -> Optional[User]:
        """Authenticate user with email and password"""
        try:
            result = await self._db.execute(select(User).where(User.email == email))
            user = result.scalar_one_or_none()
            
            # User doesn't exist
            if not user:
                return None
            # Incorrect password
            if not self.verify_password(password, user.password_hash):
                return None
            return user
        except Exception as e:
            return None

    # Create JWT tokens
    def create_token(self, data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """Create a JWT token with given data and expiration"""
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=15))
        to_encode.update({
            "exp": expire,
            "iat": datetime.now(timezone.utc),
            "jti": str(uuid.uuid4()),
        })
        return jwt.encode(to_encode, self._config.secret_key, algorithm=self._config.algorithm)

    # Create access token
    def create_access_token(self, user_id: int) -> str:
        """Create an access token for the user"""
        return self.create_token(
            {"sub": str(user_id), "type": "access"},
            timedelta(minutes=self._config.access_token_minutes)
        )

    # Create refresh token
    def create_refresh_token(self, user_id: int) -> str:
        """Create a refresh token for the user"""
        return self.create_token(
            {"sub": str(user_id), "type": "refresh"},
            timedelta(days=self._config.refresh_token_days)
        )

    # Create both access and refresh tokens
    def create_token_pair(self, user_id: int) -> TokenPair:
        """Create both access and refresh tokens for a user"""
        access_token = self.create_access_token(user_id)
        refresh_token = self.create_refresh_token(user_id)
        return TokenPair(access_token=access_token, refresh_token=refresh_token)

    # Create a new user account
    async def create_user(self, user_data: UserCreate) -> User:
        """Create a new user account"""
        try:
            # Check if user already exists
            print(user_data.email)
            print("About to execute query...")
            try:
                result = await self._db.execute(
                    select(User).where(User.email == user_data.email)
                )
                print("Query executed")
            except Exception as e:
                print("Query failed:", repr(e))
            print("REACHED")
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
        except HTTPException:
            raise
        except Exception as e:
            await self._db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create user"
            )

    # Verify JWT token and return user ID
    def verify_token(self, token: str, token_type: str) -> Optional[int]:
        """Verify a JWT token and return user ID if valid"""
        try:
            payload = jwt.decode(token, self._config.secret_key, algorithms=[self._config.algorithm])
            if payload.get("type") != token_type:
                return None
            user_id = int(payload.get("sub"))
            return user_id
        except (JWTError, ValueError, TypeError):
            return None
          
# Dependency to get the current user from JWT token
security = HTTPBearer()

# Get current user from JWT token
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
    
    try:
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        return user
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed",
            headers={"WWW-Authenticate": "Bearer"},
        )