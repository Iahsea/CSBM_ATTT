# Installation Guide - Hướng Dẫn Cài Đặt Chi Tiết

Hướng dẫn cài đặt đầy đủ cho Windows, Mac, và Linux.

---

## 🪟 Windows Installation

### Prerequisites
1. Windows 10/11
2. Administrator access
3. Internet connection

### Step 1: Install Python 3.11

**Option A: Download from python.org**
1. Go to https://www.python.org/downloads
2. Download Python 3.11+ (Latest stable)
3. Run installer
4. ✅ Check: "Add Python to PATH"
5. Click Install Now

**Verify installation:**
```cmd
python --version
```

### Step 2: Install MySQL 8.0

**Option A: MySQL Community Server**
1. Download from https://dev.mysql.com/downloads/mysql
2. Download MSI Installer
3. Run installer
4. Choose "Server only" or complete setup
5. Configure MySQL Server:
   - Port: 3306
   - Root password: 123456 (as per .env)
6. Select "Standard System Configure"
7. Finish installation

**Option B: MySQL via Chocolatey (faster)**
```cmd
# Install Chocolatey first if needed
# Then:
choco install mysql-server
```

**Verify MySQL:**
```cmd
mysql -u root -p123456 -e "SELECT VERSION();"
```

### Step 3: Install Git (Optional but Recommended)

Download from https://git-scm.com/download/win

---

### Step 4: Clone/Download Backend Project

**Using Git:**
```cmd
cd d:\Document\CSAT_BMPT
git clone <repo-url> BackEnd
cd BackEnd
```

**Or manually:**
- Download ZIP from GitHub/source
- Extract to `d:\Document\CSAT_BMPT\BackEnd`

---

### Step 5: Setup & Run

**Quick Method (Automated):**
```cmd
run_windows.bat
```

**Manual Method:**

```cmd
# Create virtual environment
python -m venv venv

# Activate it
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Setup database
mysql -u root -p123456 < setup.sql

# Run server
python main.py
```

---

### Verification

```cmd
# Should show success message
curl http://localhost:8000/health
```

---

## 🍎 Mac Installation

