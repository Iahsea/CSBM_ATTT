#!/bin/bash

# ==================== Quick Start Script (Linux/macOS) ====================
# Setup MySQL database và chuẩn bị chạy server

echo ""
echo "========================================"
echo "  Backend Project Quick Start"
echo "========================================"
echo ""

# Check if MySQL is installed
echo "[1/4] Checking MySQL installation..."
if ! command -v mysql &> /dev/null; then
    echo "❌ MySQL is not installed"
    echo "Install MySQL and try again"
    exit 1
fi
echo "✅ MySQL found"

# Create database
echo ""
echo "[2/4] Creating database..."
mysql -u root -p123456 < setup.sql
if [ $? -ne 0 ]; then
    echo "❌ Failed to create database"
    exit 1
fi
echo "✅ Database created"

# Create virtual environment (optional)
echo ""
echo "[3/4] Setting up Python environment..."
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install Python packages
echo "Installing Python packages..."
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "❌ Failed to install packages"
    exit 1
fi
echo "✅ Packages installed"

# Start server
echo ""
echo "[4/4] Starting FastAPI server..."
echo ""
echo "========================================"
echo "  Server Information:"
echo "========================================"
echo "  URL: http://localhost:8000"
echo "  Docs: http://localhost:8000/docs"
echo "  ReDoc: http://localhost:8000/redoc"
echo "  Health: http://localhost:8000/health"
echo "========================================"
echo ""

python main.py
