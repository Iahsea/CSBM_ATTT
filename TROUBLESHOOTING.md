# Troubleshooting Guide - Hướng Dẫn Khắc Phục Sự Cố

Danh sách các vấn đề phổ biến và cách giải quyết.

---

## 🔴 MySQL Connection Issues

### ❌ Error: "Can't connect to MySQL server on 'localhost'"

**Nguyên nhân:**
- MySQL service không chạy
- Credentials sai
- Firewall chặn port 3306

**Giải pháp:**

**1. Kiểm tra MySQL đang chạy:**
- **Windows:** `Services` → tìm `MySQL` → khởi động nếu dừng
- **Mac:** `brew services list` → check MySQL status
- **Linux:** `sudo systemctl status mysql`

**2. Khởi động MySQL:**
- **Windows:** `net start MySQL80` (hoặc phiên bản của bạn)
- **Mac:** `brew services start mysql`
- **Linux:** `sudo systemctl start mysql`

**3. Kiểm tra credentials:**
```bash
mysql -u root -p123456
```

Nếu không kết nối, reset password MySQL:
- **Windows:** Start MySQL with skip-grant-tables, reset password
- **Linux:** `sudo mysqld_safe --skip-grant-tables &`

**4. Kiểm tra port 3306:**
```bash
# Windows
netstat -an | findstr 3306

# Mac/Linux
lsof -i :3306
```

---

### ❌ Error: "Unknown database 'user_db'"

**Nguyên nhân:** Database chưa được tạo

**Giải pháp:**
```bash
# Run setup script
mysql -u root -p123456 < setup.sql

# Or create manually
mysql -u root -p123456 << EOF
CREATE DATABASE user_db CHARACTER SET utf8mb4;
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
) CHARACTER SET utf8mb4;
EOF
```

---

### ❌ Error: "Access denied for user 'root'"

**Nguyên nhân:** Password sai

**Giải pháp:**

**1. Kiểm tra credentials trong `.env`:**
```
DATABASE_USER=root
DATABASE_PASSWORD=123456
```

**2. Kiểm tra MySQL accept password:**
```bash
mysql -u root -p123456 -e "SELECT VERSION();"
```

**3. Reset MySQL root password:**
- **Windows:**
```commandline
# Stop MySQL
net stop MySQL80

# Start with skip-grant-tables
mysqld --skip-grant-tables

# In another terminal
mysql -u root

mysql> FLUSH PRIVILEGES;
mysql> ALTER USER 'root'@'localhost' IDENTIFIED BY '123456';
mysql> EXIT;
```

---

## 🟡 Python Environment Issues

### ❌ Error: "No module named 'fastapi'"

**Nguyên nhân:** Dependencies chưa được cài

**Giải pháp:**
```bash
# Activate virtual environment first
source venv/bin/activate  # Mac/Linux
# or
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Verify installation
pip list | grep fastapi
```

---

### ❌ Error: "ModuleNotFoundError" after pip install

**Nguyên nhân:** Virtual environment không được activate

**Kiểm tra:**
```bash
# Should show path with /venv/
which python

# If not from venv:
source venv/bin/activate
```

---

### ❌ Error: "Python version not compatible"

**Nguyên nhân:** Python < 3.9

**Kiểm tra version:**
```bash
python --version
```

**Nếu version cũ:**
- **Windows:** Download Python 3.11+ from python.org
- **Mac:** `brew install python@3.11`
- **Linux:** `sudo apt install python3.11`

---

## 🟠 FastAPI Server Issues

### ❌ Error: "Address already in use" port 8000

**Nguyên nhân:** Port 8000 đã được sử dụng

**Giải pháp:**

**1. Tìm process sử dụng port:**
```bash
# Windows
netstat -ano | findstr :8000

# Mac/Linux
lsof -i :8000
```

**2. Kết thúc process:**
```bash
# Windows (thay PID = process ID)
taskkill /PID 12345 /F

# Mac/Linux
kill -9 12345
```

**3. Hoặc sử dụng port khác:**
```bash
# Chỉnh sửa .env
PORT=8001

# Hoặc run trực tiếp
python main.py --port 8001
```

---

### ❌ Error: "Uvicorn is not installed"

**Giải pháp:**
```bash
pip install uvicorn
# or
pip install -r requirements.txt
```

---

### ❌ Error: "Application startup failed"

**Nguyên nhân:** Database không sẵn sàng

**Giải pháp:**

**1. Kiểm tra logs:**
```bash
# Xem error message chi tiết
python main.py
```

**2. Kiểm tra database:**
```bash
mysql -u root -p123456 -e "SELECT * FROM user_db.users LIMIT 1;"
```

**3. Reset database:**
```bash
mysql -u root -p123456 < setup.sql
```

---

## 🔴 API Request Issues

### ❌ Error: "404 Not Found"

**Nguyên nhân:** Endpoint sai hoặc server không chạy

**Kiểm tra:**

**1. Server running?**
```bash
curl http://localhost:8000/health
```

**2. Endpoint URL đúng?**
```bash
# Correct
curl http://localhost:8000/api/users

# Wrong (missing /api)
curl http://localhost:8000/users

# Wrong (typo endpoint)
curl http://localhost:8000/api/user  # Should be /users
```

---

### ❌ Error: "400 Bad Request" - Email validation

**Nguyên nhân:** Email format sai

