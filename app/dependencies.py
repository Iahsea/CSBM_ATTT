"""
JWT Dependencies for fastapi
"""
from fastapi import Depends, HTTPException, status, Header
from typing import Optional
from .jwt_config import verify_token, TokenData


async def get_current_user(
    authorization: Optional[str] = Header(None)
) -> TokenData:
    """
    Dependency để verify JWT token từ Authorization header.
    
    Usage:
        @router.get("/users")
        async def get_users(current_user: TokenData = Depends(get_current_user)):
            ...
    
    Header format: Authorization: Bearer <token>
    
    Raises:
        HTTPException: 401 nếu token không hợp lệ
    """
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authorization header",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    # Parse "Bearer <token>"
    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise ValueError("Invalid scheme")
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header format",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    # Verify token
    token_data = verify_token(token)
    
    if token_data is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    return token_data


async def get_current_admin(
    current_user: TokenData = Depends(get_current_user)
) -> TokenData:
    """
    Dependency để verify JWT token + admin role.
    
    Usage:
        @router.delete("/users/{id}")
        async def delete_user(
            user_id: int,
            current_admin: TokenData = Depends(get_current_admin)
        ):
            ...
    
    Raises:
        HTTPException: 403 nếu không phải admin
    """
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    return current_user
