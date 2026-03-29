# Development Guide

Hướng dẫn phát triển cho nhà phát triển muốn contribute hoặc mở rộng project.

---

## 📚 Code Structure

### Folder Organization
```
BackEnd/
├── app/                      # Main application package
│   ├── __init__.py           # Package initialization
│   ├── crud.py               # Database CRUD operations
│   ├── database.py           # MySQL connection & session management
│   ├── models.py             # SQLAlchemy ORM models
│   ├── schemas.py            # Pydantic request/response models
│   ├── security.py           # Encryption, decryption, masking logic
│   └── routers/
│       ├── __init__.py       # Router package init
│       └── user.py           # User endpoints (/api/users/*)
├── main.py                   # FastAPI app entry point
├── requirements.txt          # Python dependencies
├── .env                      # Environment variables (local)
├── setup.sql                 # Database initialization script
└── docs/                     # Documentation
```

---

## 🔄 Request Flow

```
Client Request
    ↓
Nginx/Proxy (Production)
    ↓
FastAPI (main.py)
    ↓
Router (app/routers/user.py)
    ↓
Schema Validation (app/schemas.py)
    ↓
CRUD Operation (app/crud.py)
    ↓
Security Operations (app/security.py)
  - Encryption/Decryption
  - Masking
    ↓
Database (app/database.py)
    ↓
MySQL
    ↓
            [Response back through same path]
```

---

## 🛠️ Development Workflow

### 1. Setup Development Environment

```bash
# Clone/navigate to project
cd BackEnd

# Create virtual environment
python -m venv venv

# Activate
source venv/bin/activate  # Mac/Linux
# or
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Setup database
mysql -u root -p123456 < setup.sql

# Run server
python main.py
```

### 2. Development Best Practices

#### Code Style
```bash
# Format code
black app/ main.py --line-length=120

# Check linting
flake8 app/ main.py --max-line-length=120
```

#### Type Hints
```python
# Good: Include type hints
async def create_user(user: UserCreate, db: AsyncSession) -> UserResponse:
    pass

# Bad: No type hints
async def create_user(user, db):
    pass
```

#### Error Handling
```python
# Good: Specific exceptions
try:
    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
except SQLAlchemyError as e:
    logger.error(f"Database error: {e}")
    raise HTTPException(status_code=500, detail="Database error")

# Bad: Generic exceptions
try:
    user = await db.get(User, user_id)
except:
    pass
```

#### Documentation
```python
# Good: Clear docstrings
async def encrypt(data: str, key: int) -> bytes:
    """
    Encrypt string data using XOR algorithm.
    
    Args:
        data: Plain text to encrypt
        key: Encryption key (0-255)
        
    Returns:
        Encrypted bytes
        
    Raises:
        ValueError: If key is not 0-255
    """
    if not 0 <= key <= 255:
        raise ValueError("Key must be between 0-255")
    return bytes(ord(c) ^ key for c in data)

# Bad: No documentation
async def encrypt(data: str, key: int) -> bytes:
    return bytes(ord(c) ^ key for c in data)
```

---

## 📦 Adding New Features

### Example: Add Admin User Management

#### Step 1: Update Database Schema (models.py)

```python
from enum import Enum

class UserRole(str, Enum):
    ADMIN = "admin"
    USER = "user"

class User(Base):
    __tablename__ = "users"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    email: Mapped[bytes]
    phone: Mapped[bytes]
    password: Mapped[bytes]
    role: Mapped[UserRole] = mapped_column(
        String(20), default=UserRole.USER
    )  # NEW
    is_active: Mapped[bool] = mapped_column(default=True)  # NEW
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime]
```

#### Step 2: Update Pydantic Schemas (schemas.py)

```python
class UserCreate(BaseModel):
    username: str
    email: EmailStr
    phone: str
    password: str

class UserResponse(BaseModel):
    id: int
    username: str
    email: Optional[str]
    phone: Optional[str]
    role: str  # NEW
    is_active: bool  # NEW
    created_at: datetime
    
    class Config:
        from_attributes = True
```

#### Step 3: Add CRUD Operations (crud.py)

```python
class UserCRUD:
    @staticmethod
    async def get_by_role(
        db: AsyncSession,
        role: str,
        skip: int = 0,
        limit: int = 10
    ) -> List[User]:
        """Get all users by role (admin, user, etc)"""
        query = select(User).where(User.role == role)
        query = query.offset(skip).limit(limit)
        result = await db.execute(query)
        return result.scalars().all()
```

#### Step 4: Add Endpoints (routers/user.py)

```python
@router.get("/api/users/admin/list")
async def get_admin_users(
    skip: int = Query(0),
    limit: int = Query(10),
    db: AsyncSession = Depends(get_db)
):
    """Get all admin users (requires auth in future)"""
    admins = await UserCRUD.get_by_role(db, "admin", skip, limit)
    return UserListResponse(
        total=len(admins),
        skip=skip,
        limit=limit,
        items=admins
    )
```