**Giải pháp:**
```bash
# ❌ Wrong
curl -X POST http://localhost:8000/api/users \
  -H "Content-Type: application/json" \
  -d '{"username":"test","email":"not-email","phone":"123","password":"pass"}'

# ✅ Right
curl -X POST http://localhost:8000/api/users \
  -H "Content-Type: application/json" \
  -d '{"username":"test","email":"test@example.com","phone":"0987654321","password":"pass"}'
```

---

### ❌ Error: "409 Conflict" - Duplicate username

**Nguyên nhân:** Username đã tồn tại

**Giải pháp:**

**1. Sử dụng username khác:**
```bash
# Tạo user với username duy nhất
curl -X POST http://localhost:8000/api/users \
  -d '{"username":"new_unique_user","email":"new@example.com",...}'
```

**2. Hoặc xóa user cũ:**
```bash
# Xóa user với ID 1
curl -X DELETE http://localhost:8000/api/users/1
```

---

### ❌ Error: "500 Internal Server Error"

**Nguyên nhân:** Lỗi trong backend

**Giải pháp:**

**1. Xem detailed error:**
```bash
# Run server với debug mode
ENV=development python main.py
```

**2. Check logs:**
- Xem error message trong terminal
- Kiểm tra MySQL logs

**3. Kiểm tra database:**
```bash
mysql -u root -p123456 -e "DESCRIBE user_db.users;"
```

---

## 🟠 Data Encryption Issues

### ❌ Error: "Cannot decrypt data"

**Nguyên nhân:** 
- Key generation khác
- Data bị corrupt

**Giải pháp:**

**1. Kiểm tra credentials:**
- Username và password phải match khi tạo user

**2. Xem raw data:**
```bash
# Query database trực tiếp
mysql -u root -p123456 -e "SELECT id, username, HEX(email) FROM user_db.users;"
```

**3. Reset user:**
```bash
# Delete and recreate
DELETE FROM user_db.users WHERE username='test_user';
```

---

## 🟡 Docker Issues

### ❌ Error: "Docker daemon is not running"

**Giải pháp:**
- **Windows:** Start Docker Desktop
- **Mac:** `open /Applications/Docker.app`
- **Linux:** `sudo systemctl start docker`

---

### ❌ Error: "Cannot connect to Docker daemon"

**Giải pháp:**
```bash
# Check Docker status
docker ps

# Start Docker
sudo systemctl start docker

# Add user to docker group (Linux)
sudo usermod -aG docker $USER
```

---

### ❌ Error: "MySQL container won't start"

**Giải pháp:**
```bash
# Check container logs
docker-compose logs mysql

# Inspect container
docker inspect csat_mysql

# Remove and restart
docker-compose down -v
docker-compose up -d
```

---

## 🟢 Performance Issues

### ❌ Problem: "API responses slow"

**Giải pháp:**

**1. Check database:**
```bash
# List slow queries
mysql -u root -p123456 << EOF
SET GLOBAL slow_query_log = 'ON';
SET GLOBAL long_query_time = 1;
EOF

# Then check slow query log after requests
tail -f /var/log/mysql/slow-log
```

**2. Add indexes:**
```sql
CREATE INDEX idx_email_hash ON users(email(20));
CREATE INDEX idx_created_at ON users(created_at);
```

**3. Monitor connections:**
```bash
mysql -u root -p123456 -e "SHOW PROCESSLIST;"
```

---

### ❌ Problem: "High memory usage"

**Giải pháp:**

**1. Reduce Gunicorn workers:**
```bash
# Instead of 4 workers
gunicorn main:app -w 2 -b 127.0.0.1:8000
```

**2. Check for memory leaks:**
```bash
# Monitor memory
watch -n 1 'ps aux | grep python'
```

---

## 📋 Quick Diagnostic Checklist

Run ini khi gặp vấn đề:

```bash
# 1. MySQL status
mysql -u root -p123456 -e "SELECT VERSION(); SHOW DATABASES; SELECT COUNT(*) FROM user_db.users;"

# 2. Python environment
python -c "import fastapi; print('FastAPI:', fastapi.__version__)"
pip list | grep -E "fastapi|sqlalchemy|mysql"

# 3. Server connectivity
curl http://localhost:8000/health

# 4. Port status
netstat -an | grep 8000
netstat -an | grep 3306

# 5. Logs
tail -20 /var/log/mysql/error.log  # Linux
Get-EventLog -LogName Application -Newest 20  # Windows

# 6. File permissions
ls -la main.py .env app/
```

---

## 🆘 Still Have Issues?

**Sử dụng lệnh này để collect thông tin:**

```bash
# Create diagnostic report
{
  echo "=== Python ==="; python --version
  echo "=== MySQL ==="; mysql --version
  echo "=== Docker ==="; docker --version 2>/dev/null || echo "Not installed"
  echo "=== FastAPI ==="; pip show fastapi | grep Version
  echo "=== MySQL Connectivity ==="; mysql -u root -p123456 -e "SELECT 1" 2>&1
  echo "=== Server Health ==="; curl -s http://localhost:8000/health || echo "Server not running"
} > diagnostic-report.txt

# Send report for debugging
cat diagnostic-report.txt
```

---

**📝 Notes:**
- Thay thế `123456` bằng password của bạn
- Thay thế `localhost` bằng server address nếu remote
- Check lại credentials trong `.env` file

---

**✅ Mong sự cố được giải quyết! Contact admin nếu cần hỗ trợ thêm.**
