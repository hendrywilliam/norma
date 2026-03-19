"""
Main Entry Point untuk Parser API
FastAPI application untuk parsing PDF dari peraturan.go.id
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
import os
from typing import Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import router
from api.routes import router as api_router

# Import database functions
from db.peraturan import init_db_pool, close_db_pool

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager untuk startup dan shutdown

    Tasks:
    - Startup: Inisialisasi database connection pool
    - Shutdown: Tutup database connection pool
    """
    # Startup
    try:
        logger.info("Starting Parser API...")

        # Initialize database pool
        await init_db_pool(
            host=os.getenv("DB_HOST", "localhost"),
            port=int(os.getenv("DB_PORT", "5432")),
            database=os.getenv("DB_NAME", "peraturan_db"),
            user=os.getenv("DB_USER", "postgres"),
            password=os.getenv("DB_PASSWORD", "postgres"),
            min_connections=int(os.getenv("DB_MIN_CONNECTIONS", "1")),
            max_connections=int(os.getenv("DB_MAX_CONNECTIONS", "10"))
        )

        logger.info("Database connection pool initialized successfully")
        logger.info("Parser API started successfully")

    except Exception as e:
        logger.error(f"Failed to start Parser API: {e}")
        raise

    yield

    # Shutdown
    try:
        logger.info("Shutting down Parser API...")
        await close_db_pool()
        logger.info("Database connection pool closed successfully")
        logger.info("Parser API shutdown successfully")
    except Exception as e:
        logger.error(f"Error during shutdown: {e}")


# Initialize FastAPI app
app = FastAPI(
    title="Peraturan Parser API",
    description="HTTP Server untuk parsing PDF dari peraturan.go.id dengan struktur bab, pasal, ayat",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(api_router, prefix="/api")


# Root endpoint untuk cek API
@app.get("/", tags=["Root"])
async def root():
    """
    Root endpoint untuk mengecek API

    Returns:
        Message API dan dokumentasi
    """
    return {
        "name": "Peraturan Parser API",
        "version": "0.1.0",
        "status": "running",
        "docs": "/docs",
        "redoc": "/redoc",
        "endpoints": {
            "health": "/api/health",
            "status": "/api/status",
            "parse": "/api/parse",
            "peraturan": "/api/peraturan",
            "bab": "/api/peraturan/{peraturan_id}/bab",
            "pasals": "/api/peraturan/{peraturan_id}/pasals",
            "ayats": "/api/peraturan/{peraturan_id}/pasals/{pasal_id}/ayats"
        }
    }


if __name__ == "__main__":
    import uvicorn
    import uvicorn.logging

    # Configure uvicorn logging
    uvicorn.config.LOG_LEVEL_CONFIG["uvicorn.access"] = "WARNING"

    uvicorn.run(
        "main:app",
        host=os.getenv("HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", "8000")),
        reload=os.getenv("RELOAD", "false").lower() == "true",
        log_level=os.getenv("LOG_LEVEL", "info")
    )
