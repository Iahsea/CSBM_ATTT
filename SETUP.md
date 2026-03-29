# 🚀 Backend Project Setup Guide

## 📁 Project Structure

```
BackEnd/
├── app/
│   ├── __init__.py
│   ├── database.py           # MySQL connection & configuration
│   ├── models.py             # SQLAlchemy User model
│   ├── schemas.py            # Pydantic request/response schemas
│   ├── security.py           # Encryption & masking functions
│   ├── crud.py               # CRUD operations
│   └── routers/
│       ├── __init__.py
│       └── user.py           # User API endpoints
│
├── main.py                   # FastAPI entry point
├── requirements.txt          # Python dependencies
├── .env                      # Environment variables
├── setup.sql                 # MySQL database setup script
├── README.md                 # This file
└── docs/
    ├── README.md
    ├── DATABASE_SCHEMA.md
    ├── API_ENDPOINTS.md
    ├── SECURITY.md
    └── DATA_MASKING.md
```

---

## 🛠️ Setup Instructions

### 1. Prerequisites

- Python 3.9+
- MySQL 5.7+ (hoặc MariaDB)
- pip (Python package manager)

### 2. Install Dependencies

```bash
# Navigate to project directory
cd d:\Document\CSAT_BMPT\BackEnd

# Create virtual environment (optional but recommended)
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install packages
pip install -r requirements.txt
```

### 3. Setup MySQL Database

**Option A: Using MySQL CLI**

```bash
# Login to MySQL
mysql -u root -p

# Enter password: 123456

# Run setup script
source setup.sql

# Verify database created
USE user_db;
SHOW TABLES;
```

**Option B: Using MySQL Workbench**

1. Open MySQL Workbench
2. Create new connection with:
   - Username: `root`
   - Password: `123456`
   - Host: `localhost`
   - Port: `3306`
3. Open `setup.sql` file
4. Execute script (Ctrl+Enter)

### 4. Configure Environment Variables

File `.env` đã được tạo sẵn với thông tin MySQL:

```env
DATABASE_USER=root
DATABASE_PASSWORD=123456
DATABASE_HOST=localhost
DATABASE_PORT=3306
DATABASE_NAME=user_db
```

Thay đổi if needed.

### 5. Run Server

```bash
# Development (with auto-reload)
python main.py

# Or using uvicorn directly
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Output:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Application startup complete
```

---

## 📚 API Documentation

### Access API Docs

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

### Main Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/users` | Tạo user mới |
| GET | `/api/users` | Lấy danh sách users |
| GET | `/api/users/{id}` | Lấy user theo ID |
| PUT | `/api/users/{id}` | Cập nhật user |
| DELETE | `/api/users/{id}` | Xóa user |

### Example: Create User

```bash
curl -X POST http://localhost:8000/api/users \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_doe",
    "email": "john@gmail.com",
    "phone": "0987654321",
    "password": "SecurePass123"
  }'
```

**Response:**
```json
{
  "id": 1,
  "username": "john_doe",
  "email": "j***@gmail.com",
  "phone": "09****21",
  "password": "***",
  "message": "User created successfully",
  "created_at": "2026-03-28T10:30:45"
}
```

---

## 🔐 Security Features

### Encryption

- **Algorithm**: XOR Encryption (Custom)
- **Key Generation**: simple_hash(username + password)
- **Encrypted Fields**: email, phone, password
- **Storage**: LargeBinary (VARBINARY) in MySQL

### Data Masking

- **Email**: `a***@domain.com`
- **Phone**: `09****21` (keep first 2 & last 2 digits)
- **Password**: `***` (completely hidden)

### Query Parameter

```
?mask=true   # Apply masking (default)
?mask=false  # Return plain data (require auth)
```

---

## 🧪 Testing

### Run Tests

```bash
# Install test dependencies
pip install pytest pytest-asyncio

# Run tests
pytest

# Run with coverage
pytest --cov=app

# Run specific test
pytest tests/test_security.py -v
```

### Manual Testing

```bash
# Get all users (with masking)
curl http://localhost:8000/api/users?mask=true

# Get user by ID (no masking - careful!)
curl "http://localhost:8000/api/users/1?mask=false"
```

---

## 📝 Database Schema

### Users Table

| Column | Type | Notes |
|--------|------|-------|
| id | INT PK | Auto-increment |
| username | VARCHAR(50) UNIQUE | Not encrypted (for key generation) |
| email | VARBINARY(255) | XOR Encrypted |
| phone | VARBINARY(255) | XOR Encrypted |
| password | VARBINARY(255) | XOR Encrypted |
| created_at | DATETIME | Auto-timestamp |
| updated_at | DATETIME | Auto-update |

---

## 🔍 Monitor Logs

```bash
# Server logs (watch in real-time)
# Ctrl+C to stop
tail -f server.log

# Database logs (if MySQL logging enabled)
# Windows
C:\ProgramData\MySQL\MySQL Server 8.0\Data\
```

---

## 📖 API Documentation Files

See detailed documentation:

- [DATABASE_SCHEMA.md](./docs/DATABASE_SCHEMA.md) - DB schema details
- [API_ENDPOINTS.md](./docs/API_ENDPOINTS.md) - Complete API reference
- [SECURITY.md](./docs/SECURITY.md) - Encryption algorithms
- [DATA_MASKING.md](./docs/DATA_MASKING.md) - Masking rules

---

## ⚠️ Common Issues & Solutions

### Issue: "Connection refused"
```
Error: Failed to connect to MySQL at localhost:3306
```
**Solution:**
- Make sure MySQL is running
- Check DATABASE_HOST, DATABASE_PORT in .env
- Verify MySQL credentials

### Issue: "Database doesn't exist"
```
Error: (pymysql.err.ProgrammingError) (1049, "Unknown database 'user_db'")
```
**Solution:**
- Run setup.sql to create database
- Check DATABASE_NAME in .env

### Issue: "Port already in use"
```
Error: Address already in use
```
**Solution:**
- Change PORT in .env (e.g., 8001)
- Or kill process: `lsof -ti:8000 | xargs kill -9`

---

## 🚀 Next Steps

1. **Implement Authentication** - Add JWT token auth
2. **Add Logging** - Implement audit logs
3. **Load Testing** - Test performance with ab/wrk
4. **Docker** - Containerize the application
5. **CI/CD** - Setup GitHub Actions

---

## 📞 Support

- Check [docs/](./docs/) folder for detailed documentation
- Review sample queries in setup.sql
- Check FastAPI docs at http://localhost:8000/docs

---

**Version**: 1.0  
**Last Updated**: 28/03/2026  
**Status**: Ready for Development
