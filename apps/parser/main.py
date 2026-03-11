from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field
from typing import Optional
import logging
from datetime import datetime
import os
from contextlib import asynccontextmanager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import router
from api.routes import router as api_router
from db.peraturan import init_db_pool, create_tables, close_db_pool


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager untuk startup dan shutdown"""
    # Startup
    try:
        # Initialize database pool
        await init_db_pool(
            host=os.getenv("DB_HOST", "localhost"),
            port=int(os.getenv("DB_PORT", "5432")),
            database=os.getenv("DB_NAME", "peraturan_db"),
            user=os.getenv("DB_USER", "postgres"),
            password=os.getenv("DB_PASSWORD", "password"),
            min_connections=1,
            max_connections=10
        )

        # Create tables
        await create_tables()

        logger.info("Parser API started successfully")
    except Exception as e:
        logger.error(f"Error during startup: {e}")
        raise

    yield

    # Shutdown
    try:
        await close_db_pool()
        logger.info("Parser API shutdown successfully")
    except Exception as e:
        logger.error(f"Error during shutdown: {e}")


# Initialize FastAPI app
app = FastAPI(
    title="Peraturan Parser API",
    description="HTTP Server untuk parsing PDF dari peraturan.go.id",
    version="0.1.0",
    lifespan=lifespan
)

# Include router
app.include_router(api_router, prefix="/api")

# Global status variable (legacy, maintained for compatibility)
parse_status = {
    "is_running": False,
    "last_run": None,
    "last_success": None,
    "total_parsed": 0,
    "error": None
}

# Request/Response Models (legacy)
class ParseRequest(BaseModel):
    url: Optional[str] = Field(None, description="URL spesifik untuk parsing, kosongkan untuk parsing semua")
    category: Optional[str] = Field(None, description="Kategori peraturan untuk filter")
    year: Optional[int] = Field(None, description="Tahun peraturan untuk filter")

class ParseResponse(BaseModel):
    status: str
    message: str
    job_id: Optional[str] = None

class StatusResponse(BaseModel):
    is_running: bool
    last_run: Optional[datetime]
    last_success: Optional[datetime]
    total_parsed: int
    error: Optional[str]

class HealthResponse(BaseModel):
    status: str
    timestamp: datetime


# Routes (legacy, maintained for backward compatibility)
@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now()
    )


@app.get("/status", response_model=StatusResponse)
async def get_status():
    """Get parsing status (legacy endpoint)"""
    from parser.status import get_parse_status
    return StatusResponse(**get_parse_status())


@app.post("/parse", response_model=ParseResponse)
async def trigger_parse(request: ParseRequest, background_tasks: BackgroundTasks):
    """Trigger parsing process (legacy endpoint)"""
    from parser.status import get_parse_status

    if parse_status["is_running"]:
        raise HTTPException(status_code=400, detail="Parsing sedang berjalan")

    # Generate job ID
    job_id = str(datetime.now().timestamp())

    # Add background task untuk parsing
    background_tasks.add_task(run_parse_task, request, job_id)

    return ParseResponse(
        status="queued",
        message=f"Parsing task di-queue: {request.url if request.url else 'semua peraturan'}",
        job_id=job_id
    )


async def run_parse_task(request: ParseRequest, job_id: str):
    """Background task untuk menjalankan parsing (legacy)"""
    global parse_status

    try:
        parse_status["is_running"] = True
        parse_status["last_run"] = datetime.now()
        parse_status["error"] = None

        logger.info(f"Mulai parsing: {request.url if request.url else 'semua peraturan'}")

        # TODO: Implement logic parsing sebenarnya di sini
        # - Scrape URL dari peraturan.go.id
        # - Download PDF files
        # - Parse content dari PDF
        # - Save ke database

        # Simulasi parsing (akan diganti nanti)
        await simulate_parsing()

        parse_status["is_running"] = False
        parse_status["last_success"] = datetime.now()
        parse_status["total_parsed"] += 1  # Update count

        logger.info("Parsing selesai berhasil")

    except Exception as e:
        parse_status["is_running"] = False
        parse_status["error"] = str(e)
        logger.error(f"Parsing gagal: {e}")


async def simulate_parsing():
    """Simulasi parsing untuk testing (akan diganti nanti)"""
    import asyncio
    await asyncio.sleep(5)  # Simulasi 5 detik


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
