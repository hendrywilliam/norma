"""
API Routes untuk Parser
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

# Initialize router
router = APIRouter()

# Request/Response Models
class ParseRequest(BaseModel):
    url: Optional[str] = Field(None, description="URL spesifik untuk parsing, kosongkan untuk parsing semua")
    category: Optional[str] = Field(None, description="Kategori peraturan untuk filter")
    year: Optional[int] = Field(None, description="Tahun peraturan untuk filter")
    force: bool = Field(False, description="Force re-parsing meskipun sudah ada di database")

class ParseResponse(BaseModel):
    status: str
    message: str
    job_id: Optional[str] = None
    estimated_time: Optional[int] = None  # dalam detik

class StatusResponse(BaseModel):
    is_running: bool
    last_run: Optional[datetime]
    last_success: Optional[datetime]
    total_parsed: int
    total_failed: int
    error: Optional[str]
    current_task: Optional[str] = None

class HealthResponse(BaseModel):
    status: str
    timestamp: datetime
    version: str

class PeraturanSummary(BaseModel):
    id: str
    judul: str
    nomor: str
    tahun: int
    kategori: str
    tanggal_disahkan: Optional[datetime]
    created_at: datetime


# Routes
@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint untuk monitoring"""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now(),
        version="0.1.0"
    )


@router.get("/status", response_model=StatusResponse)
async def get_status():
    """Get status parsing terakhir"""
    # TODO: Implement fetch status dari database/memory
    from ..parser.status import get_parse_status

    status_data = get_parse_status()
    return StatusResponse(**status_data)


@router.post("/parse", response_model=ParseResponse)
async def trigger_parse(request: ParseRequest, background_tasks: BackgroundTasks):
    """Trigger parsing process

    Args:
        request: Parse request dengan parameter filter
        background_tasks: FastAPI background tasks untuk async execution

    Returns:
        ParseResponse dengan status job
    """
    from ..parser.status import get_parse_status

    # Cek apakah parsing sedang berjalan
    status = get_parse_status()
    if status["is_running"] and not request.force:
        raise HTTPException(
            status_code=400,
            detail="Parsing sedang berjalan. Gunakan force=true untuk override."
        )

    # Generate job ID
    job_id = f"parse_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    # Add background task
    background_tasks.add_task(run_parse_task, request, job_id)

    # Estimasi waktu berdasarkan request
    estimated_time = estimate_parse_time(request)

    return ParseResponse(
        status="queued",
        message=f"Parsing task di-queue: {request.url if request.url else 'semua peraturan'}",
        job_id=job_id,
        estimated_time=estimated_time
    )


@router.get("/peraturan", response_model=List[PeraturanSummary])
async def list_peraturan(
    skip: int = 0,
    limit: int = 20,
    category: Optional[str] = None,
    year: Optional[int] = None,
    search: Optional[str] = None
):
    """List semua peraturan di database dengan filter

    Args:
        skip: Offset untuk pagination
        limit: Max hasil per page
        category: Filter kategori
        year: Filter tahun
        search: Search string di judul/nomor

    Returns:
        List dari peraturan summary
    """
    # TODO: Implement fetch dari database
    from ..db.peraturan import get_peraturan_list

    peraturan = await get_peraturan_list(
        skip=skip,
        limit=limit,
        category=category,
        year=year,
        search=search
    )

    return peraturan


@router.get("/peraturan/{peraturan_id}")
async def get_peraturan_detail(peraturan_id: str):
    """Get detail peraturan spesifik

    Args:
        peraturan_id: ID peraturan

    Returns:
        Detail peraturan lengkap dengan konten
    """
    # TODO: Implement fetch detail dari database
    from ..db.peraturan import get_peraturan_by_id

    peraturan = await get_peraturan_by_id(peraturan_id)

    if not peraturan:
        raise HTTPException(status_code=404, detail="Peraturan tidak ditemukan")

    return peraturan


