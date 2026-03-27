"""
API Routes untuk Parser
API routes untuk trigger parsing, cek status, dan query peraturan, bab, pasal, ayat
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime
import logging

# Import models dari folder models/ yang sudah dipisah
from models.peraturan import (
    PeraturanBase,
    PeraturanCreate,
    PeraturanUpdate,
    PeraturanInDB,
    PeraturanResponse,
    PeraturanSummary,
    PeraturanFilter,
    PeraturanListResponse,
    PeraturanDetail,
    PeraturanMetadata,
    ParseResult,
    PeraturanFullResponse as PeraturanFullResponseModel,
)
from models.bab import (
    BabBase,
    BabCreate,
    BabUpdate,
    BabInDB,
    BabResponse,
    BabWithPasalCount,
    BabListResponse,
    BabFilter,
)
from models.pasal import (
    PasalBase,
    PasalCreate,
    PasalUpdate,
    PasalInDB,
    PasalResponse,
    PasalWithAyatCount,
    PasalWithBabPeraturan,
    PasalListResponse,
    PasalFilter,
)
from models.ayat import (
    AyatBase,
    AyatCreate,
    AyatUpdate,
    AyatInDB,
    AyatResponse,
    AyatWithPasalBabPeraturan,
    AyatListResponse,
    AyatFilter,
)

logger = logging.getLogger(__name__)

# Initialize router
router = APIRouter(tags=["Parser API"])

# ========================================
# ========================================
# Request/Response Models untuk Parsing (Local ke routes)
# ========================================


class ParseRequest(BaseModel):
    url: Optional[str] = None
    category: Optional[str] = None
    year: Optional[int] = None
    force: bool = False


class ParseResponse(BaseModel):
    status: str
    message: str
    job_id: Optional[str] = None
    estimated_time: Optional[int] = None


class HealthResponse(BaseModel):
    status: str
    timestamp: datetime
    version: str


class StatusResponse(BaseModel):
    is_running: bool
    last_run: Optional[datetime]
    last_success: Optional[datetime]
    total_parsed: int
    total_failed: int
    error: Optional[str]
    current_task: Optional[str] = None
    progress: int = 0
    total_items: int = 0
    processed_items: int = 0


# PeraturanFullResponse yang extend dari model di peraturan.py
class PeraturanFullResponse(PeraturanFullResponseModel):
    bab_list: List[BabWithPasalCount] = []
    pasal_list: List[PasalWithAyatCount] = []
    ayat_list: List[AyatResponse] = []


# ========================================
# Health & Status Endpoints
# ========================================


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint untuk monitoring"""
    return HealthResponse(status="healthy", timestamp=datetime.now(), version="0.1.0")


@router.get("/status", response_model=StatusResponse)
async def get_status():
    """Get status parsing terakhir"""
    from parser.status import get_parse_status

    status_data = get_parse_status()
    return StatusResponse(**status_data)


# ========================================
# Parsing Endpoints
# ========================================


@router.post("/parse", response_model=ParseResponse)
async def trigger_parse(request: ParseRequest, background_tasks: BackgroundTasks):
    """Trigger parsing process

    Args:
        request: Parse request dengan parameter filter
        background_tasks: FastAPI background tasks untuk async execution

    Returns:
        ParseResponse dengan status job
    """
    from parser.status import get_parse_status

    # Cek apakah parsing sedang berjalan
    status = get_parse_status()
    if status["is_running"] and not request.force:
        raise HTTPException(
            status_code=400, detail="Parsing sedang berjalan. Gunakan force=true untuk override."
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
        estimated_time=estimated_time,
    )


# ========================================
# Peraturan Endpoints (Read-only untuk Parser)
# ========================================


@router.get("/peraturan", response_model=List[PeraturanSummary])
async def list_peraturan(
    skip: int = 0,
    limit: int = 20,
    category: Optional[str] = None,
    year: Optional[int] = None,
    jenis: Optional[str] = None,
    status: Optional[str] = None,
    search: Optional[str] = None,
):
    """List semua peraturan di database dengan filter

    Args:
        skip: Offset untuk pagination
        limit: Limit hasil per page
        category: Filter kategori
        year: Filter tahun
        jenis: Filter jenis peraturan
        status: Filter status peraturan
        search: Search string di judul/nomor

    Returns:
        List dari peraturan summary
    """
    from repositories.peraturan import peraturan_repository

    peraturan = await peraturan_repository.get_list(
        skip=skip,
        limit=limit,
        category=category,
        year=year,
        jenis=jenis,
        status=status,
        search=search,
    )

    return peraturan["items"]


