#!/usr/bin/env python
"""
Quick Setup & Test Runner
Chạy lần lượt tất cả steps để test hệ thống
"""
import os
import sys
import subprocess
import time
import requests
from pathlib import Path

def print_header(text):
    print("\n" + "="*60)
    print(f"  {text}")
    print("="*60 + "\n")

def print_step(num, text):
    print(f"[Step {num}] {text}")

def print_success(text):
    print(f"✅ {text}")

def print_error(text):
    print(f"❌ {text}")

def print_warning(text):
    print(f"⚠️  {text}")

# ==================== Setup ====================

print_header("QUICK SETUP & TEST")

# Step 1: Check Python
print_step(1, "Checking Python")
try:
    import fastapi
    import sqlalchemy
    print_success(f"FastAPI {fastapi.__version__} installed")
    print_success(f"SQLAlchemy {sqlalchemy.__version__} installed")
except ImportError as e:
    print_error(f"Missing dependency: {e}")
    print_warning("Run: pip install -r requirements.txt")
    sys.exit(1)

# Step 2: Check database
print_step(2, "Checking Database")
try:
    import mysql.connector
    print_success("MySQL connector available")
except ImportError:
    print_error("MySQL connector not installed")
    print_warning("Run: pip install mysql-connector-python")

# Step 3: Setup .env
print_step(3, "Checking .env configuration")
if Path(".env").exists():
    print_success(".env file exists")
    with open(".env") as f:
        config = f.read()
        if "DATABASE_PASSWORD" in config:
            print_success("Database credentials configured")
else:
    print_warning(".env not found, creating with defaults...")
    env_content = """DATABASE_USER=root
DATABASE_PASSWORD=123456
DATABASE_HOST=localhost
DATABASE_PORT=3306
DATABASE_NAME=user_db
SECRET_KEY=your-secret-key-change-in-production
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=60
"""
    with open(".env", "w") as f:
        f.write(env_content)
    print_success(".env created with default values")

# Step 4: Check database exists
print_step(4, "Checking MySQL database")
print_warning("Make sure MySQL is running and database 'user_db' exists")
print_warning("If not, run: mysql -u root -p < setup.sql")
user_input = input("\nReady to continue? (y/n): ").strip().lower()
if user_input != 'y':
    print("Exiting...")
    sys.exit(1)

# Step 5: Start server
print_header("STARTING SERVER")
print_step(5, "Starting FastAPI server...")
print_warning("The server will run in the background")
print_warning("Press Ctrl+C to stop server anytime\n")

# Run server in background
process = subprocess.Popen(
    [sys.executable, "main.py"],
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE
)

print("⏳ Waiting for server startup (3 seconds)...")
time.sleep(3)

# Check if server is running
try:
    response = requests.get("http://localhost:8000/health", timeout=5)
    if response.status_code == 200:
        print_success("Server is running at http://localhost:8000")
    else:
        print_error(f"Server returned status {response.status_code}")
except requests.exceptions.ConnectionError:
    print_error("Cannot connect to server")
    print_warning("Make sure port 8000 is available")
    print_warning("See server output above for error details")
    process.kill()
    sys.exit(1)

# Step 6: Run tests
print_header("RUNNING TESTS")
print_step(6, "Running complete test suite...\n")

try:
    # Import and run tests
    exec(open("test_complete_flow.py").read())
except KeyboardInterrupt:
    print("\n\nTest interrupted by user")
except Exception as e:
    print_error(f"Test error: {e}")
finally:
    # Stop server
    print_header("CLEANUP")
    print_step(7, "Stopping server...")
    process.terminate()
    try:
        process.wait(timeout=5)
        print_success("Server stopped")
    except subprocess.TimeoutExpired:
        print_warning("Force killing server...")
        process.kill()

print_header("DONE")
print_success("Setup and testing complete!")
print("\n📚 Next steps:")
print("  1. Review TEST_GUIDE.md for manual testing")
print("  2. Check IMPLEMENTATION_SUMMARY.md for details")
print("  3. Start server: python main.py")
print("  4. Open docs: http://localhost:8000/docs")
