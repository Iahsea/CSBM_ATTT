"""
CRUD Operations: Create, Read, Update, Delete
Quản lý database operations
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import selectinload
from .models import User, Role
from .schemas import UserCreate, UserUpdate
from .security import (
    encrypt,
    decrypt,
    generate_key,
    apply_masking,
    mask_email,
    mask_phone,
    get_master_key,
)
from datetime import datetime
import base64


def to_user_response(user: User) -> dict:
    """
    Convert User model to user response dict with masked email/phone.
    
    Args:
        user: User model instance (với eager-loaded role relationship)
    
    Returns:
        dict: User response với masked email/phone
    """
    # Email và phone đã encrypted nên không thể mask trực tiếp
    # Ta hiển thị masked pattern "***@***" và "****"
    return {
        "id": user.id,
        "username": user.username,
        "email": "***@***",
        "phone": "****",
        "role": user.role.name if user.role else "user",
        "created_at": user.created_at.isoformat() if user.created_at else None,
        "updated_at": user.updated_at.isoformat() if user.updated_at else None
    }


def to_user_response_for_admin(user: User) -> dict:
    """
    Convert User model to response dict for admin view.
    Cho admin xem encrypted data (không decrypt).
    Encrypted bytes được convert sang base64 string để serialize thành JSON.
    
    Args:
        user: User model instance (với eager-loaded role relationship)
    
    Returns:
        dict: User response với encrypted email/phone (base64 encoded, không mask)
    """
    def bytes_to_base64(data: bytes) -> str:
        """Convert bytes to base64 string, or return (blank) if None"""
        if not data:
            return "(blank)"
        try:
            return base64.b64encode(data).decode('utf-8')
        except:
            return "(error)"
    
    return {
        "id": user.id,
        "username": user.username,
        "email": bytes_to_base64(user.email),      # Encrypted → base64
        "phone": bytes_to_base64(user.phone),      # Encrypted → base64
        "password": bytes_to_base64(user.password),  # Encrypted → base64
        "role": user.role.name if user.role else "user",
        "created_at": user.created_at.isoformat() if user.created_at else None,
        "updated_at": user.updated_at.isoformat() if user.updated_at else None
    }


def to_user_response_for_admin_decrypted(user: User) -> dict:
    """
    Convert User model to response dict for admin view (with decrypted email/phone).
    Admin xem email/phone decrypted (bằng master key), password luôn masked.
    
    Args:
        user: User model instance (với eager-loaded role relationship)
    
    Returns:
        dict: User response với email/phone decrypted, password masked
    """
    master_key = get_master_key()
    
    # Decrypt email/phone bằng master key
    decrypted_email = decrypt(user.email, master_key) if user.email else ""
    decrypted_phone = decrypt(user.phone, master_key) if user.phone else ""
    
    return {
        "id": user.id,
        "username": user.username,
        "email": decrypted_email,           # Decrypted via master key
        "phone": decrypted_phone,           # Decrypted via master key
        "password": "***",                  # Always masked
        "role": user.role.name if user.role else "user",
        "created_at": user.created_at.isoformat() if user.created_at else None,
        "updated_at": user.updated_at.isoformat() if user.updated_at else None
    }


class RoleCRUD:
    """CRUD operations cho Role model"""
    
    @staticmethod
    async def get_role_by_name(db: AsyncSession, name: str) -> Role:
        """
        Get role by name (admin, user)
        """
        query = select(Role).where(Role.name == name)
        result = await db.execute(query)
        return result.scalar_one_or_none()


class UserCRUD:
    """
    CRUD operations cho User model
    """

    @staticmethod
    async def create_user(db: AsyncSession, user: UserCreate) -> User:
        """
        Tạo user mới với encryption.
        
        Args:
            db: Database session
            user: UserCreate schema
        
        Returns:
            User model instance
        
        Raises:
            ValueError: Nếu duplicate username hoặc role không tồn tại
        """
        try:
            # Get role by name
            role_query = select(Role).where(Role.name == user.role)
            role_result = await db.execute(role_query)
            db_role = role_result.scalar_one_or_none()
            
            if not db_role:
                raise ValueError(f"Role '{user.role}' does not exist")
            
            # Generate keys
            per_user_key = generate_key(user.username, user.password)
            master_key = get_master_key()
            
            # Encrypt sensitive fields
            encrypted_email = encrypt(user.email, master_key)
            encrypted_phone = encrypt(user.phone, master_key)
            encrypted_password = encrypt(user.password, per_user_key)
            
            # Create user instance
            db_user = User(
                username=user.username,
                email=encrypted_email,
                phone=encrypted_phone,
                password=encrypted_password,
                role_id=db_role.id,  # Use role_id instead of role
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            
            # Save to database
            db.add(db_user)
            await db.commit()
            
            # Refresh with role relationship loaded
            await db.refresh(db_user)
            # Need to reload with selectinload to avoid greenlet issue
            query = select(User).where(User.id == db_user.id).options(selectinload(User.role))
            result = await db.execute(query)
            db_user = result.scalar_one_or_none()
            
            return db_user
        
        except IntegrityError:
            await db.rollback()
            raise ValueError(f"Username '{user.username}' already exists")


    @staticmethod
    async def get_user_by_id(db: AsyncSession, user_id: int, mask: bool = True) -> User:
        """
        Lấy user theo ID (không decrypt - return encrypted).
        
        Args:
            db: Database session
            user_id: User ID
            mask: Áp dụng masking hay không (không dùng, vì encrypted)
        
        Returns:
            User model instance
        
        Raises:
            ValueError: Nếu user không tồn tại
        """
        query = select(User).where(User.id == user_id).options(selectinload(User.role))
        result = await db.execute(query)
        db_user = result.scalar_one_or_none()
        
        if not db_user:
            raise ValueError(f"User with ID {user_id} does not exist")
        
        return db_user


    @staticmethod
    async def get_user_by_username(db: AsyncSession, username: str) -> User:
        """
        Lấy user theo username.
        
        Args:
            db: Database session
            username: Username
        
        Returns:
            User model instance hoặc None
        """
        query = select(User).where(User.username == username).options(selectinload(User.role))
        result = await db.execute(query)
        return result.scalar_one_or_none()


    @staticmethod
    async def get_users(db: AsyncSession, skip: int = 0, limit: int = 10, mask: bool = True) -> tuple:
        """
        Lấy danh sách users với pagination (không decrypt - return encrypted).
        
        Args:
            db: Database session
            skip: Số records bỏ qua
            limit: Số records trả về
            mask: Áp dụng masking hay không
        
        Returns:
            (total_count, users_list)
        """
        # Get total count
        count_query = select(User)
        count_result = await db.execute(count_query)
        total = len(count_result.all())
        
        # Get paginated users
        query = select(User).offset(skip).limit(limit).options(selectinload(User.role))
        result = await db.execute(query)
        users = result.scalars().all()
        
        return total, users


    @staticmethod
    async def update_user(db: AsyncSession, user_id: int, user_update: UserUpdate, username: str, old_password: str = None) -> User:
        """
        Cập nhật user với re-encryption.
        
        Args:
            db: Database session
            user_id: User ID
            user_update: UserUpdate schema
            username: Username (để sinh key)
            old_password: Old password (để decrypt dữ liệu cũ, required nếu update password)
        
        Returns:
            Updated User model instance
        
        Raises:
            ValueError: Nếu user không tồn tại hoặc password sai
        """
        query = select(User).where(User.id == user_id)
        result = await db.execute(query)
        db_user = result.scalar_one_or_none()
        
        if not db_user:
            raise ValueError(f"User with ID {user_id} does not exist")
        
        master_key = get_master_key()
        
        # Nếu update password, cần verify old_password
        if user_update.password:
            if not old_password:
                raise ValueError("old_password is required to update password")
            
            # Verify old password using per-user key
            old_key = generate_key(username, old_password)
            try:
                decrypted_old_password = decrypt(db_user.password, old_key)
            except Exception:
                raise ValueError("Invalid old password")
            
            if decrypted_old_password != old_password:
                raise ValueError("Invalid old password")
            
            # Update password với new per-user key
            new_key = generate_key(username, user_update.password)
            db_user.password = encrypt(user_update.password, new_key)
            
            # Ensure email/phone are stored with master key (migrate if needed)
            if db_user.email:
                try:
                    decrypted_email = decrypt(db_user.email, master_key)
                except Exception:
                    decrypted_email = decrypt(db_user.email, old_key)
                db_user.email = encrypt(decrypted_email, master_key)
            
            if db_user.phone:
                try:
                    decrypted_phone = decrypt(db_user.phone, master_key)
                except Exception:
                    decrypted_phone = decrypt(db_user.phone, old_key)
                db_user.phone = encrypt(decrypted_phone, master_key)
        else:
            # Không update password
            if user_update.email:
                db_user.email = encrypt(user_update.email, master_key)
            if user_update.phone:
                db_user.phone = encrypt(user_update.phone, master_key)
        
        db_user.updated_at = datetime.utcnow()
        
        db.add(db_user)
        await db.commit()
        await db.refresh(db_user)
        
        return db_user


    @staticmethod
    async def delete_user(db: AsyncSession, user_id: int) -> User:
        """
        Xóa user.
        
        Args:
            db: Database session
            user_id: User ID
        
        Returns:
            Deleted User model instance
        
        Raises:
            ValueError: Nếu user không tồn tại
        """
        query = select(User).where(User.id == user_id)
        result = await db.execute(query)
        db_user = result.scalar_one_or_none()
        
        if not db_user:
            raise ValueError(f"User with ID {user_id} does not exist")
        
        await db.delete(db_user)
        await db.commit()
        
        return db_user


# ==================== Helper Functions ====================

def _decrypt_and_mask_user(user: User, username: str, password: str, mask: bool = True) -> dict:
    """
    Decrypt user data và áp dụng masking.
    
    Args:
        user: User model instance
        username: Username (để sinh key)
        password: Password plain text (để sinh key)
        mask: Áp dụng masking hay không
    
    Returns:
        dict: User data (decrypted, có hoặc không masked)
    """
    # Decrypt dữ liệu nhạy cảm
    decrypted_data = decrypt_user_data(user, username, password)
    
    # Merge với model data + apply masking
    user_response = get_user_response(user, decrypted_data, mask=mask)
    
    return user_response


def decrypt_user_data(user: User, username: str, password: str) -> dict:
    """
    Decrypt user data với username + password.
    
    Args:
        user: User model instance
        username: Username
        password: Password (plain text)
    
    Returns:
        dict: User data (decrypted)
    """
    key = generate_key(username, password)
    
    decrypted_email = decrypt(user.email, key) if user.email else None
    decrypted_phone = decrypt(user.phone, key) if user.phone else None
    decrypted_password = decrypt(user.password, key) if user.password else None
    
    return {
        "email": decrypted_email,
        "phone": decrypted_phone,
        "password": decrypted_password
    }


def get_user_response(user: User, decrypted_data: dict = None, mask: bool = True) -> dict:
    """
    Get user response (merged model + decrypted data + masking).
    
    Args:
        user: User model instance
        decrypted_data: Dict with decrypted email/phone/password
        mask: Áp dụng masking hay không
    
    Returns:
        dict: User response
    """
    user_data = user.to_dict(decrypted_data)
    masked_data = apply_masking(user_data, mask=mask)
    return masked_data


def get_role_based_response(user: User, decrypted_data: dict = None, current_role: str = "user") -> dict:
    """
    Get user response dựa vào role của current user.
    
    Args:
        user: User model instance
        decrypted_data: Dict with decrypted email/phone/password
        current_role: Role của current user (user/admin)
    
    Returns:
        dict: User response (admin xem full, user xem masked)
    
    Logic:
    - admin: Xem full dữ liệu (không mask)
    - user: Xem bị mask
    """
    # Admin xem full, user xem masked
    should_mask = (current_role != "admin")
    return get_user_response(user, decrypted_data, mask=should_mask)


def get_role_based_response_from_model(user: User, current_role: str = "user") -> dict:
    """
    Get user response từ User model (encrypted data).
    Dùng cho GET endpoints không decrypt.
    
    Vì data được encrypt, ta không thể decrypt để xem full.
    Admin cũng chỉ thấy masked pattern như user role (vì không có password để decrypt).
    
    Args:
        user: User model instance (có encrypted data)
        current_role: Role của current user (user/admin)
    
    Returns:
        dict: User response (all masked pattern)
    
    Note: 
    - Không thể decrypt nên both admin & user thấy masked pattern
    - Nếu admin muốn xem full, cần endpoint riêng /users/{id}/details
      với current admin user auth để decrypt
    """
    # Vì không có password để decrypt, ta trả về masked pattern cho all
    return {
        "id": user.id,
        "username": user.username,
        "email": "***@***",           # Cannot decrypt without password
        "phone": "****",              # Cannot decrypt without password
        "password": "***",            # Always masked
        "role": user.role.name if user.role else "user",
        "created_at": user.created_at.isoformat() if user.created_at else None,
        "updated_at": user.updated_at.isoformat() if user.updated_at else None
    }


    @staticmethod
    async def get_user_by_id(db: AsyncSession, user_id: int, mask: bool = True) -> dict:
        """
        Lấy user theo ID (không decrypt - return encrypted).
        
        Args:
            db: Database session
            user_id: User ID
            mask: Áp dụng masking hay không (không dùng, vì encrypted)
        
        Returns:
            User model instance
        
        Raises:
            ValueError: Nếu user không tồn tại
        
        Note: Không decrypt, chỉ return encrypted data
              Admin sẽ thấy full, user thấy masked
        """
        query = select(User).where(User.id == user_id).options(selectinload(User.role))
        result = await db.execute(query)
        db_user = result.scalar_one_or_none()
        
        if not db_user:
            raise ValueError(f"User with ID {user_id} does not exist")
        
        return db_user


    @staticmethod
    async def get_user_by_username(db: AsyncSession, username: str) -> User:
        """
        Lấy user theo username.
        
        Args:
            db: Database session
            username: Username
        
        Returns:
            User model instance hoặc None
        """
        query = select(User).where(User.username == username).options(selectinload(User.role))
        result = await db.execute(query)
        return result.scalar_one_or_none()


    @staticmethod
    async def get_users(db: AsyncSession, skip: int = 0, limit: int = 10, mask: bool = True) -> tuple:
        """
        Lấy danh sách users với pagination (không decrypt - return encrypted).
        
        Args:
            db: Database session
            skip: Số records bỏ qua
            limit: Số records trả về
            mask: Áp dụng masking hay không
        
        Returns:
            (total_count, users_list)
        
        Note: Không decrypt, chỉ return encrypted data
              Admin sẽ thấy full, user thấy masked
        """
        # Get total count
        count_query = select(User)
        count_result = await db.execute(count_query)
        total = len(count_result.all())
        
        # Get paginated users
        query = select(User).offset(skip).limit(limit).options(selectinload(User.role))
        result = await db.execute(query)
        users = result.scalars().all()
        
        return total, users


    @staticmethod
    async def update_user(db: AsyncSession, user_id: int, user_update: UserUpdate, username: str, old_password: str = None) -> User:
        """
        Cập nhật user với re-encryption.
        
        Args:
            db: Database session
            user_id: User ID
            user_update: UserUpdate schema
            username: Username (để sinh key)
            old_password: Old password (để decrypt dữ liệu cũ, required nếu update password)
        
        Returns:
            Updated User model instance
        
        Raises:
            ValueError: Nếu user không tồn tại hoặc password sai
        """
        query = select(User).where(User.id == user_id)
        result = await db.execute(query)
        db_user = result.scalar_one_or_none()
        
        if not db_user:
            raise ValueError(f"User with ID {user_id} does not exist")
        
        # Nếu update password, cần verify old_password
        if user_update.password:
            if not old_password:
                raise ValueError("old_password is required to update password")
            
            # Verify old password
            old_key = generate_key(username, old_password)
            try:
                decrypted_old_password = decrypt(db_user.password, old_key)
            except:
                raise ValueError("Invalid old password")
            
            if decrypted_old_password != old_password:
                raise ValueError("Invalid old password")
            
            # Update password với new key
            new_key = generate_key(username, user_update.password)
            db_user.password = encrypt(user_update.password, new_key)
            
            # Re-encrypt email & phone với new key
            if db_user.email:
                decrypted_email = decrypt(db_user.email, old_key)
                db_user.email = encrypt(decrypted_email, new_key)
            
            if db_user.phone:
                decrypted_phone = decrypt(db_user.phone, old_key)
                db_user.phone = encrypt(decrypted_phone, new_key)
        else:
            # Không update password, dùng current key để update email/phone
            current_key = generate_key(username, old_password) if old_password else None
            
            if user_update.email and current_key:
                db_user.email = encrypt(user_update.email, current_key)
            elif user_update.email:
                # Không có key để encrypt, raise error
                raise ValueError("Password is required to update email/phone")
            
            if user_update.phone and current_key:
                db_user.phone = encrypt(user_update.phone, current_key)
            elif user_update.phone:
                raise ValueError("Password is required to update email/phone")
        
        db_user.updated_at = datetime.utcnow()
        
        db.add(db_user)
        await db.commit()
        await db.refresh(db_user)
        
        return db_user


    @staticmethod
    async def delete_user(db: AsyncSession, user_id: int) -> User:
        """
        Xóa user.
        
        Args:
            db: Database session
            user_id: User ID
        
        Returns:
            Deleted User model instance
        
        Raises:
            ValueError: Nếu user không tồn tại
        """
        query = select(User).where(User.id == user_id)
        result = await db.execute(query)
        db_user = result.scalar_one_or_none()
        
        if not db_user:
            raise ValueError(f"User with ID {user_id} does not exist")
        
        await db.delete(db_user)
        await db.commit()
        
        return db_user


# ==================== Helper Functions ====================

def _decrypt_and_mask_user(user: User, username: str, password: str, mask: bool = True) -> dict:
    """
    Decrypt user data và áp dụng masking.
    
    Args:
        user: User model instance
        username: Username (để sinh key)
        password: Password plain text (để sinh key)
        mask: Áp dụng masking hay không
    
    Returns:
        dict: User data (decrypted, có hoặc không masked)
    """
    # Decrypt dữ liệu nhạy cảm
    decrypted_data = decrypt_user_data(user, username, password)
    
    # Merge với model data + apply masking
    user_response = get_user_response(user, decrypted_data, mask=mask)
    
    return user_response


def decrypt_user_data(user: User, username: str, password: str) -> dict:
    """
    Decrypt user data với username + password.
    
    Args:
        user: User model instance
        username: Username
        password: Password (plain text)
    
    Returns:
        dict: User data (decrypted)
    """
    master_key = get_master_key()
    per_user_key = generate_key(username, password)
    
    # Email/phone ưu tiên decrypt bằng master key (dữ liệu mới).
    # Nếu fail/ra chuỗi không hợp lệ, fallback per-user key để phục vụ migration.
    def _safe_decrypt(data: bytes, primary_key: bytes, fallback_key: bytes) -> str | None:
        if not data:
            return None
        try:
            return decrypt(data, primary_key)
        except Exception:
            try:
                return decrypt(data, fallback_key)
            except Exception:
                return None
    
    decrypted_email = _safe_decrypt(user.email, master_key, per_user_key)
    decrypted_phone = _safe_decrypt(user.phone, master_key, per_user_key)
    decrypted_password = decrypt(user.password, per_user_key) if user.password else None
    
    return {
        "email": decrypted_email,
        "phone": decrypted_phone,
        "password": decrypted_password
    }


async def migrate_user_to_master_key(db: AsyncSession, user: User, username: str, password: str) -> bool:
    """
    Re-encrypt email/phone bằng master key. Cần password để lấy per-user key
    nếu dữ liệu còn dạng cũ.
    Trả về True nếu có thay đổi.
    """
    master_key = get_master_key()
    per_user_key = generate_key(username, password)

    def looks_like_email(value: str | None) -> bool:
        return bool(value) and "@" in value

    def looks_like_phone(value: str | None) -> bool:
        if not value:
            return False
        digits = ''.join(c for c in value if c.isdigit() or c == '+')
        return len(digits) >= 4

    changed = False

    # Try decrypt with master key first
    try:
        email_master = decrypt(user.email, master_key) if user.email else None
        phone_master = decrypt(user.phone, master_key) if user.phone else None
    except Exception:
        email_master = None
        phone_master = None

    already_master = looks_like_email(email_master) or looks_like_phone(phone_master)
    if already_master:
        return False

    # Fallback decrypt with per-user key
    try:
        email_old = decrypt(user.email, per_user_key) if user.email else None
        phone_old = decrypt(user.phone, per_user_key) if user.phone else None
    except Exception:
        email_old = None
        phone_old = None

    if email_old:
        user.email = encrypt(email_old, master_key)
        changed = True
    if phone_old:
        user.phone = encrypt(phone_old, master_key)
        changed = True

    if changed:
        db.add(user)
        await db.commit()
        await db.refresh(user)

    return changed


def get_user_response(user: User, decrypted_data: dict = None, mask: bool = True) -> dict:
    """
    Get user response (merged model + decrypted data + masking).
    
    Args:
        user: User model instance
        decrypted_data: Dict with decrypted email/phone/password
        mask: Áp dụng masking hay không
    
    Returns:
        dict: User response
    """
    user_data = user.to_dict(decrypted_data)
    masked_data = apply_masking(user_data, mask=mask)
    return masked_data


def get_role_based_response(user: User, decrypted_data: dict = None, current_role: str = "user") -> dict:
    """
    Get user response dựa vào role của current user.
    
    Args:
        user: User model instance
        decrypted_data: Dict with decrypted email/phone/password
        current_role: Role của current user (user/admin)
    
    Returns:
        dict: User response (admin xem full, user xem masked)
    
    Logic:
    - admin: Xem full dữ liệu (không mask)
    - user: Xem bị mask
    """
    # Admin xem full, user xem masked
    should_mask = (current_role != "admin")
    return get_user_response(user, decrypted_data, mask=should_mask)


def get_role_based_response_from_model(user: User, current_role: str = "user") -> dict:
    """
    Get user response từ User model (encrypted data).
    Dùng cho GET endpoints không decrypt.
    
    Vì data được encrypt, ta không thể decrypt để xem full.
    Admin cũng chỉ thấy masked pattern như user role (vì không có password để decrypt).
    
    Args:
        user: User model instance (có encrypted data)
        current_role: Role của current user (user/admin)
    
    Returns:
        dict: User response (all masked pattern)
    
    Note: 
    - Không thể decrypt nên both admin & user thấy masked pattern
    - Nếu admin muốn xem full, cần endpoint riêng /users/{id}/details
      với current admin user auth để decrypt
    """
    # Vì không có password để decrypt, ta trả về masked pattern cho all
    return {
        "id": user.id,
        "username": user.username,
        "email": "***@***",           # Cannot decrypt without password
        "phone": "****",              # Cannot decrypt without password
        "password": "***",            # Always masked
        "role": user.role,
        "created_at": user.created_at.isoformat() if user.created_at else None,
        "updated_at": user.updated_at.isoformat() if user.updated_at else None
    }