@router.get("/peraturan/{peraturan_id}")
async def get_peraturan_detail(peraturan_id: str):
    """Get detail peraturan spesifik dengan count bab, pasal, ayat

    Args:
        peraturan_id: ID peraturan

    Returns:
        Detail peraturan lengkap dengan count bab, pasal, ayat
    """
    from repositories.peraturan import peraturan_repository

    peraturan = await peraturan_repository.get_by_id(peraturan_id)

    if not peraturan:
        raise HTTPException(status_code=404, detail="Peraturan tidak ditemukan")

    return peraturan


@router.get("/peraturan/{peraturan_id}/full", response_model=PeraturanFullResponse)
async def get_peraturan_full(peraturan_id: str):
    """Get peraturan lengkap dengan semua bab, pasals, dan ayats

    Args:
        peraturan_id: ID peraturan

    Returns:
        PeraturanFullResponse dengan peraturan, bab_list, pasal_list, ayat_list
    """
    from repositories.peraturan import peraturan_repository
    from repositories.bab import bab_repository
    from repositories.pasal import pasal_repository
    from repositories.ayat import ayat_repository

    peraturan = await peraturan_repository.get_by_id(peraturan_id)
    if not peraturan:
        raise HTTPException(status_code=404, detail="Peraturan tidak ditemukan")

    bab_result = await bab_repository.get_list(peraturan_id)
    pasal_result = await pasal_repository.get_list(peraturan_id)
    ayat_result = await ayat_repository.get_list_by_peraturan(peraturan_id)

    result = {
        "peraturan": peraturan,
        "bab_list": bab_result.get("items", []),
        "pasal_list": pasal_result.get("items", []),
        "ayat_list": ayat_result,
    }

    if not result:
        raise HTTPException(status_code=404, detail="Peraturan tidak ditemukan")

    return PeraturanFullResponse(
        peraturan=PeraturanDetail(**result["peraturan"]),
        bab_list=[BabWithPasalCount(**bab) for bab in result.get("bab_list", [])],
        pasal_list=[PasalWithAyatCount(**pasal) for pasal in result.get("pasal_list", [])],
        ayat_list=[AyatResponse(**ayat) for ayat in result.get("ayat_list", [])],
    )


@router.post("/peraturan/{peraturan_id}/reparse")
async def reparse_peraturan(peraturan_id: str, background_tasks: BackgroundTasks):
    """Trigger re-parse untuk peraturan spesifik

    Args:
        peraturan_id: ID peraturan untuk di-reparse

    Returns:
        ParseResponse dengan status job
    """
    from repositories.peraturan import peraturan_repository

    # Cek apakah peraturan ada
    peraturan = await peraturan_repository.get_by_id(peraturan_id)
    if not peraturan:
        raise HTTPException(status_code=404, detail="Peraturan tidak ditemukan")

    job_id = f"reparse_{peraturan_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    # Add background task untuk re-parse
    background_tasks.add_task(run_reparse_task, peraturan_id, job_id)

    return ParseResponse(
        status="queued",
        message=f"Re-parse task di-queue: {peraturan['judul']}",
        job_id=job_id,
        estimated_time=60,  # Estimasi 1 menit untuk re-parse
    )


