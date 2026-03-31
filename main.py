"""
FastAPI Main Application
Entry point của backend server
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
import logging

from app.database import init_db, close_db
from app.routers import user_router
from app.routers.auth import router as auth_router

# Logging configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Data Masking + Encryption Backend",
    description="Hệ thống quản lý dữ liệu an toàn với Data Masking + Encryption",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# ==================== CORS Configuration ====================

origins = [
    "http://localhost",
    "http://localhost:3000",
    "http://localhost:4200",
    "http://localhost:5000",
    "http://localhost:8000",
    "http://127.0.0.1",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:4200",
    "http://127.0.0.1:5000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logger.info("✓ CORS middleware added")


# ==================== Startup & Shutdown Events ====================

@app.on_event("startup")
async def startup_event():
    """
    Chạy khi server khởi động.
    - Khởi tạo database
    - Log startup info
    """
    logger.info("🚀 Starting up server...")
    
    try:
        await init_db()
        logger.info("✅ Database initialized")
    except Exception as e:
        logger.error(f"❌ Failed to initialize database: {e}")
    
    logger.info("✨ Server started successfully!")


@app.on_event("shutdown")
async def shutdown_event():
    """
    Chạy khi server tắt.
    - Đóng database connections
    """
    logger.info("🛑 Shutting down server...")
    
    try:
        await close_db()
        logger.info("✅ Database connections closed")
    except Exception as e:
        logger.error(f"❌ Failed to close database: {e}")
    
    logger.info("✨ Server shutdown complete!")


# ==================== Routes ====================

@app.get(
    "/",
    tags=["root"],
    summary="API Root",
    description="Lấy thông tin API"
)
async def root():
    """
    GET /
    Root endpoint trả về thông tin API
    """
    return {
        "message": "Data Masking + Encryption Backend",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
        "redoc": "/redoc"
    }


@app.get(
    "/health",
    tags=["health"],
    summary="Health Check",
    description="Kiểm tra server health"
)
async def health_check():
    """
    GET /health
    Health check endpoint
    """
    return {
        "status": "healthy",
        "message": "Server is running"
    }


# Include routers
app.include_router(
    auth_router,
    prefix="/api/auth",
    tags=["auth"]
)

logger.info("✓ Auth router included at /api/auth")

app.include_router(
    user_router,
    prefix="/api/users",
    tags=["users"]
)

logger.info("✓ User router included at /api/users")


# ==================== Error Handlers ====================

@app.exception_handler(ValueError)
async def value_error_handler(request, exc):
    """
    Custom handler cho ValueError
    """
    return {
        "error": "Validation Error",
        "detail": str(exc)
    }


# ==================== Logging ====================

logger.info("=" * 60)
logger.info("🎯 FastAPI Application Configured")
logger.info("=" * 60)
logger.info(f"📡 API Docs: http://localhost:8000/docs")
logger.info(f"📡 ReDoc: http://localhost:8000/redoc")
logger.info(f"📡 API Root: http://localhost:8000/")
logger.info(f"📡 Health Check: http://localhost:8000/health")
logger.info(f"📡 API Users: http://localhost:8000/api/users")
logger.info("=" * 60)


# ==================== Entry Point ====================

if __name__ == "__main__":
    import uvicorn
    
    # Get environment variables
    HOST = os.getenv("HOST", "0.0.0.0")
    PORT = int(os.getenv("PORT", 8000))
    RELOAD = os.getenv("RELOAD", "true").lower() == "true"
    
    logger.info(f"🚀 Starting server at {HOST}:{PORT}")
    logger.info(f"🔄 Auto-reload: {RELOAD}")
    
    uvicorn.run(
        "main:app",
        host=HOST,
        port=PORT,
        reload=RELOAD,
        log_level="info"
    )