@router.post("/peraturan/{peraturan_id}/reparse")
async def reparse_peraturan(peraturan_id: str, background_tasks: BackgroundTasks):
    """Trigger re-parse untuk peraturan spesifik

    Args:
        peraturan_id: ID peraturan untuk di-reparse

    Returns:
        ParseResponse dengan status job
    """
    from ..db.peraturan import get_peraturan_by_id

    # Cek apakah peraturan ada
    peraturan = await get_peraturan_by_id(peraturan_id)
    if not peraturan:
        raise HTTPException(status_code=404, detail="Peraturan tidak ditemukan")

    job_id = f"reparse_{peraturan_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    # Add background task untuk re-parse
    background_tasks.add_task(run_reparse_task, peraturan_id, job_id)

    return ParseResponse(
        status="queued",
        message=f"Re-parse task di-queue: {peraturan['judul']}",
        job_id=job_id,
        estimated_time=60  # Estimasi 1 menit untuk re-parse
    )


# Helper Functions
async def run_parse_task(request: ParseRequest, job_id: str):
    """Background task untuk menjalankan parsing"""
    from ..parser.status import update_parse_status
    from ..parser.scraper import scrape_peraturan, download_pdf
    from ..parser.pdf_parser import parse_pdf_from_bytes
    from ..db.peraturan import save_peraturan
    from ..parser.pdf_parser import extract_structure, extract_keywords

    try:
        from ..parser.status import start_parsing, update_progress, increment_success_count, increment_failure_count, finish_parsing

        start_parsing(job_id)

        logger.info(f"[{job_id}] Mulai parsing: {request.url if request.url else 'semua peraturan'}")

        # 1. Scrape URLs dari peraturan.go.id
        update_parse_status(current_task="Scraping URLs")
        urls = await scrape_peraturan(
            url=request.url,
            category=request.category,
            year=request.year
        )

        logger.info(f"[{job_id}] Ditemukan {len(urls)} URL untuk di-parse")

        if not urls:
            logger.warning(f"[{job_id}] Tidak ada URL ditemukan")
            finish_parsing(success=True)
            return

        # 2. Download dan parse setiap PDF
        success_count = 0
        failed_count = 0

        for idx, url_info in enumerate(urls, 1):
            try:
                update_progress(idx, len(urls), f"Parsing {idx}/{len(urls)}: {url_info.get('judul', 'Unknown')}")

                # Dapatkan PDF URL dari detail page jika belum ada
                pdf_url = url_info.get("pdf_url")
                if not pdf_url and url_info.get("url"):
                    # Scrape detail page untuk dapat PDF URL
                    from ..parser.scraper import scrape_single_url
                    detail = await scrape_single_url(url_info["url"])
                    if detail:
                        pdf_url = detail[0].get("pdf_url") if detail else None

                if not pdf_url:
                    logger.warning(f"[{job_id}] Tidak ada PDF URL untuk: {url_info.get('judul', 'Unknown')}")
                    increment_failure_count()
                    continue

                # Download PDF
                logger.info(f"[{job_id}] Downloading PDF from: {pdf_url}")
                pdf_bytes = await download_pdf(pdf_url)

                # Parse PDF dari bytes
                pdf_data = await parse_pdf_from_bytes(pdf_bytes)

                # Extract structure dan keywords
                structure = extract_structure(pdf_data.get("text", ""))
                keywords = extract_keywords(pdf_data.get("text", ""))

                # Build peraturan data untuk save
                peraturan_data = {
                    "id": generate_peraturan_id(url_info),
                    **url_info,
                    "pdf_url": pdf_url,
                    "konten": pdf_data.get("text"),
                    "metadata": {
                        **pdf_data.get("metadata", {}),
                        "page_count": pdf_data.get("page_count", 0),
                        "structure": structure,
                        "keywords": keywords
                    },
                    "parsed_at": datetime.now()
                }

                # Save ke database
                await save_peraturan(peraturan_data)

                success_count += 1
                increment_success_count()
                logger.info(f"[{job_id}] Berhasil parse {idx}/{len(urls)}")

            except Exception as e:
                failed_count += 1
                increment_failure_count(str(e))
                logger.error(f"[{job_id}] Gagal parse {url_info.get('judul', 'Unknown')}: {e}")

        # 3. Update status final
        finish_parsing(success=True)
        logger.info(f"[{job_id}] Parsing selesai. Success: {success_count}, Failed: {failed_count}")

    except Exception as e:
        from ..parser.status import finish_parsing
        finish_parsing(success=False, error=str(e))
        logger.error(f"[{job_id}] Parsing gagal: {e}")