@router.delete("/peraturan/{peraturan_id}")
async def delete_peraturan(peraturan_id: str):
    """Hapus peraturan dan semua data terkait (bab, pasal, ayat)

    Args:
        peraturan_id: ID peraturan yang akan dihapus

    Returns:
        Dictionary dengan status penghapusan
    """
    from repositories.peraturan import peraturan_repository
    from repositories.bab import bab_repository
    from repositories.pasal import pasal_repository
    from repositories.ayat import ayat_repository

    # Cek apakah peraturan ada
    peraturan = await peraturan_repository.get_by_id(peraturan_id)
    if not peraturan:
        raise HTTPException(status_code=404, detail="Peraturan tidak ditemukan")

    # Hapus semua ayat terkait pasal milik peraturan ini
    # Note: Karena ada foreign key CASCADE, hapus peraturan akan otomatis hapus bab, pasal, ayat
    # Tapi kita hapus manual untuk memastikan

    try:
        # Get all pasal for this peraturan
        pasal_list = await pasal_repository.get_list(peraturan_id, skip=0, limit=10000)
        pasal_ids = [p["id"] for p in pasal_list.get("items", [])]

        # Delete ayats for each pasal
        for pasal_id in pasal_ids:
            # Delete ayats (manual delete for each pasal)
            # Note: Ayat table has CASCADE delete from Pasal
            pass  # CASCADE will handle this

        # Delete all bab (CASCADE will delete pasal, which cascade to ayat)
        deleted_bab = await bab_repository.delete_by_peraturan(peraturan_id)
        logger.info(f"Deleted {deleted_bab} bab for peraturan {peraturan_id}")

        # Delete peraturan (CASCADE akan hapus sisa data)
        deleted = await peraturan_repository.delete(peraturan_id)

        if deleted:
            logger.info(f"Peraturan {peraturan_id} deleted successfully")
            return {
                "status": "success",
                "message": f"Peraturan '{peraturan.get('judul', peraturan_id)}' berhasil dihapus",
                "deleted_peraturan_id": peraturan_id,
                "deleted_bab_count": deleted_bab,
            }
        else:
            raise HTTPException(status_code=500, detail="Gagal menghapus peraturan")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting peraturan {peraturan_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Error menghapus peraturan: {str(e)}")


# ========================================
# Bab Endpoints (Read-only)
# ========================================


@router.get("/peraturan/{peraturan_id}/bab", response_model=List[BabResponse])
async def list_bab(peraturan_id: str, skip: int = 0, limit: int = 50):
    """List semua bab untuk peraturan spesifik dengan pagination

    Args:
        peraturan_id: ID peraturan
        skip: Offset untuk pagination
        limit: Limit hasil per page

    Returns:
        List dari bab untuk peraturan
    """
    from repositories.bab import bab_repository

    bab_result = await bab_repository.get_list(peraturan_id=peraturan_id, skip=skip, limit=limit)

    return bab_result["items"]


@router.get("/peraturan/{peraturan_id}/bab/{bab_id}", response_model=BabResponse)
async def get_bab_detail(bab_id: int):
    """Get detail bab spesifik

    Args:
        bab_id: ID bab

    Returns:
        Detail bab lengkap
    """
    from repositories.bab import bab_repository

    bab = await bab_repository.get_by_id(bab_id)

    if not bab:
        raise HTTPException(status_code=404, detail="Bab tidak ditemukan")

    return bab


@router.get("/peraturan/{peraturan_id}/bab/{bab_id}/pasals", response_model=List[PasalResponse])
async def list_pasal_by_bab(peraturan_id: str, bab_id: int, skip: int = 0, limit: int = 50):
    """List semua pasal dalam bab spesifik dengan pagination

    Args:
        peraturan_id: ID peraturan
        bab_id: ID bab
        skip: Offset untuk pagination
        limit: Limit hasil per page

    Returns:
        List dari pasal dalam bab
    """
    from repositories.pasal import pasal_repository

    pasal_result = await pasal_repository.get_list(
        peraturan_id=peraturan_id, bab_id=bab_id, skip=skip, limit=limit
    )

    return pasal_result["items"]


# ========================================
# Pasal Endpoints (Read-only)
# ========================================


@router.get("/peraturan/{peraturan_id}/pasals", response_model=List[PasalWithBabPeraturan])
async def list_pasal(
    peraturan_id: str, bab_id: Optional[int] = None, skip: int = 0, limit: int = 50
):
    """List semua pasal untuk peraturan spesifik (atau dalam bab spesifik) dengan pagination

    Args:
        peraturan_id: ID peraturan
        bab_id: Optional ID bab untuk filter
        skip: Offset untuk pagination
        limit: Limit hasil per page

    Returns:
        List dari pasal dengan info bab dan peraturan
    """
    from repositories.pasal import pasal_repository

    pasal_result = await pasal_repository.get_list(
        peraturan_id=peraturan_id, bab_id=bab_id, skip=skip, limit=limit
    )

    return pasal_result["items"]


@router.get("/peraturan/{peraturan_id}/pasals/{pasal_id}", response_model=PasalWithAyatCount)
async def get_pasal_detail(peraturan_id: str, pasal_id: int):
    """Get detail pasal spesifik dengan count ayat

    Args:
        peraturan_id: ID peraturan
        pasal_id: ID pasal

    Returns:
        Detail pasal lengkap dengan count ayat
    """
    from repositories.pasal import pasal_repository

    pasal = await pasal_repository.get_by_id(pasal_id)

    if not pasal:
        raise HTTPException(status_code=404, detail="Pasal tidak ditemukan")

    return PasalWithAyatCount(**pasal)


@router.get("/peraturan/{peraturan_id}/pasals/{pasal_id}/ayats", response_model=List[AyatResponse])
async def list_ayat_by_pasal(peraturan_id: str, pasal_id: int, skip: int = 0, limit: int = 50):
    """List semua ayat dalam pasal spesifik dengan pagination

    Args:
        peraturan_id: ID peraturan
        pasal_id: ID pasal
        skip: Offset untuk pagination
        limit: Limit hasil per page

    Returns:
        List dari ayat dalam pasal
    """
    from repositories.ayat import ayat_repository

    items = await ayat_repository.get_list_by_pasal(pasal_id=pasal_id, skip=skip, limit=limit)

    return items if items else []


# ========================================
# Helper Functions untuk Parsing
# ========================================


async def run_parse_task(request: ParseRequest, job_id: str):
    """Background task untuk menjalankan parsing"""
    from parser.status import (
        start_parsing,
        update_parse_status,
        update_progress,
        increment_success_count,
        increment_failure_count,
        finish_parsing,
    )
    from parser.scraper import scrape_peraturan
    from parser.pdf_parser import parse_peraturan_complete, format_peraturan_data_for_db
    from repositories.peraturan import peraturan_repository
    from repositories.bab import bab_repository
    from repositories.pasal import pasal_repository
    from repositories.ayat import ayat_repository

    try:
        start_parsing(job_id)
        update_parse_status(job_id=job_id, current_task="Scraping URLs")
        logger.info(
            f"[{job_id}] Mulai parsing: {request.url if request.url else 'semua peraturan'}"
        )

        # 1. Scrape URLs dari peraturan.go.id
        urls = await scrape_peraturan(url=request.url, category=request.category, year=request.year)

        logger.info(f"[{job_id}] Ditemukan {len(urls)} URL untuk di-parse")
        update_parse_status(job_id=job_id, total_items=len(urls))

        if not urls:
            logger.warning(f"[{job_id}] Tidak ada URL ditemukan")
            finish_parsing(job_id=job_id, success=True)
            return

        # 2. Download dan parse setiap PDF
        success_count = 0
        failed_count = 0

        for idx, url_info in enumerate(urls, 1):
            try:
                update_parse_status(
                    job_id=job_id,
                    current_task=f"Parsing {idx}/{len(urls)}: {url_info.get('judul', 'Unknown')}",
                )

                # Format data peraturan dari scraper
                peraturan_data = {"id": generate_peraturan_id(url_info), **url_info}

                # Download dan parse PDF
                pdf_result = await parse_peraturan_complete(
                    pdf_source=url_info.get("pdf_url"), peraturan_id=peraturan_data["id"]
                )

                # Format data untuk database
                peraturan_final, bab_list, pasal_list, ayat_list = format_peraturan_data_for_db(
                    peraturan_data=peraturan_data,
                    bab_data=pdf_result["bab"],
                    pasal_data=pdf_result["pasal"],
                    ayat_data=pdf_result["ayat"],
                )

                # Save peraturan
                await peraturan_repository.create(peraturan_final)

                # Save bab
                for bab in bab_list:
                    await bab_repository.create(bab)

                # Save pasal
                for pasal in pasal_list:
                    await pasal_repository.create(pasal)

                # Save ayat
                for ayat in ayat_list:
                    await ayat_repository.create(ayat)

                # Update parsed_at di peraturan
                await peraturan_repository.update(
                    peraturan_data["id"],
                    {
                        "parsed_at": datetime.now(),
                        "metadata": {
                            "bab_count": len(bab_list),
                            "pasal_count": len(pasal_list),
                            "ayat_count": len(ayat_list),
                            "parse_duration": pdf_result.get("metadata", {}).get(
                                "duration_seconds"
                            ),
                            "page_count": pdf_result.get("metadata", {}).get("page_count"),
                        },
                    },
                )

                success_count += 1
                update_progress(job_id=job_id, current=idx, total=len(urls))

                logger.info(f"[{job_id}] Berhasil parse {idx}/{len(urls)}")

            except Exception as e:
                failed_count += 1
                logger.error(f"[{job_id}] Gagal parse {url_info.get('judul', 'Unknown')}: {e}")

        # 3. Update status final
        update_parse_status(
            job_id=job_id,
            is_running=False,
            last_success=datetime.now(),
            total_parsed=success_count,
            total_failed=failed_count,
            current_task=None,
        )

        logger.info(f"[{job_id}] Parsing selesai. Success: {success_count}, Failed: {failed_count}")

    except Exception as e:
        from parser.status import finish_parsing

        finish_parsing(job_id=job_id, success=False, error=str(e))
        logger.error(f"[{job_id}] Parsing gagal: {e}")


async def run_reparse_task(peraturan_id: str, job_id: str):
    """Background task untuk re-parse peraturan spesifik"""
    from parser.status import update_parse_status, finish_parsing
    from repositories.peraturan import peraturan_repository
    from repositories.bab import bab_repository
    from repositories.pasal import pasal_repository
    from repositories.ayat import ayat_repository
    from parser.pdf_parser import parse_peraturan_complete, format_peraturan_data_for_db

    try:
        update_parse_status(job_id=job_id, is_running=True)

        # Get peraturan dari database
        peraturan = await peraturan_repository.get_by_id(peraturan_id)

        logger.info(f"[{job_id}] Mulai re-parse: {peraturan['judul']}")

        # Get PDF URL
        pdf_url = peraturan.get("pdf_url")
        if not pdf_url:
            raise ValueError("Tidak ada PDF URL")

        # Re-parse PDF
        update_parse_status(job_id=job_id, current_task=f"Re-parsing: {peraturan['judul']}")

        pdf_result = await parse_peraturan_complete(pdf_source=pdf_url, peraturan_id=peraturan_id)

        # Format data untuk database
        # Hanya update bab, pasals, ayats (jangan update peraturan info)
        bab_list = pdf_result["bab"]
        pasal_list = pdf_result["pasal"]
        ayat_list = pdf_result["ayat"]

        # Delete old bab, pasals, ayats for this peraturan
        await bab_repository.delete_by_peraturan(peraturan_id)

        # Re-save ke database (akan update existing bab, pasals, ayats)
        for bab in bab_list:
            await bab_repository.create(bab)

        for pasal in pasal_list:
            await pasal_repository.create(pasal)

        for ayat in ayat_list:
            await ayat_repository.create(ayat)

        # Update reparse count dan last reparse
        await peraturan_repository.update(
            peraturan_id,
            {
                "reparse_count": peraturan.get("reparse_count", 0) + 1,
                "last_reparse_at": datetime.now(),
                "parsed_at": datetime.now(),
                "metadata": {
                    **peraturan.get("metadata", {}),
                    "bab_count": len(bab_list),
                    "pasal_count": len(pasal_list),
                    "ayat_count": len(ayat_list),
                    "reparse_duration": pdf_result.get("metadata", {}).get("duration_seconds"),
                },
            },
        )

        update_parse_status(
            job_id=job_id, is_running=False, last_success=datetime.now(), total_parsed=1
        )

        logger.info(f"[{job_id}] Re-parse selesai: {peraturan['judul']}")

    except Exception as e:
        finish_parsing(job_id=job_id, success=False, error=str(e))
        logger.error(f"[{job_id}] Re-parse gagal: {e}")


def generate_peraturan_id(peraturan_info: dict) -> str:
    """Generate unique ID untuk peraturan"""
    import hashlib
    import re

    # Clean nomor untuk ID
    nomor = re.sub(r"[^a-zA-Z0-9]", "_", peraturan_info.get("nomor", ""))
    tahun = peraturan_info.get("tahun", 0)
    kategori = peraturan_info.get("kategori", "UU")

    # Generate hash dari URL untuk uniqueness
    url = peraturan_info.get("url", "")
    url_hash = hashlib.md5(url.encode()).hexdigest()[:8]

    return f"{kategori}_{nomor}_{tahun}_{url_hash}".upper()


def estimate_parse_time(request: ParseRequest) -> int:
    """Estimasi waktu parsing dalam detik"""
    if request.url:
        return 60  # 1 menit untuk URL spesifik

    if request.category or request.year:
        return 600  # 10 menit untuk dengan filter

    return 3600  # 1 jam untuk semua peraturan
