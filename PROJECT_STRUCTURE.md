# Project Structure & File Guide

Hướng dẫn chi tiết về cấu trúc dự án và mục đích của từng file.

---

## 📂 Complete Directory Structure

```
BackEnd/
│
├── 📄 Main Files
│   ├── main.py                      # FastAPI entry point - starts server
│   ├── requirements.txt             # Python package dependencies
│   ├── .env                         # Environment variables (MySQL credentials, etc)
│   └── setup.sql                    # MySQL database initialization script
│
├── 📁 app/                          # Main application package
│   ├── __init__.py                  # Package initialization
│   ├── crud.py                      # Database CRUD operations (Create, Read, Update, Delete)
│   ├── database.py                  # MySQL connection setup & session management
│   ├── models.py                    # SQLAlchemy ORM models (User table schema)
│   ├── schemas.py                   # Pydantic request/response validation models
│   ├── security.py                  # Encryption, decryption, data masking functions
│   │
│   └── 📁 routers/                  # API route handlers
│       ├── __init__.py              # Router package init
│       └── user.py                  # User management endpoints
│
├── 📁 docs/                         # Documentation files
│   ├── README.md                    # System overview
│   ├── DATABASE_SCHEMA.md           # User table schema details
│   ├── API_ENDPOINTS.md             # API endpoint documentation
│   ├── SECURITY.md                  # Encryption algorithms & details
│   └── DATA_MASKING.md              # Data masking rules
│
├── 🐳 Docker & Container Files
│   ├── Dockerfile                   # Docker image definition
│   └── docker-compose.yml           # Multi-container orchestration
│
├── 📚 Documentation & Guides
│   ├── README.md                    # Quick start guide (main file to read first)
│   ├── SETUP.md                     # Detailed setup instructions
│   ├── DEPLOYMENT.md                # Production deployment guide (3 options)
│   ├── DEVELOPMENT.md               # Developer guide for contributing
│   ├── TROUBLESHOOTING.md           # Common issues & solutions
│   └── PROJECT_STRUCTURE.md         # This file
│
├── 🧪 Testing & Utilities
│   ├── test_api.py                  # Interactive API test suite
│   ├── Makefile                     # Common commands (make setup, make run, etc)
│   └── .gitignore                   # Git ignore patterns
│
└── 🚀 Startup Scripts
    ├── run_windows.bat              # Windows automated startup script
    └── run_unix.sh                  # Unix/Mac automated startup script
```

---

## 📋 File Purposes & When to Use

### Core Application Files

#### `main.py` ⭐
**Purpose:** FastAPI application entry point
- Initializes FastAPI app
- Registers routers
- Sets up lifecycle hooks (startup/shutdown)
- Configures CORS middleware
- Runs development/production server

**When to edit:**
- Adding new routers
- Configuring new middleware
- Changing startup/shutdown logic
- Debugging server initialization issues

**Example:**
```python
app = FastAPI()
app.include_router(user_router)

@app.on_event("startup")
async def startup():
    await init_db()
```

---

#### `requirements.txt`
**Purpose:** Python package dependencies
- Lists all required packages
- Specifies exact versions for reproducibility
- Used by `pip install -r requirements.txt`

**When to edit:**
- Adding new Python libraries
- Upgrading packages
- Removing unused dependencies

**Common packages:**
- FastAPI: Web framework
- SQLAlchemy: ORM database layer
- aiomysql: Async MySQL driver
- Pydantic: Data validation
- Uvicorn: ASGI server

---

#### `.env`
**Purpose:** Environment configuration (sensitive data)
- Database credentials (user, password, host)
- Server host/port
- Environment mode (dev/prod)
- Should NOT be committed to git

**When to edit:**
- Deploying to different environment
- Changing database credentials
- Adjusting server port
- Toggling debug mode

**Example:**
```env
DATABASE_USER=root
DATABASE_PASSWORD=123456
DATABASE_HOST=localhost
DATABASE_PORT=3306
DATABASE_NAME=user_db
HOST=0.0.0.0
PORT=8000
ENV=development
```

---

#### `setup.sql`
**Purpose:** MySQL database initialization script
- Creates database `user_db`
- Creates `users` table with proper schema
- Creates indexes for performance
- Executed once during initial setup

**When to use:**
```bash
mysql -u root -p123456 < setup.sql
```

**When to edit:**
- Adding new columns to User table
- Creating additional tables
- Modifying table constraints

---

### Application Package (app/)

#### `app/models.py`
**Purpose:** SQLAlchemy ORM model definitions
- Defines `User` table schema
- Maps Python class to MySQL table
- Specifies column types & constraints