async def run_reparse_task(peraturan_id: str, job_id: str):
    """Background task untuk re-parse peraturan spesifik"""
    from ..parser.status import update_parse_status, start_parsing, finish_parsing
    from ..db.peraturan import get_peraturan_by_id, update_peraturan
    from ..parser.scraper import download_pdf
    from ..parser.pdf_parser import parse_pdf_from_bytes, extract_structure, extract_keywords

    try:
        start_parsing(job_id)

        # Get peraturan dari database
        peraturan = await get_peraturan_by_id(peraturan_id)

        logger.info(f"[{job_id}] Mulai re-parse: {peraturan['judul']}")

        # Get PDF URL
        pdf_url = peraturan.get("pdf_url") or peraturan.get("url")

        if not pdf_url:
            raise ValueError("Tidak ada PDF URL untuk peraturan ini")

        # Re-parse PDF
        update_parse_status(current_task=f"Downloading PDF: {peraturan['judul']}")
        pdf_bytes = await download_pdf(pdf_url)

        update_parse_status(current_task=f"Parsing PDF: {peraturan['judul']}")
        pdf_data = await parse_pdf_from_bytes(pdf_bytes)

        # Extract structure dan keywords
        structure = extract_structure(pdf_data.get("text", ""))
        keywords = extract_keywords(pdf_data.get("text", ""))

        # Update di database
        update_data = {
            "konten": pdf_data.get("text"),
            "metadata": {
                **pdf_data.get("metadata", {}),
                "page_count": pdf_data.get("page_count", 0),
                "structure": structure,
                "keywords": keywords
            },
            "reparse_count": peraturan.get("reparse_count", 0) + 1,
            "last_reparse_at": datetime.now(),
            "parsed_at": datetime.now()
        }

        await update_peraturan(peraturan_id, update_data)

        finish_parsing(success=True)
        logger.info(f"[{job_id}] Re-parse selesai: {peraturan['judul']}")

    except Exception as e:
        finish_parsing(success=False, error=str(e))
        logger.error(f"[{job_id}] Re-parse gagal: {e}")


def generate_peraturan_id(peraturan_info: dict) -> str:
    """Generate unique ID untuk peraturan"""
    import hashlib
    import re

    # Clean nomor untuk ID
    nomor = re.sub(r'[^a-zA-Z0-9]', '_', peraturan_info.get('nomor', ''))
    tahun = peraturan_info.get('tahun', 0)
    kategori = peraturan_info.get('kategori', 'UU')

    # Generate hash dari URL untuk uniqueness
    url_hash = hashlib.md5(peraturan_info.get('url', '').encode()).hexdigest()[:8]

    return f"{kategori}_{nomor}_{tahun}_{url_hash}".upper()


def estimate_parse_time(request: ParseRequest) -> int:
    """Estimasi waktu parsing dalam detik"""
    # Estimasi kasar:
    # - Peraturan spesifik: 30-60 detik
    # - Semua peraturan tanpa filter: 1-2 jam
    # - Dengan filter: 5-30 menit

    if request.url:
        return 60  # 1 menit untuk URL spesifik

    if request.category or request.year:
        return 600  # 10 menit untuk dengan filter

    return 3600  # 1 jam untuk semua peraturan
