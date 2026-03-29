"""
User Routes: API endpoints cho User management
"""
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from datetime import datetime

from ..database import get_db
from ..models import User
from ..security import encrypt, get_master_key
from ..schemas import (
    UserCreate,
    UserUpdate,
    UserResponse,
    UserCreateResponse,
    UserUpdateResponse,
    UserDeleteResponse,
    UserListResponse,
    ErrorResponse,
    DecryptUserDataRequest,
    ResetPasswordRequest
)
from ..crud import UserCRUD, decrypt_user_data, get_user_response, get_role_based_response, get_role_based_response_from_model, to_user_response, to_user_response_for_admin, to_user_response_for_admin_decrypted
from ..jwt_config import TokenData
from ..dependencies import get_current_user, get_current_admin

router = APIRouter(
    prefix="/users",
    tags=["users"],
    responses={404: {"model": ErrorResponse}}
)


# ==================== POST /users - Tạo User ====================

@router.post(
    "",
    response_model=UserCreateResponse,
    status_code=201,
    summary="Tạo user mới",
    description="Tạo user mới với encryption"
)
async def create_user(
    user: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Tạo user mới.
    
    - **username**: Tên đăng nhập (3-50 chars, duy nhất)
    - **email**: Email hợp lệ
    - **phone**: Số điện thoại (10-15 digits)
    - **password**: Mật khẩu (tối thiểu 6 ký tự)
    
    Dữ liệu sensitive (email, phone, password) sẽ được mã hóa.
    Response sẽ có masking áp dụng.
    """
    try:
        # Tạo user
        db_user = await UserCRUD.create_user(db, user)
        
        # Decrypt để hiển thị
        decrypted_data = decrypt_user_data(db_user, user.username, user.password)
        
        # Apply masking
        user_response = get_user_response(db_user, decrypted_data, mask=True)
        user_response["message"] = "User created successfully"
        
        return user_response
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


# ==================== GET /users - Lấy danh sách Users ====================

@router.get(
    "",
    response_model=UserListResponse,
    summary="Lấy danh sách users",
    description="Lấy danh sách users với pagination và role-based masking"
)
async def get_users(
    skip: int = Query(0, ge=0, description="Số records bỏ qua"),
    limit: int = Query(10, ge=1, le=100, description="Số records trả về"),
    current_user: TokenData = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Lấy danh sách users.
    
    Query parameters:
    - **skip**: Số records bỏ qua (default: 0)
    - **limit**: Số records trả về (max: 100, default: 10)
    
    Authorization:
    - Header: Authorization: Bearer <jwt_token>
    
    Response:
    - Nếu admin: Email/phone/password được hiển thị đầy đủ
    - Nếu user role: Email/phone/password được masked
    """
    try:
        total, users = await UserCRUD.get_users(db, skip=skip, limit=limit, mask=True)
        
        # Role-based response
        if current_user.role == "admin":
            # Admin xem email/phone decrypted, password masked
            user_responses = [to_user_response_for_admin_decrypted(user) for user in users]
        else:
            # User xem masked
            user_responses = [to_user_response(user) for user in users]
        
        return UserListResponse(
            total=total,
            skip=skip,
            limit=limit,
            items=user_responses
        )
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


# ==================== GET /users/{id} - Lấy User theo ID ====================

@router.get(
    "/{user_id}",
    response_model=UserResponse,
    summary="Lấy user theo ID",
    description="Lấy user theo ID với role-based masking"
)
async def get_user(
    user_id: int,
    current_user: TokenData = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Lấy user theo ID.
    
    Path parameters:
    - **user_id**: User ID
    
    Authorization:
    - Header: Authorization: Bearer <jwt_token>
    
    Response:
    - Nếu admin: Email/phone/password được hiển thị đầy đủ (nếu có endpoint decrypt)
    - Nếu user role: Email/phone/password được masked (default)
    """
    try:
        # Get user from database
        user = await UserCRUD.get_user_by_id(db, user_id, mask=True)
        
        if not user:
            raise HTTPException(status_code=404, detail=f"User with ID {user_id} not found")
        
        # Role-based response
        if current_user.role == "admin":
            # Admin xem email/phone decrypted (bằng master key), password masked
            return to_user_response_for_admin_decrypted(user)
        else:
            # User chỉ xem chính mình
            if current_user.user_id != user_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You can only view your own information"
                )
            # User xem chính mình - hiển thị masked
            return to_user_response(user)
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


# ==================== POST /users/{id}/decrypt-info - Xem Full Decrypted Data ====================

@router.post(
    "/{user_id}/decrypt-info",
    response_model=UserResponse,
    summary="Xem thông tin user đã decrypt",
    description="Admin hoặc user nhập password để xem full email/phone/password (decrypted)"
)
async def view_decrypted_user_info(
    user_id: int,
    request: DecryptUserDataRequest,
    current_user: TokenData = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Xem full decrypted user data.
    
    Path parameters:
    - **user_id**: User ID
    
    Request body:
    - **password**: Password của user đó (để decrypt email/phone)
    
    Authorization:
    - Header: Authorization: Bearer <jwt_token>
    - Chỉ admin hoặc chính user đó mới có quyền
    
    Response:
    - Email/phone/password đã decrypt, hiển thị đầy đủ (không masked)
    """
    try:
        # Kiểm tra quyền: user chỉ xem chính mình, admin xem bất kỳ ai
        if current_user.user_id != user_id and current_user.role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to view this user's details"
            )
        
        # Get user from database
        user = await UserCRUD.get_user_by_id(db, user_id, mask=True)
        
        if not user:
            raise HTTPException(status_code=404, detail=f"User with ID {user_id} not found")
        
        # Decrypt user data với password được cung cấp
        decrypted_data = decrypt_user_data(user, user.username, request.password)
        
        # Get full response (không mask)
        user_response = get_user_response(user, decrypted_data, mask=False)
        
        return user_response
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


# ==================== POST /users/{id}/reset-password - Reset Password ====================

@router.post(
    "/{user_id}/reset-password",
    response_model=UserResponse,
    summary="Reset password user (Admin only)",
    description="Admin reset password mới cho user - password cũ không cần nhập"
)
async def reset_user_password(
    user_id: int,
    request: ResetPasswordRequest,
    current_user: TokenData = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Reset password cho user (chỉ admin).
    
    Path parameters:
    - **user_id**: User ID
    
    Request body:
    - **new_password**: New password (minimum 6 chars)
    
    Authorization:
    - Header: Authorization: Bearer <jwt_token>
    - Chỉ admin có quyền
    
    Response:
    - User data với password masked (****)
    """
    try:
        # Kiểm tra quyền: chỉ admin
        if current_user.role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only admin can reset password"
            )
        
        # Get user from database
        user = await UserCRUD.get_user_by_id(db, user_id, mask=True)
        
        if not user:
            raise HTTPException(status_code=404, detail=f"User with ID {user_id} not found")
        
        # Reset password
        master_key = get_master_key()
        user.password = encrypt(request.new_password, master_key)
        user.updated_at = datetime.utcnow()
        
        db.add(user)
        await db.commit()
        await db.refresh(user)
        
        # Return user response với password masked
        return to_user_response_for_admin_decrypted(user)
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


# ==================== PUT /users/{id} - Cập nhật User ====================

@router.put(
    "/{user_id}",
    response_model=UserUpdateResponse,
    summary="Cập nhật user",
    description="Cập nhật thông tin user"
)
async def update_user(
    user_id: int,
    user_update: UserUpdate,
    current_user: TokenData = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Cập nhật thông tin user.
    
    Path parameters:
    - **user_id**: User ID
    
    Request body:
    - **email** (optional): Email mới
    - **phone** (optional): Số điện thoại mới
    - **password** (optional): Mật khẩu mới
    - **old_password** (required if updating password): Mật khẩu hiện tại
    
    Authorization:
    - Header: Authorization: Bearer <jwt_token>
    - Chỉ user có thể cập nhật chính mình, hoặc admin cập nhật bất kỳ user nào
    
    Lưu ý:
    - Username không thể thay đổi
    - Chỉ cập nhật fields có trong request
    - Nếu cập nhật password, phải cung cấp old_password
    """
    try:
        # Kiểm tra quyền: user chỉ cập nhật chính mình, admin cập nhật bất kỳ ai
        if current_user.user_id != user_id and current_user.role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to update this user"
            )
        
        # Lấy user từ database
        db_user = await UserCRUD.get_user_by_id(db, user_id)
        
        if not db_user:
            raise HTTPException(status_code=404, detail=f"User with ID {user_id} not found")
        
        # Update user (cần username + old_password)
        old_password = user_update.old_password if user_update.password else None
        updated_user = await UserCRUD.update_user(
            db, user_id, user_update, 
            username=db_user.username,
            old_password=old_password
        )
        
        # Response (masked)
        user_response = get_user_response(updated_user, mask=True)
        user_response["message"] = "User updated successfully"
        
        return user_response
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


# ==================== DELETE /users/{id} - Xóa User ====================

@router.delete(
    "/{user_id}",
    response_model=UserDeleteResponse,
    summary="Xóa user",
    description="Xóa user khỏi database (admin only)"
)
async def delete_user(
    user_id: int,
    current_user: TokenData = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    Xóa user.
    
    Path parameters:
    - **user_id**: User ID
    
    Authorization:
    - Header: Authorization: Bearer <jwt_token>
    - Chỉ admin có thể xóa user
    """
    try:
        db_user = await UserCRUD.delete_user(db, user_id)
        
        return UserDeleteResponse(
            id=db_user.id,
            username=db_user.username,
            message="User deleted successfully"
        )
    
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