**Key components:**
```python
class User(Base):
    id: Primary Key
    username: Unique, indexed
    email: Encrypted (LargeBinary)
    phone: Encrypted (LargeBinary)
    password: Encrypted (LargeBinary)
    created_at, updated_at: Timestamps
```

**When to edit:**
- Adding new user fields
- Changing column types
- Adding/removing constraints

---

#### `app/schemas.py`
**Purpose:** Pydantic request/response models
- Validates incoming API requests
- Formats outgoing API responses
- Provides autocomplete in Swagger UI

**Key schemas:**
- `UserCreate`: POST request schema
- `UserUpdate`: PUT request schema
- `UserResponse`: Response with masked/encrypted data
- `UserListResponse`: Paginated list response

**When to edit:**
- Adding new request fields
- Changing validation rules
- Modifying response format

---

#### `app/security.py`
**Purpose:** Encryption, decryption, and data masking

**Key functions:**
```python
simple_hash()        # Generate encryption key from credentials
encrypt()           # XOR-based encryption
decrypt()           # XOR-based decryption
mask_email()        # Hide email (a***@domain.com)
mask_phone()        # Hide phone (xx****yy)
mask_password()     # Always returns ***
apply_masking()     # Apply masking based on mask parameter
```

**When to edit:**
- Changing encryption algorithm
- Modifying masking patterns
- Adding new data types to mask

---

#### `app/database.py`
**Purpose:** MySQL connection management
- Creates async engine with connection pooling
- Provides session factory for dependency injection
- Handles DB lifecycle (init, close)

**When to edit:**
- Changing MySQL connection parameters
- Adjusting connection pool settings
- Modifying DB initialization logic

---

#### `app/crud.py`
**Purpose:** Database CRUD operations
- Create user (with encryption)
- Read users (with masking/decryption)
- Update user (re-encrypt changed fields)
- Delete user

**Methods:**
```python
create_user()          # Insert new user
get_user_by_id()       # Retrieve user by ID
get_users()            # List all users (paginated)
update_user()          # Update user fields
delete_user()          # Delete user
```

**When to edit:**
- Adding new query methods
- Changing encryption flow
- Modifying update logic

---

#### `app/routers/user.py`
**Purpose:** FastAPI endpoints for user management

**Endpoints:**
- `POST /api/users` - Create user
- `GET /api/users` - List users
- `GET /api/users/{id}` - Get user by ID
- `PUT /api/users/{id}` - Update user
- `DELETE /api/users/{id}` - Delete user

**When to edit:**
- Adding new endpoints
- Changing route paths
- Modifying endpoint behavior
- Adding request validation

---

### Docker Files

#### `Dockerfile`
**Purpose:** Build Docker image for backend

**When to use:**
```bash
docker build -t csat-backend:latest .
```

**When to edit:**
- Changing Python version (FROM python:X.X)
- Installing system dependencies
- Changing startup command

---

#### `docker-compose.yml`
**Purpose:** Orchestrate multiple containers (MySQL + Backend)

**Services:**
- MySQL: Database container
- Backend: FastAPI application container

**When to use:**
```bash
docker-compose up -d      # Start all services
docker-compose down       # Stop all services
docker-compose logs -f    # View logs
```

**When to edit:**
- Adding new services
- Changing port mappings
- Modifying environment variables
- Changing healthcheck settings

---

### Documentation Files

#### `README.md` ⭐⭐⭐
**Purpose:** Main quick-start guide - **START HERE**
- Overview of project
- Installation steps
- How to run server
- Basic API examples
- Troubleshooting links

**When to read:** First thing when setting up project

---

#### `SETUP.md`
**Purpose:** Detailed setup instructions
- Prerequisites check
- Step-by-step MySQL setup
- Virtual environment creation
- Dependency installation
- Database verification
- Common setup issues

**When to read:** If quick start doesn't work

---

#### `DEPLOYMENT.md`
**Purpose:** Production deployment guide
- Local development setup
- Docker Compose deployment
- Linux server deployment (with Nginx, Supervisor)
- AWS/Cloud deployment
- Kubernetes deployment
- Performance optimization

**When to read:** Before deploying to production

---

#### `DEVELOPMENT.md`
**Purpose:** Developer guide
- Code structure explanation
- Request flow diagram
- Development workflow
- Adding new features
- Testing guide
- Git workflow
- Debugging tips

**When to read:** Before contributing code changes

---

#### `TROUBLESHOOTING.md`
**Purpose:** Common issues & solutions
- MySQL connection issues
- Python environment issues
- FastAPI server issues
- API request errors
- Docker issues
- Performance issues
- Diagnostic checklist

**When to read:** When something breaks

---

