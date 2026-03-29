@echo off
REM ==================== Quick Start Script ====================
REM Setup MySQL database và chuẩn bị chạy server

setlocal enabledelayedexpansion

echo.
echo ========================================
echo  Backend Project Quick Start
echo ========================================
echo.

REM Check if MySQL is installed
echo [1/4] Checking MySQL installation...
mysql --version > nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ MySQL is not installed or not in PATH
    echo Please install MySQL and add it to PATH environment variable
    exit /b 1
)
echo ✅ MySQL found

REM Create database
echo.
echo [2/4] Creating database...
mysql -u root -p123456 < setup.sql
if %errorlevel% neq 0 (
    echo ❌ Failed to create database
    exit /b 1
)
echo ✅ Database created

REM Install Python packages
echo.
echo [3/4] Installing Python packages...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ❌ Failed to install packages
    exit /b 1
)
echo ✅ Packages installed

REM Start server
echo.
echo [4/4] Starting FastAPI server...
echo.
echo ========================================
echo  Server Information:
echo ========================================
echo  URL: http://localhost:8000
echo  Docs: http://localhost:8000/docs
echo  ReDoc: http://localhost:8000/redoc
echo  Health: http://localhost:8000/health
echo ========================================
echo.

python main.py

pause