#### Step 5: Run Migration

```bash
# Update database
mysql -u root -p123456 << EOF
ALTER TABLE users ADD COLUMN role VARCHAR(20) DEFAULT 'user';
ALTER TABLE users ADD COLUMN is_active BOOLEAN DEFAULT TRUE;
EOF

# Test
python -c "from app.models import User; print('✅ Migration successful')"
```

---

## 🧪 Testing

### Unit Tests

```python
# tests/test_security.py
import pytest
from app.security import encrypt, decrypt, simple_hash, mask_email

def test_encrypt_decrypt():
    """Test encryption/decryption reversibility"""
    data = "test_password"
    key = simple_hash("test_user" + "test_password")
    encrypted = encrypt(data, key)
    decrypted = decrypt(encrypted, key)
    assert decrypted == data

def test_mask_email():
    """Test email masking"""
    result = mask_email("user@example.com")
    assert result == "u***@example.com"
    assert "@" in result
```

### Integration Tests

```python
# tests/test_endpoints.py
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_create_user():
    """Test user creation endpoint"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post("/api/users", json={
            "username": "testuser",
            "email": "test@example.com",
            "phone": "0987654321",
            "password": "TestPass123"
        })
        assert response.status_code == 201
        assert response.json()["username"] == "testuser"
```

### Run Tests

```bash
# Install pytest
pip install pytest pytest-asyncio

# Run all tests
pytest

# Run specific test
pytest tests/test_security.py::test_encrypt_decrypt -v

# Run with coverage
pytest --cov=app --cov-report=html
```

---

## 🐛 Debugging

### Enable Debug Logging

```python
# In main.py
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

@app.get("/debug")
async def get_debug_info():
    """Debug endpoint (remove in production)"""
    return {
        "message": "Debug info",
        "env": os.getenv("ENV"),
        "database_url": os.getenv("DATABASE_URL")
    }
```

### Debug with FastAPI

```bash
# Run with reload and verbose logging
PYTHONUNBUFFERED=1 python main.py
```

### Database Debugging

```python
# In app/database.py
engine = create_async_engine(
    DATABASE_URL,
    echo=True,  # Print all SQL statements
    echo_pool=True,  # Print connection pool events
)
```

---

## 📋 Common Tasks

### Add New Endpoint

1. Create schema in `schemas.py` (if needed)
2. Add CRUD method in `crud.py`
3. Add route in `routers/user.py`
4. Test with `test_api.py`

### Add New Database Field

1. Update `User` model in `models.py`
2. Update schemas in `schemas.py`
3. Update `encrypt/decrypt` logic if needed in `security.py`
4. Run migration SQL
5. Update tests

### Add New Router

1. Create `app/routers/feature.py`
2. Import in `main.py`: `from app.routers import feature`
3. Include in app: `app.include_router(feature.router)`

---

## 🔑 Environment Variables

```bash
# Development
ENV=development
RELOAD=true
DEBUG=true

# Production
ENV=production
RELOAD=false
DEBUG=false

# Database
DATABASE_HOST=localhost
DATABASE_PORT=3306
DATABASE_USER=root
DATABASE_PASSWORD=123456
DATABASE_NAME=user_db

# Server
HOST=0.0.0.0
PORT=8000
```

---

## 📝 Git Workflow

```bash
# Create feature branch
git checkout -b feature/add-user-roles

# Make changes
git add .

# Commit with clear message
git commit -m "feat: add user role management"

# Push to remote
git push origin feature/add-user-roles

# Create Pull Request and get reviewed
```

### Commit Message Format
```
feat: add user roles management
^--^  ^---------------------^
|     |
|     +-> Summary (lowercase, imperative)
|
+-> Type: feat, fix, docs, style, refactor, test, chore
```

---

## 🚀 Performance Tips

1. **Use async/await** - Don't block the event loop
2. **Connection pooling** - Already configured in database.py
3. **Batch operations** - For multiple inserts: `db.execute(insert(User).values(...))`
4. **Caching** - Use Redis for frequent queries
5. **Pagination** - Always paginate large datasets
6. **Indexes** - Add indexes on frequently searched fields

---

## ✅ Pre-Commit Checklist

Before committing:
- [ ] Code formatted with `black`
- [ ] Linting passes with `flake8`
- [ ] Tests pass with `pytest`
- [ ] Type hints added (optional but recommended)
- [ ] Documentation updated
- [ ] No hardcoded credentials
- [ ] No TODO comments left behind

---

## 📞 Support

- Check existing docs in `/docs` folder
- Check SETUP.md for common issues
- Review test files in `tests/`

---

**Happy coding! 🎉**
