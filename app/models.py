"""
SQLAlchemy ORM Models
Định nghĩa User & Role models với relationships
"""
from sqlalchemy import Column, Integer, String, LargeBinary, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base


class Role(Base):
    """
    Role Model - Lưu trữ các role hệ thống.
    
    Attributes:
        id: Primary key (auto-increment)
        name: Tên role (admin, user)
        description: Mô tả role
        created_at: Timestamp tạo
    """
    
    __tablename__ = "roles"

    # Primary Key
    id = Column(
        Integer,
        primary_key=True,
        index=True,
        comment="Role ID (auto-increment)"
    )

    # Role Name
    name = Column(
        String(20),
        unique=True,
        nullable=False,
        index=True,
        comment="Role name (admin, user)"
    )

    # Description
    description = Column(
        String(255),
        nullable=True,
        comment="Role description"
    )

    # Timestamps
    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
        comment="Role creation timestamp"
    )

    # Relationships
    users = relationship("User", back_populates="role")

    def __repr__(self):
        return f"<Role(id={self.id}, name='{self.name}')>"


class User(Base):
    """
    User Model - Lưu trữ thông tin user với encrypted fields.
    
    Attributes:
        id: Primary key (auto-increment)
        username: Tên đăng nhập (NOT encrypted, dùng để sinh key)
        email: Email (encrypted - LargeBinary)
        phone: Số điện thoại (encrypted - LargeBinary)
        password: Mật khẩu (encrypted - LargeBinary)
        role_id: Foreign key tới roles table
        created_at: Timestamp tạo tài khoản
        updated_at: Timestamp cập nhật lần cuối
    """
    
    __tablename__ = "users"

    # Primary Key
    id = Column(
        Integer,
        primary_key=True,
        index=True,
        comment="User ID (auto-increment)"
    )

    # Username (NOT encrypted - needed to generate key)
    username = Column(
        String(50),
        unique=True,
        nullable=False,
        index=True,
        comment="Username (unique, not encrypted)"
    )

    # Email (Encrypted)
    email = Column(
        LargeBinary,
        nullable=False,
        comment="Email (encrypted)"
    )

    # Phone (Encrypted)
    phone = Column(
        LargeBinary,
        nullable=False,
        comment="Phone number (encrypted)"
    )

    # Password (Encrypted)
    password = Column(
        LargeBinary,
        nullable=False,
        comment="Password (encrypted)"
    )

    # Role (foreign key)
    role_id = Column(
        Integer,
        ForeignKey("roles.id"),
        default=2,  # Default to "user" role (id=2)
        nullable=False,
        comment="Role ID (foreign key, default=user)"
    )

    # Timestamps
    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=True,
        comment="Account creation timestamp"
    )

    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=True,
        comment="Last update timestamp"
    )

    # Relationships
    role = relationship("Role", back_populates="users")

    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}')>"

    def to_dict(self, decrypted_data: dict = None):
        """
        Convert User model to dictionary.
        
        Args:
            decrypted_data: Optional dict with decrypted email/phone/password
        
        Returns:
            dict
        """
        result = {
            "id": self.id,
            "username": self.username,
            "role": self.role.name if self.role else "user",  # Return role name
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
        
        # Add decrypted data if provided
        if decrypted_data:
            result.update(decrypted_data)
        else:
            # If no decrypted data, add masked placeholders
            result["email"] = "***@***"
            result["phone"] = "****"
            result["password"] = "***"
        
        return result
