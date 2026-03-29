"""
Authentication Routes: Login & Auth management
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel

from ..database import get_db
from ..models import User
from ..crud import UserCRUD
from ..security import verify_password, encrypt, decrypt, generate_key
from ..jwt_config import create_access_token, TokenData

router = APIRouter(
    prefix="/auth",
    tags=["auth"],
    responses={404: {"model": dict}}
)


# ==================== Schemas ====================

class LoginRequest(BaseModel):
    """
    Schema cho login request
    """
    username: str
    password: str

    class Config:
        example = {
            "username": "admin",
            "password": "123456"
        }


class LoginResponse(BaseModel):
    """
    Schema cho login response
    """
    access_token: str
    token_type: str = "bearer"
    user_id: int
    username: str
    role: str

    class Config:
        example = {
            "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
            "token_type": "bearer",
            "user_id": 1,
            "username": "admin",
            "role": "admin"
        }


# ==================== POST /auth/login ====================

@router.post(
    "/login",
    response_model=LoginResponse,
    summary="Login user",
    description="Đăng nhập và lấy JWT token"
)
async def login(
    request: LoginRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Đăng nhập user.
    
    - **username**: Tên đăng nhập
    - **password**: Mật khẩu
    
    Response:
    - **access_token**: JWT token (dùng trong Authorization header)
    - **token_type**: "bearer"
    - **user_id**: ID của user
    - **username**: Tên đăng nhập
    - **role**: Role của user (user, admin)
    """
    try:
        # Lấy user by username (dùng CRUD có selectinload)
        db_user = await UserCRUD.get_user_by_username(db, request.username)
        
        if not db_user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username or password"
            )
        
        # Verify password - dùng encrypt key để decrypt password từ DB
        # Vì password được lưu encrypted, ta cần decrypt rồi so sánh
        key = generate_key(request.username, request.password)
        try:
            decrypted_password = decrypt(db_user.password, key)
        except:
            # Nếu decrypt fail = password sai
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username or password"
            )
        
        # So sánh password
        if decrypted_password != request.password:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username or password"
            )
        
        # Tạo JWT token (dùng role name từ relationship object)
        access_token = create_access_token(
            username=db_user.username,
            user_id=db_user.id,
            role=db_user.role.name  # Role đã được eager-load bởi selectinload
        )
        
        return LoginResponse(
            access_token=access_token,
            token_type="bearer",
            user_id=db_user.id,
            username=db_user.username,
            role=db_user.role.name  # Role đã available
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )
