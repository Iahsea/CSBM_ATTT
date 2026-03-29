# Quick Start - Bắt Đầu Nhanh (5 Phút)

**Chỉ 5 bước để chạy backend API 🚀**

---

## ⚡ Yêu Cầu Tối Thiểu
- Python 3.9+
- MySQL 5.7+ (localhost:3306)
- MySQL Credentials: `root` / `123456`

---

## 🚀 Setup & Run (Chọn 1 trong 3 cách)

### Cách 1️⃣: Automatic Script (Dễ Nhất)

**Windows:**
```bash
run_windows.bat
```

**Mac/Linux:**
```bash
bash run_unix.sh
```

✅ Done! Server sẽ chạy tại http://localhost:8000

---

### Cách 2️⃣: Makefile Commands

```bash
# Setup
make setup      # Create venv + install everything

# Run
make run        # Start server

# Or all-in-one
make setup && make run
```

✅ Access: http://localhost:8000/docs

---

### Cách 3️⃣: Manual Step-by-Step

**Step 1: Create Virtual Environment**
```bash
python -m venv venv
```

**Step 2: Activate It**
```bash
# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate
```

**Step 3: Install Packages**
```bash
pip install -r requirements.txt
```

**Step 4: Setup Database**
```bash
mysql -u root -p123456 < setup.sql
```

**Step 5: Run Server**
```bash
python main.py
```

---

## 🌐 Access Your API

**Swagger UI:** http://localhost:8000/docs

**Health Check:**
```bash
curl http://localhost:8000/health
```

---

## 🧪 Quick Test

```bash
# Create a user
curl -X POST "http://localhost:8000/api/users" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser123",
    "email": "test@example.com",
    "phone": "0987654321",
    "password": "TestPass123"
  }'

# Get all users
curl "http://localhost:8000/api/users?mask=true"

# Or use interactive test
python test_api.py
```

---

## 🐳 Alternative: Docker (Includes MySQL)

```bash
# One command to start MySQL + Backend
docker-compose up -d

# Check it's running
docker-compose ps

# View logs
docker-compose logs -f

# Or access Swagger UI
# http://localhost:8000/docs
```

---

## 📋 Common Issues

| Issue | Fix |
|-------|-----|
| "Can't connect to MySQL" | Start MySQL: `net start MySQL80` (Windows) or similar |
| "No module named 'fastapi'" | Run: `pip install -r requirements.txt` |
| "Port 8000 in use" | Change `.env` PORT or kill process using port |
| "Database not found" | Run: `mysql -u root -p123456 < setup.sql` |

🔍 **More help:** See [TROUBLESHOOTING.md](TROUBLESHOOTING.md)

---

## 📚 Next Steps

1. **Explore API:** Visit http://localhost:8000/docs (Interactive Swagger UI)
2. **Read Docs:** Check [README.md](README.md) for complete guide
3. **Test Data:** Use [test_api.py](test_api.py) for automated testing
4. **Understand Code:** See [DEVELOPMENT.md](DEVELOPMENT.md)
5. **Deploy:** Follow [DEPLOYMENT.md](DEPLOYMENT.md) when ready

---

## 🎯 API Endpoints

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/health` | Health check |
| GET | `/` | API info |
| POST | `/api/users` | Create user |
| GET | `/api/users` | List users |
| GET | `/api/users/{id}` | Get user |
| PUT | `/api/users/{id}` | Update user |
| DELETE | `/api/users/{id}` | Delete user |

---

## ✅ Verification Checklist

After running server, verify:

```bash
# Health check (should return 200)
curl http://localhost:8000/health

# Create a user (should return 201)
curl -X POST http://localhost:8000/api/users \
  -H "Content-Type: application/json" \
  -d '{
    "username":"verify_test",
    "email":"verify@test.com",
    "phone":"1234567890",
    "password":"TestPass123"
  }'

# List users (should show your user)
curl http://localhost:8000/api/users

# View Swagger UI
# Open: http://localhost:8000/docs
```

---

**✨ All working? Congratulations! Your backend API is ready! 🎉**

For detailed documentation, see:
- [README.md](README.md) - Full guide
- [API_ENDPOINTS.md](docs/API_ENDPOINTS.md) - API details
- [DATABASE_SCHEMA.md](docs/DATABASE_SCHEMA.md) - Database structure
- [SECURITY.md](docs/SECURITY.md) - Encryption details

---

**Have questions? Check [TROUBLESHOOTING.md](TROUBLESHOOTING.md) or [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md)**
