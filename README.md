# Backend - User Management API

**Hệ thống quản lý người dùng với mã hóa dữ liệu** | **User Management System with Data Encryption**

---

## 📋 Tổng Quan

Backend phục vụ các API cho quản lý người dùng với tính năng:
- ✅ Mã hóa/giải mã dữ liệu XOR
- ✅ Che che dữ liệu (email, điện thoại, mật khẩu)
- ✅ Quản lý người dùng (CRUD)
- ✅ MySQL database
- ✅ FastAPI async framework
- ✅ Swagger documentation

---

## 🚀 Cách Cài Đặt

### 1️⃣ Yêu Cầu
- **Python 3.9+**
- **MySQL 5.7+** (running on localhost:3306)
- **MySQL Credentials**: root / 123456

### 2️⃣ Database Setup

**Trên Windows:**
```bash
mysql -u root -p123456 < setup.sql
```

**Trên Mac/Linux:**
```bash
mysql -u root -p123456 < setup.sql
```

**Hoặc setup thủ công:**
```sql
CREATE DATABASE user_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE user_db;
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(255) UNIQUE NOT NULL,
    email LONGBLOB NOT NULL,
    phone LONGBLOB NOT NULL,
    password LONGBLOB NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_username (username)
) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### 3️⃣ Cài Đặt Python Packages

**T
ạo Virtual Environment:**
```bash
python -m venv venv
```

**Activate Environment:**
- **Windows:** `venv\Scripts\activate`
- **Mac/Linux:** `source venv/bin/activate`

**Cài Đặt Dependencies:**
```bash
pip install -r requirements.txt
```

**Kiểm Tra Cài Đặt:**
```bash
pip list
```

---

## ▶️ Chạy Server

### Cách 1: Command Line
```bash
python main.py
```

### Cách 2: Automation Script
**Windows:**
```bash
run_windows.bat
```

**Mac/Linux:**
```bash
bash run_unix.sh
```

### Cách 3: Uvicorn Direct
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

---

## 🌐 API Documentation

**Server chạy tại:** `http://localhost:8000`

### 📚 Swagger Documentation
- **Interactive Docs:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

### 🏥 Health Check
```bash
curl http://localhost:8000/health
```

---

## 🧪 Testing

### Chạy Test Suite
```bash
python test_api.py
```

### Test Individual Endpoints

**1. Tạo người dùng:**
```bash
curl -X POST "http://localhost:8000/api/users" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_doe",
    "email": "john@example.com",
    "phone": "0987654321",
    "password": "SecurePass123"
  }'
```

**2. Lấy danh sách người dùng (có che che dữ liệu):**
```bash
curl "http://localhost:8000/api/users?mask=true&limit=10"
```

**3. Lấy người dùng theo ID:**
```bash
curl "http://localhost:8000/api/users/1?mask=true"
```

**4. Cập nhật người dùng:**
```bash
curl -X PUT "http://localhost:8000/api/users/1" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "new_email@example.com",
    "phone": "0912345678"
  }'
```

**5. Xóa người dùng:**
```bash
curl -X DELETE "http://localhost:8000/api/users/1"
```

---

## 📁 Cấu Trúc Folder

```
BackEnd/
├── app/
│   ├── __init__.py              # App package
│   ├── crud.py                  # CRUD operations
│   ├── database.py              # MySQL connection
│   ├── models.py                # SQLAlchemy models
│   ├── schemas.py               # Pydantic schemas
│   ├── security.py              # Encryption/Masking logic
│   └── routers/
│       ├── __init__.py
│       └── user.py              # User endpoints
├── main.py                      # FastAPI app entry point
├── requirements.txt             # Python dependencies
├── .env                         # Environment variables
├── setup.sql                    # Database setup script
├── test_api.py                  # API test suite
├── SETUP.md                     # Detailed setup guide
├── run_windows.bat              # Windows startup script
├── run_unix.sh                  # Unix startup script
└── docs/
    ├── README.md
    ├── DATABASE_SCHEMA.md
    ├── API_ENDPOINTS.md
    ├── SECURITY.md
    └── DATA_MASKING.md
```

---

## ⚙️ Cấu Hình

### Environment Variables (`.env`)
```env
# Database
DATABASE_USER=root
DATABASE_PASSWORD=123456
DATABASE_HOST=localhost
DATABASE_PORT=3306
DATABASE_NAME=user_db

# Server
HOST=0.0.0.0
PORT=8000
RELOAD=true
ENV=development
```

### Thay Đổi Cấu Hình
1. Mở file `.env`
2. Chỉnh sửa các giá trị
3. Khởi động lại server

---

## 🔒 Bảo Mật

### Mã Hóa XOR
- **Key Generation:** `simple_hash(username + password)`
- **Algorithm:** XOR bit-by-bit với key
- **Storage:** LONGBLOB trong MySQL

### Che Che Dữ Liệu (Masking)
- **Email:** `a***@domain.com`
- **Phone:** `xx****yy` (hiển thị 2 chữ số đầu + 2 chữ số cuối)
- **Password:** `***` (luôn được che)

### Query Parameters
```bash
?mask=true   # Che che dữ liệu nhạy cảm (mặc định)
?mask=false  # Hiển thị dữ liệu plaintext (cần caution)
```

---

## 🐛 Troubleshooting

### Lỗi: "Can't connect to MySQL server"
- ✅ Kiểm tra MySQL đang chạy: `mysql -u root -p123456`
- ✅ Kiểm tra credentials trong `.env`
- ✅ Kiểm tra port 3306 không bị firewall chặn

### Lỗi: "ModuleNotFoundError"
- ✅ Chạy: `pip install -r requirements.txt`
- ✅ Kiểm tra virtual environment được active

### Lỗi: "Database user_db does not exist"
- ✅ Chạy setup.sql: `mysql -u root -p123456 < setup.sql`
- ✅ Kiểm tra MySQL user có quyền CREATE DATABASE

### Server không khởi động
- ✅ Kiểm tra port 8000 không được sử dụng: `netstat -an | grep 8000`
- ✅ Kiểm tra Python path: `which python` hoặc `where python`
- ✅ Kiểm tra logs trong terminal

---

## 📞 API Reference

| Method | Endpoint | Mô Tả | Auth |
|--------|----------|-------|------|
| GET | / | Root info | ❌ |
| GET | /health | Health check | ❌ |
| POST | /api/users | Tạo người dùng | ❌ |
| GET | /api/users | Danh sách người dùng | ❌ |
| GET | /api/users/{id} | Lấy người dùng | ❌ |
| PUT | /api/users/{id} | Cập nhật người dùng | ❌ |
| DELETE | /api/users/{id} | Xóa người dùng | ❌ |

---

## 📚 Tài Liệu Chi Tiết

Xem folder `docs/`:
- [Database Schema](docs/DATABASE_SCHEMA.md)
- [API Endpoints](docs/API_ENDPOINTS.md)
- [Security Details](docs/SECURITY.md)
- [Data Masking Rules](docs/DATA_MASKING.md)

---

## 🎯 Tính Năng Sắp Tới

- [ ] JWT Authentication
- [ ] Rate Limiting
- [ ] Audit Logging
- [ ] Docker Support
- [ ] Unit Tests
- [ ] CI/CD Pipeline

---

**✅ Backend ready! Hãy bắt đầu với `/health` check:**
```bash
curl http://localhost:8000/health
```
