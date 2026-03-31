"""
API Routes untuk Parser
API routes untuk trigger parsing, cek status, dan query peraturan, bab, pasal, ayat
"""

import os
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


class ParseRequest(BaseModel):
    url: Optional[str] = None
    category: Optional[str] = None
    year: Optional[int] = None
    force: bool = False
    model: str = "glm-4.6v"
    concurrency: int = 3


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
    """Trigger AI parsing process

    Args:
        request: Parse request dengan parameter:
        - url: URL spesifik atau kosong untuk semua peraturan
        - api_key: GLM API key (wajib)
        - model: GLM model (default: glm-4v)
        - concurrency: Concurrent page processing (default: 3)

    Flow:
        1. Scrape HTML → ambil metadata (judul, nomor, tahun, pdf_url)
        2. Download PDF dari pdf_url
        3. Convert PDF pages → Images (base64)
        4. Send to GLM-4V vision → Extract BAB, Pasal, Ayat
        5. Save to Database

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
        message=f"AI Parsing task di-queue: {request.url if request.url else 'semua peraturan'}",
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
# AI Parsing Endpoints
# ========================================


_ai_parse_jobs: Dict[str, Dict[str, Any]] = {}


@router.post("/parse/ai", response_model=ParseResponse)
async def trigger_ai_parse(
    peraturan_id: str,
    background_tasks: BackgroundTasks,
    model: str = "glm-4.6v",
    concurrency: int = 3,
):
    """Trigger AI-based PDF parsing using GLM-4V vision model

    Args:
        peraturan_id: ID peraturan yang akan di-parse
        background_tasks: FastAPI background tasks
        model: GLM model to use (glm-4v or glm-4v)
        concurrency: Number of concurrent page processing

    Returns:
        ParseResponse dengan status job
    """
    from parser.status import get_parse_status

    api_key = os.getenv("GLM_API_KEY")
    if not api_key:
        raise HTTPException(
            status_code=500,
            detail="GLM_API_KEY tidak ditemukan di environment variables",
        )

    status = get_parse_status()
    if status["is_running"]:
        raise HTTPException(status_code=400, detail="Parsing sedang berjalan. Coba lagi nanti.")

    job_id = f"ai_parse_{peraturan_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    _ai_parse_jobs[job_id] = {
        "status": "queued",
        "peraturan_id": peraturan_id,
        "started_at": None,
        "completed_at": None,
        "progress": 0,
        "current_page": 0,
        "total_pages": 0,
        "error": None,
        "result": None,
    }

    background_tasks.add_task(
        run_ai_parse_task,
        job_id=job_id,
        peraturan_id=peraturan_id,
        api_key=api_key,
        model=model,
        concurrency=concurrency,
    )

    return ParseResponse(
        status="queued",
        message=f"AI parsing task di-queue untuk peraturan {peraturan_id}",
        job_id=job_id,
        estimated_time=120,
    )


@router.post("/parse/ai/url", response_model=ParseResponse)
async def trigger_ai_parse_from_url(
    pdf_url: str,
    background_tasks: BackgroundTasks,
    judul: Optional[str] = None,
    nomor: Optional[str] = None,
    tahun: Optional[int] = None,
    kategori: str = "UU",
    model: str = "glm-4.6v",
    concurrency: int = 3,
):
    """Trigger AI-based PDF parsing from a URL directly

    Args:
        pdf_url: URL to PDF file
        background_tasks: FastAPI background tasks
        judul: Judul peraturan (optional)
        nomor: Nomor peraturan (optional)
        tahun: Tahun peraturan (optional)
        kategori: Kategori peraturan (default: UU)
        model: GLM model to use
        concurrency: Number of concurrent page processing

    Returns:
        ParseResponse dengan status job
    """
    from parser.status import get_parse_status

    api_key = os.getenv("GLM_API_KEY")
    if not api_key:
        raise HTTPException(
            status_code=500,
            detail="GLM_API_KEY tidak ditemukan di environment variables",
        )

    status = get_parse_status()
    if status["is_running"]:
        raise HTTPException(status_code=400, detail="Parsing sedang berjalan. Coba lagi nanti.")

    import hashlib

    url_hash = hashlib.md5(pdf_url.encode()).hexdigest()[:8]
    peraturan_id = f"{kategori}_{nomor or 'unknown'}_{tahun or 0}_{url_hash}".upper()

    job_id = f"ai_parse_url_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    _ai_parse_jobs[job_id] = {
        "status": "queued",
        "peraturan_id": peraturan_id,
        "started_at": None,
        "completed_at": None,
        "progress": 0,
        "current_page": 0,
        "total_pages": 0,
        "error": None,
        "result": None,
    }

    background_tasks.add_task(
        run_ai_parse_from_url_task,
        job_id=job_id,
        pdf_url=pdf_url,
        peraturan_id=peraturan_id,
        api_key=api_key,
        peraturan_info={
            "judul": judul,
            "nomor": nomor,
            "tahun": tahun,
            "kategori": kategori,
        },
        model=model,
        concurrency=concurrency,
    )

    return ParseResponse(
        status="queued",
        message=f"AI parsing task di-queue untuk PDF dari URL",
        job_id=job_id,
        estimated_time=120,
    )


@router.get("/parse/ai/status/{job_id}")
async def get_ai_parse_status(job_id: str):
    """Get status of AI parsing job

    Args:
        job_id: Job ID returned from trigger_ai_parse

    Returns:
        Dictionary with job status
    """
    if job_id not in _ai_parse_jobs:
        raise HTTPException(status_code=404, detail="Job not found")

    job = _ai_parse_jobs[job_id]

    return {
        "job_id": job_id,
        "status": job["status"],
        "peraturan_id": job["peraturan_id"],
        "progress": job["progress"],
        "current_page": job["current_page"],
        "total_pages": job["total_pages"],
        "started_at": job["started_at"],
        "completed_at": job["completed_at"],
        "error": job["error"],
        "result": job["result"],
    }


@router.get("/parse/ai/result/{job_id}")
async def get_ai_parse_result(job_id: str):
    """Get result of completed AI parsing job

    Args:
        job_id: Job ID returned from trigger_ai_parse

    Returns:
        AIParseResult with parsed structure
    """
    if job_id not in _ai_parse_jobs:
        raise HTTPException(status_code=404, detail="Job not found")

    job = _ai_parse_jobs[job_id]

    if job["status"] != "completed":
        raise HTTPException(
            status_code=400,
            detail=f"Job status is {job['status']}, not completed",
        )

    return job["result"]


async def run_ai_parse_task(
    job_id: str,
    peraturan_id: str,
    api_key: str,
    model: str,
    concurrency: int,
):
    """Background task untuk AI parsing"""
    from parser.ai_agent import parse_pdf_with_ai
    from parser.status import update_parse_status
    from repositories.peraturan import peraturan_repository
    from repositories.bab import bab_repository
    from repositories.pasal import pasal_repository
    from repositories.ayat import ayat_repository
    import time

    _ai_parse_jobs[job_id]["status"] = "running"
    _ai_parse_jobs[job_id]["started_at"] = datetime.now().isoformat()

    try:
        peraturan = await peraturan_repository.get_by_id(peraturan_id)
        if not peraturan:
            raise ValueError(f"Peraturan {peraturan_id} not found")

        pdf_url = peraturan.get("pdf_url")
        if not pdf_url:
            raise ValueError("Tidak ada PDF URL")

        update_parse_status(
            job_id=job_id, current_task=f"AI Parsing: {peraturan.get('judul', 'Unknown')}"
        )

        start_time = time.time()

        ai_result = await parse_pdf_with_ai(
            pdf_source=pdf_url,
            api_key=api_key,
            peraturan_info={
                "judul": peraturan.get("judul"),
                "nomor": peraturan.get("nomor"),
                "tahun": peraturan.get("tahun"),
                "kategori": peraturan.get("kategori"),
            },
            model=model,
            concurrency=concurrency,
        )

        _ai_parse_jobs[job_id]["total_pages"] = ai_result["page_count"]
        _ai_parse_jobs[job_id]["progress"] = 100

        processing_time = time.time() - start_time

        bab_list = []
        for bab in ai_result["bab_list"]:
            bab_list.append(
                {
                    "peraturan_id": peraturan_id,
                    "nomor_bab": bab.get("nomor_bab"),
                    "judul_bab": bab.get("judul_bab"),
                    "urutan": bab.get("urutan"),
                }
            )

        pasal_list = []
        pasal_bab_mapping = {}
        for pasal in ai_result["pasal_list"]:
            nomor_bab = pasal.get("nomor_bab")
            pasal_list.append(
                {
                    "peraturan_id": peraturan_id,
                    "nomor_pasal": pasal.get("nomor_pasal"),
                    "judul_pasal": pasal.get("judul_pasal"),
                    "konten_pasal": pasal.get("konten_pasal"),
                    "urutan": pasal.get("urutan"),
                    "nomor_bab": nomor_bab,
                }
            )
            pasal_bab_mapping[pasal.get("nomor_pasal")] = nomor_bab

        ayat_list = []
        for ayat in ai_result["ayat_list"]:
            ayat_list.append(
                {
                    "nomor_pasal": ayat.get("nomor_pasal"),
                    "nomor_ayat": ayat.get("nomor_ayat"),
                    "konten_ayat": ayat.get("konten_ayat"),
                    "urutan": ayat.get("urutan"),
                }
            )

        await bab_repository.delete_by_peraturan(peraturan_id)

        bab_id_map = {}
        for bab in bab_list:
            bab_id = await bab_repository.create(bab)
            bab_id_map[bab.get("nomor_bab")] = bab_id

        pasal_id_map = {}
        pasal_bab_id_map = {}
        for pasal in pasal_list:
            nomor_bab = pasal.get("nomor_bab")
            bab_id = bab_id_map.get(nomor_bab) if nomor_bab else None
            pasal_data = {**pasal, "bab_id": bab_id}
            pasal_id = await pasal_repository.create(pasal_data)
            pasal_id_map[pasal.get("nomor_pasal")] = pasal_id
            pasal_bab_id_map[pasal.get("nomor_pasal")] = bab_id

        for ayat in ayat_list:
            nomor_pasal = ayat.get("nomor_pasal")
            pasal_id = pasal_id_map.get(nomor_pasal)
            if pasal_id is None and pasal_id_map:
                pasal_id = list(pasal_id_map.values())[0]

            bab_id = pasal_bab_id_map.get(nomor_pasal)

            ayat_data = {
                "pasal_id": pasal_id,
                "bab_id": bab_id,
                "peraturan_id": peraturan_id,
                "nomor_ayat": ayat.get("nomor_ayat"),
                "konten_ayat": ayat.get("konten_ayat"),
                "urutan": ayat.get("urutan"),
            }
            await ayat_repository.create(ayat_data)
            pasal_id_map[pasal.get("nomor_pasal")] = pasal_id
            pasal_bab_id_map[pasal.get("nomor_pasal")] = bab_id

        for ayat in ayat_list:
            nomor_pasal = ayat.get("nomor_pasal")
            pasal_id = pasal_id_map.get(nomor_pasal)
            if pasal_id is None and pasal_id_map:
                pasal_id = list(pasal_id_map.values())[0]

            bab_id = pasal_bab_id_map.get(nomor_pasal)

            ayat_data = {
                "pasal_id": pasal_id,
                "bab_id": bab_id,
                "peraturan_id": peraturan_id,
                "nomor_ayat": ayat.get("nomor_ayat"),
                "konten_ayat": ayat.get("konten_ayat"),
                "urutan": ayat.get("urutan"),
            }
            await ayat_repository.create(ayat_data)

        await peraturan_repository.update(
            peraturan_id,
            {
                "parsed_at": datetime.now(),
                "metadata": {
                    **peraturan.get("metadata", {}),
                    "bab_count": len(bab_list),
                    "pasal_count": len(pasal_list),
                    "ayat_count": len(ayat_list),
                    "ai_confidence": ai_result.get("confidence", 0),
                    "processing_time_seconds": processing_time,
                    "ai_model": model,
                },
            },
        )

        _ai_parse_jobs[job_id]["status"] = "completed"
        _ai_parse_jobs[job_id]["completed_at"] = datetime.now().isoformat()
        _ai_parse_jobs[job_id]["result"] = {
            "success": True,
            "peraturan_id": peraturan_id,
            "bab_count": len(bab_list),
            "pasal_count": len(pasal_list),
            "ayat_count": len(ayat_list),
            "confidence": ai_result.get("confidence", 0),
            "processing_time_seconds": processing_time,
        }

        update_parse_status(
            job_id=job_id,
            is_running=False,
            last_success=datetime.now(),
            total_parsed=1,
        )

        logger.info(f"[{job_id}] AI parsing completed: {peraturan.get('judul')}")

    except Exception as e:
        _ai_parse_jobs[job_id]["status"] = "failed"
        _ai_parse_jobs[job_id]["error"] = str(e)
        _ai_parse_jobs[job_id]["completed_at"] = datetime.now().isoformat()
        logger.error(f"[{job_id}] AI parsing failed: {e}")


async def run_ai_parse_from_url_task(
    job_id: str,
    pdf_url: str,
    peraturan_id: str,
    api_key: str,
    peraturan_info: Dict[str, Any],
    model: str,
    concurrency: int,
):
    """Background task untuk AI parsing from URL"""
    from parser.ai_agent import parse_pdf_with_ai
    from parser.status import update_parse_status
    import time

    _ai_parse_jobs[job_id]["status"] = "running"
    _ai_parse_jobs[job_id]["started_at"] = datetime.now().isoformat()

    try:
        update_parse_status(job_id=job_id, current_task=f"AI Parsing: {pdf_url}")

        start_time = time.time()

        ai_result = await parse_pdf_with_ai(
            pdf_source=pdf_url,
            api_key=api_key,
            peraturan_info=peraturan_info,
            model=model,
            concurrency=concurrency,
        )

        processing_time = time.time() - start_time

        _ai_parse_jobs[job_id]["status"] = "completed"
        _ai_parse_jobs[job_id]["completed_at"] = datetime.now().isoformat()
        _ai_parse_jobs[job_id]["total_pages"] = ai_result["page_count"]
        _ai_parse_jobs[job_id]["progress"] = 100
        _ai_parse_jobs[job_id]["result"] = {
            "success": True,
            "peraturan_id": peraturan_id,
            "bab_list": ai_result["bab_list"],
            "pasal_list": ai_result["pasal_list"],
            "ayat_list": ai_result["ayat_list"],
            "full_text": ai_result["full_text"],
            "page_count": ai_result["page_count"],
            "confidence": ai_result["confidence"],
            "processing_time_seconds": processing_time,
        }

        update_parse_status(
            job_id=job_id,
            is_running=False,
            last_success=datetime.now(),
            total_parsed=1,
        )

        logger.info(f"[{job_id}] AI parsing from URL completed")

    except Exception as e:
        _ai_parse_jobs[job_id]["status"] = "failed"
        _ai_parse_jobs[job_id]["error"] = str(e)
        _ai_parse_jobs[job_id]["completed_at"] = datetime.now().isoformat()
        logger.error(f"[{job_id}] AI parsing from URL failed: {e}")


# ========================================
# Helper Functions untuk Parsing
# ========================================


async def run_parse_task(request: ParseRequest, job_id: str):
    """Background task untuk menjalankan AI parsing dengan GLM-4V"""
    from parser.status import (
        start_parsing,
        update_parse_status,
        update_progress,
        finish_parsing,
    )
    from parser.scraper import scrape_peraturan
    from parser.ai_agent import parse_pdf_with_ai
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

        # Get API key from environment
        api_key = os.getenv("GLM_API_KEY")
        if not api_key:
            raise ValueError("GLM_API_KEY tidak ditemukan di environment variables")

        # 1. Scrape URLs dari peraturan.go.id
        urls = await scrape_peraturan(url=request.url, category=request.category, year=request.year)

        logger.info(f"[{job_id}] Ditemukan {len(urls)} URL untuk di-parse")
        update_parse_status(job_id=job_id, total_items=len(urls))

        if not urls:
            logger.warning(f"[{job_id}] Tidak ada URL ditemukan")
            finish_parsing(job_id=job_id, success=True)
            return

        # 2. Download dan parse setiap PDF dengan AI
        success_count = 0
        failed_count = 0

        for idx, url_info in enumerate(urls, 1):
            try:
                update_parse_status(
                    job_id=job_id,
                    current_task=f"Parsing {idx}/{len(urls)}: {url_info.get('judul', 'Unknown')}",
                )

                pdf_url = url_info.get("pdf_url")
                if not pdf_url:
                    logger.warning(f"[{job_id}] Tidak ada PDF URL untuk {url_info.get('judul')}")
                    failed_count += 1
                    continue

                # Format data peraturan dari scraper
                peraturan_data = {"id": generate_peraturan_id(url_info), **url_info}
                peraturan_id = peraturan_data["id"]

                logger.info(f"[{job_id}] Mengdownload PDF: {pdf_url}")

                # AI-based parsing with GLM-4V
                ai_result = await parse_pdf_with_ai(
                    pdf_source=pdf_url,
                    api_key=api_key,
                    peraturan_info={
                        "judul": url_info.get("judul"),
                        "nomor": url_info.get("nomor"),
                        "tahun": url_info.get("tahun"),
                        "kategori": url_info.get("kategori"),
                    },
                    model=request.model,
                    concurrency=request.concurrency,
                )

                # Prepare data for database
                bab_list = [
                    {
                        "peraturan_id": peraturan_id,
                        "nomor_bab": bab.get("nomor_bab"),
                        "judul_bab": bab.get("judul_bab"),
                        "urutan": bab.get("urutan"),
                    }
                    for bab in ai_result.get("bab_list", [])
                ]

                pasal_list = []
                for pasal in ai_result.get("pasal_list", []):
                    pasal_list.append(
                        {
                            "peraturan_id": peraturan_id,
                            "nomor_pasal": pasal.get("nomor_pasal"),
                            "judul_pasal": pasal.get("judul_pasal"),
                            "konten_pasal": pasal.get("konten_pasal"),
                            "urutan": pasal.get("urutan"),
                            "nomor_bab": pasal.get("nomor_bab"),
                        }
                    )

                ayat_list = [
                    {
                        "nomor_pasal": ayat.get("nomor_pasal"),
                        "nomor_ayat": ayat.get("nomor_ayat"),
                        "konten_ayat": ayat.get("konten_ayat"),
                        "urutan": ayat.get("urutan"),
                    }
                    for ayat in ai_result.get("ayat_list", [])
                ]

                peraturan_final = {
                    **peraturan_data,
                    "parsed_at": datetime.now(),
                    "metadata": {
                        "bab_count": len(bab_list),
                        "pasal_count": len(pasal_list),
                        "ayat_count": len(ayat_list),
                        "page_count": ai_result.get("page_count", 0),
                        "ai_confidence": ai_result.get("confidence", 0),
                        "pages_processed": ai_result.get("pages_processed", 0),
                        "ai_model": request.model,
                    },
                }

                await peraturan_repository.create(peraturan_final)

                await bab_repository.delete_by_peraturan(peraturan_id)

                bab_id_map = {}
                for bab in bab_list:
                    bab_id = await bab_repository.create(bab)
                    bab_id_map[bab.get("nomor_bab")] = bab_id

                pasal_id_map = {}
                pasal_bab_id_map = {}
                for pasal in pasal_list:
                    nomor_bab = pasal.get("nomor_bab")
                    bab_id = bab_id_map.get(nomor_bab) if nomor_bab else None
                    pasal_data = {**pasal, "bab_id": bab_id}
                    pasal_id = await pasal_repository.create(pasal_data)
                    pasal_id_map[pasal.get("nomor_pasal")] = pasal_id
                    pasal_bab_id_map[pasal.get("nomor_pasal")] = bab_id

                for ayat in ayat_list:
                    nomor_pasal = ayat.get("nomor_pasal")
                    pasal_id = pasal_id_map.get(nomor_pasal)
                    if pasal_id is None and pasal_id_map:
                        pasal_id = list(pasal_id_map.values())[0]

                    bab_id = pasal_bab_id_map.get(nomor_pasal)

                    ayat_data = {
                        "pasal_id": pasal_id,
                        "bab_id": bab_id,
                        "peraturan_id": peraturan_id,
                        "nomor_ayat": ayat.get("nomor_ayat"),
                        "konten_ayat": ayat.get("konten_ayat"),
                        "urutan": ayat.get("urutan"),
                    }
                    await ayat_repository.create(ayat_data)

                success_count += 1
                update_progress(job_id=job_id, current=idx, total=len(urls))

                logger.info(
                    f"[{job_id}] Berhasil parse {idx}/{len(urls)}: "
                    f"{len(bab_list)} BAB, {len(pasal_list)} Pasal, {len(ayat_list)} Ayat"
                )

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
