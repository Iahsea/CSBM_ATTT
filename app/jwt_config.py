"""
JWT Configuration & Token Management
"""
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from pydantic import BaseModel
from dotenv import load_dotenv
import os

# Load env
load_dotenv()

# JWT Secret Key - from .env hoặc default
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MINUTES", "60"))


class TokenData(BaseModel):
    """Token payload structure"""
    username: str
    user_id: int
    role: str
    exp: datetime = None


def create_access_token(
    username: str,
    user_id: int,
    role: str,
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    Tạo JWT access token.
    
    Args:
        username: Tên đăng nhập
        user_id: User ID
        role: User role (user, admin, etc)
        expires_delta: Thời gian hết hạn token (default: 1 hour)
    
    Returns:
        JWT token string
    """
    if expires_delta is None:
        expires_delta = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    expire = datetime.utcnow() + expires_delta
    
    to_encode = {
        "username": username,
        "user_id": user_id,
        "role": role,
        "exp": expire
    }
    
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(token: str) -> Optional[TokenData]:
    """
    Xác thực JWT token.
    
    Args:
        token: JWT token string
    
    Returns:
        TokenData nếu hợp lệ, None nếu không
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("username")
        user_id: int = payload.get("user_id")
        role: str = payload.get("role")
        
        if username is None or user_id is None:
            return None
        
        return TokenData(
            username=username,
            user_id=user_id,
            role=role
        )
    except JWTError:
        return None
