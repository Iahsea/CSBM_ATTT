"""
Pydantic Schemas: Request/Response models
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime


# ==================== Role Schemas ====================

class RoleResponse(BaseModel):
    """
    Schema cho response chứa role information
    """
    id: int
    name: str
    description: Optional[str] = None
    created_at: Optional[datetime] = None

    class Config:
        example = {
            "id": 1,
            "name": "admin",
            "description": "Administrator - full access",
            "created_at": "2026-03-28T10:30:45"
        }


# ==================== Request Schemas ====================

class UserCreate(BaseModel):
    """
    Schema cho tạo user mới (POST /users)
    """
    username: str = Field(..., min_length=3, max_length=50, description="Username (3-50 chars)")
    email: EmailStr = Field(..., description="Valid email address")
    phone: str = Field(..., min_length=10, max_length=15, description="Phone number (10-15 digits)")
    password: str = Field(..., min_length=6, description="Password (minimum 6 chars)")
    role: str = Field(default="user", description="User role name (user/admin)")

    class Config:
        example = {
            "username": "john_doe",
            "email": "john@gmail.com",
            "phone": "0987654321",
            "password": "SecurePass123",
            "role": "user"
        }


class UserUpdate(BaseModel):
    """
    Schema cho cập nhật user (PUT /users/{id})
    Tất cả fields đều optional.
    Nếu cập nhật password, phải cung cấp old_password để verify
    """
    email: Optional[EmailStr] = Field(None, description="New email")
    phone: Optional[str] = Field(None, min_length=10, max_length=15, description="New phone")
    password: Optional[str] = Field(None, min_length=6, description="New password")
    old_password: Optional[str] = Field(None, description="Current password (required if updating password)")

    class Config:
        example = {
            "email": "john.new@gmail.com",
            "phone": "0912345678",
            "password": "NewPassword123",
            "old_password": "OldPassword123"
        }


class DecryptUserDataRequest(BaseModel):
    """
    Schema cho request xem full decrypted user data (POST /users/{id}/decrypt-info)
    Admin cần nhập password của user để decrypt email/phone/password
    """
    password: str = Field(..., description="Password của user đó")

    class Config:
        example = {
            "password": "userPassword123"
        }


class ResetPasswordRequest(BaseModel):
    """
    Schema cho request reset password (POST /users/{id}/reset-password)
    Admin reset password mới cho user - chỉ admin có quyền
    """
    new_password: str = Field(..., min_length=6, description="New password (minimum 6 chars)")

    class Config:
        example = {
            "new_password": "NewPassword123"
        }


# ==================== Response Schemas ====================

class UserResponse(BaseModel):
    """
    Schema cho trả về user data (GET /users)
    Có áp dụng masking hoặc không tùy theo role
    """
    id: int
    username: str
    email: str  # Có thể là masked hoặc plain text
    phone: str  # Có thể là masked hoặc plain text
    password: Optional[str] = None  # Thường là masked hoặc không trả về
    role: str  # User role
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        example = {
            "id": 1,
            "username": "john_doe",
            "email": "j***@gmail.com",  # Masked (nếu user role)
            "phone": "09****21",         # Masked (nếu user role)
            "password": "***",           # Masked
            "role": "user",
            "created_at": "2026-03-28T10:30:45",
            "updated_at": "2026-03-28T10:30:45"
        }


class UserCreateResponse(BaseModel):
    """
    Schema cho response khi tạo user (POST /users success)
    """
    id: int
    username: str
    email: str  # Masked
    phone: str  # Masked
    password: str  # Masked (always ***)
    message: str = "User created successfully"
    created_at: Optional[datetime] = None

    class Config:
        example = {
            "id": 1,
            "username": "john_doe",
            "email": "j***@gmail.com",
            "phone": "09****21",
            "password": "***",
            "message": "User created successfully",
            "created_at": "2026-03-28T10:30:45"
        }


class UserUpdateResponse(BaseModel):
    """
    Schema cho response khi cập nhật user (PUT /users/{id} success)
    """
    id: int
    username: str
    email: str  # Masked
    phone: str  # Masked
    message: str = "User updated successfully"
    updated_at: Optional[datetime] = None

    class Config:
        example = {
            "id": 1,
            "username": "john_doe",
            "email": "j***@gmail.com",
            "phone": "09****78",
            "message": "User updated successfully",
            "updated_at": "2026-03-28T14:30:45"
        }


class UserDeleteResponse(BaseModel):
    """
    Schema cho response khi xóa user (DELETE /users/{id} success)
    """
    id: int
    username: str
    message: str = "User deleted successfully"

    class Config:
        example = {
            "id": 1,
            "username": "john_doe",
            "message": "User deleted successfully"
        }


class UserListResponse(BaseModel):
    """
    Schema cho trả về danh sách users (GET /users)
    """
    total: int
    skip: int
    limit: int
    items: List[UserResponse]

    class Config:
        example = {
            "total": 3,
            "skip": 0,
            "limit": 10,
            "items": [
                {
                    "id": 1,
                    "username": "john_doe",
                    "email": "j***@gmail.com",
                    "phone": "09****21",
                    "password": "***",
                    "created_at": "2026-03-28T10:30:45"
                }
            ]
        }


# ==================== Error Schemas ====================

class ErrorResponse(BaseModel):
    """
    Schema cho error response
    """
    error: str
    detail: str

    class Config:
        example = {
            "error": "User not found",
            "detail": "User with ID 999 does not exist"
        }


class ValidationErrorResponse(BaseModel):
    """
    Schema cho validation error response
    """
    error: str
    detail: str

    class Config:
        example = {
            "error": "Invalid email format",
            "detail": "Email must be a valid email address"
        }
