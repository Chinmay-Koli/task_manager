from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, APIKeyHeader
from sqlalchemy.orm import Session
import os
import secrets
import hashlib

from app.database import get_db
from app.models import User, APIKey
from app.schemas import TokenData

# Security configuration
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-this-in-production")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Get password hash"""
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """Get current user from token"""
    credential_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credential_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credential_exception

    user = db.query(User).filter(User.username == token_data.username).first()
    if user is None:
        raise credential_exception
    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """Get current active user"""
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


# ==================== API KEY MANAGEMENT ====================

def generate_api_key() -> tuple[str, str]:
    """
    Generate a new API key.
    Returns: (plain_key, prefix) where:
    - plain_key: Full API key to show user once (e.g., "tm_a1b2c3d4e5f6...")
    - prefix: First 8 chars for identification
    """
    # Generate 32 random bytes = 64 hex characters
    random_bytes = secrets.token_hex(32)
    api_key = f"tm_{random_bytes}"  # Prefix with "tm_" for Task Manager
    prefix = api_key[:10]  # Get first 10 chars including prefix
    return api_key, prefix


def hash_api_key(api_key: str) -> str:
    """Hash API key using SHA-256"""
    return hashlib.sha256(api_key.encode()).hexdigest()


def verify_api_key(plain_key: str, hashed_key: str) -> bool:
    """Verify if plain key matches hashed key"""
    return hash_api_key(plain_key) == hashed_key


# API Key Header for validation
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


async def get_user_from_api_key(
    api_key: Optional[str] = Depends(api_key_header),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """
    Extract user from API key.
    Returns None if no API key provided (for optional auth).
    Raises 401 if API key is invalid.
    """
    if not api_key:
        return None
    
    # Hash the provided key
    hashed_provided_key = hash_api_key(api_key)
    
    # Find API key in database
    db_api_key = db.query(APIKey).filter(
        APIKey.hashed_key == hashed_provided_key
    ).first()
    
    if not db_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key"
        )
    
    # Check if API key is active
    if not db_api_key.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key is inactive"
        )
    
    # Check if API key has expired
    if db_api_key.expires_at and db_api_key.expires_at < datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key has expired"
        )
    
    # Update last used timestamp
    db_api_key.last_used_at = datetime.utcnow()
    db.add(db_api_key)
    db.commit()
    
    # Return the associated user
    user = db.query(User).filter(User.id == db_api_key.user_id).first()
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account is inactive"
        )
    
    return user


async def get_current_user_or_api_key(
    current_user: Optional[User] = Depends(get_current_user),
    api_user: Optional[User] = Depends(get_user_from_api_key),
) -> User:
    """
    Get user from either JWT token or API key.
    Prioritizes JWT token if both are provided.
    """
    user = current_user or api_user
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
    return user