#### `docs/` folder
**Purpose:** Architecture & design documentation
- **DATABASE_SCHEMA.md**: User table structure
- **API_ENDPOINTS.md**: Expected API behavior
- **SECURITY.md**: Encryption algorithm details
- **DATA_MASKING.md**: Masking rules

**When to read:** Understanding system design

---

### Utility Files

#### `test_api.py`
**Purpose:** Interactive API testing suite
- Test basic CRUD operations
- Test error handling
- Test data masking

**When to use:**
```bash
python test_api.py
```

**When to edit:**
- Adding new test cases
- Testing new endpoints
- Changing test data

---

#### `Makefile`
**Purpose:** Common command shortcuts

**Available commands:**
```bash
make setup          # Create venv + install deps
make install        # Install dependencies only
make run            # Run development server
make test           # Run API tests
make clean          # Clean cache/temp files
make db-setup       # Initialize database
make docker-up      # Start Docker services
make docker-down    # Stop Docker services
make lint           # Run linting
make format         # Format code with black
```

**When to use:** Quick access to common tasks

---

#### `.gitignore`
**Purpose:** Prevent committing unwanted files
- Virtual environments
- Environment variables
- Python cache
- IDE settings
- Log files

**When to edit:**
- Adding new files to ignore
- Removing accidentally tracked files

---

### Startup Scripts

#### `run_windows.bat`
**Purpose:** Automated setup & run for Windows
- Set environment variables
- Create venv if needed
- Install packages
- Initialize database
- Start server

**When to use:**
```commandline
run_windows.bat
```

**When to edit:**
- Changing startup process
- Modifying initial setup

---

#### `run_unix.sh`
**Purpose:** Automated setup & run for Mac/Linux
- Same as Windows version but for Unix systems
- Uses bash instead of batch

**When to use:**
```bash
bash run_unix.sh
```

---

## 🔄 File Dependencies

```
main.py
├── app/routers/user.py
│   ├── app/crud.py
│   │   ├── app/models.py
│   │   ├── app/database.py
│   │   └── app/security.py
│   ├── app/schemas.py
│   └── app/database.py
│
├── app/database.py
│   ├── app/models.py
│   └── .env
│
└── .env (configuration)
```

---

## 📍 Which File to Edit For Common Tasks

| Task | File(s) |
|------|---------|
| Add new user field | `models.py`, `schemas.py`, `crud.py`, `security.py`, `setup.sql` |
| Add new endpoint | `routers/user.py`, `crud.py` |
| Change encryption method | `security.py`, `models.py` |
| Add new middleware | `main.py` |
| Change database host | `.env` |
| Modify masking pattern | `security.py` |
| Add testing | `test_api.py` |
| Change startup behavior | `main.py`, `database.py` |
| Package for production | `Dockerfile`, `docker-compose.yml` |
| Deploy to server | `DEPLOYMENT.md` instructions |

---

## 🎯 Reading Order for Different Roles

### For End Users
1. `README.md` - Understand what the system does
2. `SETUP.md` - Follow setup steps
3. Swagger UI at `http://localhost:8000/docs` - Test API
4. `TROUBLESHOOTING.md` - If issues arise

### For Developers Contributing Code
1. `README.md` - Quick overview
2. `DEVELOPMENT.md` - Code structure & workflow
3. Specific files in `app/` as needed
4. `test_api.py` - See how to test changes

### For DevOps/SysAdmin Deploying
1. `DEPLOYMENT.md` - Choose deployment method
2. `SETUP.md` - Initial database setup
3. Docker files & scripts - For containerization
4. `TROUBLESHOOTING.md` - Common deployment issues

### For Security Audit
1. `docs/SECURITY.md` - Encryption details
2. `app/security.py` - Review implementation
3. `docs/DATA_MASKING.md` - Masking rules
4. `.env` - Check credential storage

---

## 📊 Quick Statistics

| Metric | Value |
|--------|-------|
| Python files | 8 |
| Documentation files | 10 |
| Configuration files | 4 |
| Docker files | 2 |
| Test/Utility files | 3 |
| Total files | 27+ |
| Total lines of code | ~2,000+ |
| Total documentation | ~5,000+ lines |

---

## ✅ Checklist Before First Run

- [ ] Read `README.md`
- [ ] MySQL is running (`mysql -u root -p123456`)
- [ ] `.env` has correct credentials
- [ ] Run `setup.sql`
- [ ] Create virtual environment
- [ ] Install `requirements.txt`
- [ ] Run `python main.py`
- [ ] Access `http://localhost:8000/docs`
- [ ] Test API with `/health` endpoint
- [ ] Run `test_api.py`

---

**🎉 Ready to start? Begin with README.md!**