### Prerequisites
1. macOS 10.14+
2. Homebrew (https://brew.sh)
3. Internet connection

### Step 1: Install Python 3.11

```bash
brew install python@3.11
```

**Verify:**
```bash
python3.11 --version
```

**Create alias (optional):**
```bash
echo 'alias python=python3.11' >> ~/.zshrc
source ~/.zshrc
```

---

### Step 2: Install MySQL 8.0

```bash
# Install MySQL
brew install mysql

# Start MySQL
brew services start mysql

# Configure password
mysql -u root << EOF
ALTER USER 'root'@'localhost' IDENTIFIED BY '123456';
FLUSH PRIVILEGES;
EOF
```

**Verify:**
```bash
mysql -u root -p123456 -e "SELECT VERSION();"
```

---

### Step 3: Install Git (Usually Pre-installed)

```bash
# Check if installed
git --version

# If not:
brew install git
```

---

### Step 4: Clone Backend Project

```bash
mkdir -p ~/Documents/CSAT_BMPT
cd ~/Documents/CSAT_BMPT
git clone <repo-url> BackEnd
cd BackEnd
```

---

### Step 5: Setup & Run

```bash
# Create virtual environment
python3.11 -m venv venv

# Activate it
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Setup database
mysql -u root -p123456 < setup.sql

# Run server
python main.py
```

---

### Verification

```bash
# Should return 200
curl http://localhost:8000/health

# Or use automated script
bash run_unix.sh
```

---

## 🐧 Linux Installation

### Prerequisites
1. Ubuntu 20.04+ / Debian 11+
2. Sudo access
3. Internet connection

### Step 1: Update System

```bash
sudo apt update
sudo apt upgrade -y
```

### Step 2: Install Python 3.11

```bash
sudo apt install -y python3.11 python3.11-venv python3-pip
```

**Verify:**
```bash
python3.11 --version
```

---

### Step 3: Install MySQL Server

```bash
# Install MySQL
sudo apt install -y mysql-server

# Start service
sudo systemctl start mysql

# Enable auto-start
sudo systemctl enable mysql

# Verify
mysql --version
```

**Configure MySQL (Optional):**
```bash
sudo mysql_secure_installation
```

---

### Step 4: Set MySQL Root Password

```bash
sudo mysql -u root << EOF
ALTER USER 'root'@'localhost' IDENTIFIED BY '123456';
FLUSH PRIVILEGES;
EOF
```

**Verify:**
```bash
mysql -u root -p123456 -e "SELECT VERSION();"
```

---

### Step 5: Install Git

```bash
sudo apt install -y git
```

---

### Step 6: Clone Backend Project

```bash
mkdir -p ~/projects/csat
cd ~/projects/csat
git clone <repo-url> BackEnd
cd BackEnd
```

---

### Step 7: Setup & Run

```bash
# Create virtual environment
python3.11 -m venv venv

# Activate it
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Setup database
mysql -u root -p123456 < setup.sql

# Run server
python main.py
```

---

### Make Scripts Accessible (Optional)

```bash
# Make run script executable
chmod +x run_unix.sh

# Run it
./run_unix.sh
```

---

### Verification

```bash
# Check server health
curl http://localhost:8000/health

# Expected response: {"status":"ok"}
```

---

## 🐳 Docker Installation (All Platforms)

**Recommended for:** Temporary testing, easy cleanup, production

### Prerequisites
1. Docker Desktop installed
2. 4GB+ RAM available

### Installation Links
- **Windows/Mac:** https://www.docker.com/products/docker-desktop
- **Linux:** `sudo apt install docker.io docker-compose`

### Step 1: Install Docker

**Windows/Mac:**
1. Download Docker Desktop
2. Install and start
3. Verify: `docker --version`

**Linux:**
```bash
sudo apt install docker.io docker-compose
sudo systemctl start docker
```

---

### Step 2: Clone Project

```bash
git clone <repo-url> BackEnd
cd BackEnd
```

---

### Step 3: Run with Docker Compose

```bash
# Start all services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f backend
```

---

### Step 4: Access API

Visit http://localhost:8000/docs

### Stop Services

```bash
docker-compose down
```

---

## 🔧 Post-Installation Configuration

### 1. Verify All Components

```bash
# Python
python --version

# MySQL
mysql -u root -p123456 -e "SELECT 1;"

# FastAPI
curl http://localhost:8000/health

# Browser
# Visit http://localhost:8000/docs
```

### 2. Adjust Environment (If Needed)

Edit `.env` file:
```env
# Change if needed
DATABASE_USER=root
DATABASE_PASSWORD=123456
DATABASE_HOST=localhost
DATABASE_PORT=3306
DATABASE_NAME=user_db
HOST=0.0.0.0
PORT=8000
```

### 3. Initialize Database (One Time)

```bash
mysql -u root -p123456 < setup.sql
```

### 4. Test API

```python
# Create test user
curl -X POST http://localhost:8000/api/users \
  -H "Content-Type: application/json" \
  -d '{
    "username":"install_test",
    "email":"test@install.com",
    "phone":"0123456789",
    "password":"TestPass123"
  }'
```

---

## 🆘 Platform-Specific Troubleshooting

### Windows Issues

**Python not found:**
- Reinstall Python and check "Add to PATH"
- Use full path: `C:\Python311\python.exe`

**MySQL port conflict:**
- Change port in `.env`: PORT=3307
- Or: `netstat -ano | findstr 3306` to find process

**Virtual environment activation fails:**
```cmd
# Try PowerShell instead of CMD
powershell
venv\Scripts\Activate.ps1
```

---

### Mac Issues

**Permission denied on scripts:**
```bash
chmod +x run_unix.sh
./run_unix.sh
```

**MySQL connection refused:**
```bash
brew services start mysql
```

**Cannot find MySQL:**
```bash
# Add to PATH
export PATH="/usr/local/opt/mysql/bin:$PATH"
```

---

### Linux Issues

**MySQL permission denied:**
```bash
sudo mysql -u root -p123456
# Or
sudo usermod -aG mysql $USER
```

**Python venv fails:**
```bash
sudo apt install python3.11-venv
python3.11 -m venv venv
```

**Port 8000 already in use:**
```bash
lsof -i :8000
kill -9 <PID>
```

---

## ✅ Installation Verification Checklist

- [ ] Python installed: `python --version`
- [ ] MySQL running: `mysql -u root -p123456 -e "SELECT 1;"`
- [ ] Project folder exists
- [ ] Virtual environment created
- [ ] Dependencies installed: `pip list | grep fastapi`
- [ ] Database initialized: `mysql -u root -p123456 -e "SHOW TABLES FROM user_db;"`
- [ ] Server starts: `python main.py` (no errors)
- [ ] Health check passes: `curl http://localhost:8000/health`
- [ ] Swagger UI loads: http://localhost:8000/docs

---

## 🚀 Next Steps

After successful installation:

1. **Quick Start:** Run test API: `python test_api.py`
2. **Explore Docs:** Visit http://localhost:8000/docs in browser
3. **Read Guide:** Check [README.md](README.md)
4. **Try Deploy:** Check [DEPLOYMENT.md](DEPLOYMENT.md)

---

**Installation complete! 🎉 Start developing!**

For issues, see [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
