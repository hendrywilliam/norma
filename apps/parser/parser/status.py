"""
Status Management untuk Parsing Jobs
Track status parsing yang sedang berjalan atau sudah selesai
"""

from typing import Dict, Optional
from datetime import datetime
from threading import Lock
import logging

logger = logging.getLogger(__name__)

# Global status storage (in-memory, bisa diganti dengan Redis/Database nanti)
_parse_status: Dict = {
    "is_running": False,
    "job_id": None,
    "current_task": None,
    "last_run": None,
    "last_success": None,
    "total_parsed": 0,
    "total_failed": 0,
    "error": None,
    "progress": 0,
    "total_items": 0,
    "processed_items": 0,
}

# Thread lock untuk concurrent access
_status_lock = Lock()


def get_parse_status() -> Dict:
    """
    Get status parsing terakhir

    Returns:
        Dictionary berisi status parsing
    """
    with _status_lock:
        return _parse_status.copy()


def update_parse_status(
    is_running: Optional[bool] = None,
    job_id: Optional[str] = None,
    current_task: Optional[str] = None,
    last_run: Optional[datetime] = None,
    last_success: Optional[datetime] = None,
    total_parsed: Optional[int] = None,
    total_failed: Optional[int] = None,
    error: Optional[str] = None,
    progress: Optional[int] = None,
    total_items: Optional[int] = None,
    processed_items: Optional[int] = None,
) -> None:
    """
    Update status parsing

    Args:
        is_running: Status apakah parsing sedang berjalan
        job_id: ID dari job yang sedang berjalan
        current_task: Task yang sedang dijalankan
        last_run: Waktu terakhir parsing dijalankan
        last_success: Waktu terakhir parsing berhasil
        total_parsed: Total peraturan yang berhasil diparse
        total_failed: Total peraturan yang gagal diparse
        error: Error message jika parsing gagal
        progress: Progress percentage (0-100)
        total_items: Total items yang akan diparse
        processed_items: Total items yang sudah diparse
    """
    with _status_lock:
        if is_running is not None:
            _parse_status["is_running"] = is_running

        if job_id is not None:
            _parse_status["job_id"] = job_id

        if current_task is not None:
            _parse_status["current_task"] = current_task

        if last_run is not None:
            _parse_status["last_run"] = last_run

        if last_success is not None:
            _parse_status["last_success"] = last_success

        if total_parsed is not None:
            _parse_status["total_parsed"] = total_parsed

        if total_failed is not None:
            _parse_status["total_failed"] = total_failed

        if error is not None:
            _parse_status["error"] = error

        if progress is not None:
            _parse_status["progress"] = progress

        if total_items is not None:
            _parse_status["total_items"] = total_items

        if processed_items is not None:
            _parse_status["processed_items"] = processed_items

    logger.debug(f"Status updated: {get_parse_status()}")


def start_parsing(job_id: str, total_items: int = 0) -> None:
    """
    Mulai tracking untuk parsing job baru

    Args:
        job_id: ID dari parsing job
        total_items: Total items yang akan diparse
    """
    update_parse_status(
        is_running=True,
        job_id=job_id,
        last_run=datetime.now(),
        error=None,
        progress=0,
        total_items=total_items,
        processed_items=0,
        current_task="Initializing",
    )

    logger.info(f"Started parsing job {job_id} with {total_items} items")


def finish_parsing(
    job_id: Optional[str] = None, success: bool = True, error: Optional[str] = None
) -> None:
    """
    Selesaikan parsing job

    Args:
        job_id: ID dari parsing job
        success: Apakah parsing berhasil
        error: Error message jika gagal
    """
    if success:
        update_parse_status(
            job_id=job_id,
            is_running=False,
            last_success=datetime.now(),
            progress=100,
            current_task=None,
            error=None,
        )
        logger.info("Parsing job finished successfully")
    else:
        update_parse_status(job_id=job_id, is_running=False, error=error, current_task=None)
        logger.error(f"Parsing job failed: {error}")


def update_progress(
    job_id: Optional[str] = None, current: int = 0, total: int = 0, task: Optional[str] = None
) -> None:
    """
    Update progress parsing

    Args:
        job_id: ID dari parsing job
        current: Jumlah item yang sudah diparse
        total: Total item yang akan diparse
        task: Task yang sedang dijalankan
    """
    progress = int((current / total) * 100) if total > 0 else 0

    update_parse_status(
        job_id=job_id,
        progress=progress,
        processed_items=current,
        total_items=total,
        current_task=task,
    )

    logger.debug(f"[{job_id}] Progress: {progress}% ({current}/{total}) - {task}")


def increment_success_count() -> None:
    """Increment counter peraturan yang berhasil diparse"""
    with _status_lock:
        _parse_status["total_parsed"] += 1

    logger.debug(f"Success count: {_parse_status['total_parsed']}")


def increment_failure_count(error: Optional[str] = None) -> None:
    """
    Increment counter peraturan yang gagal diparse

    Args:
        error: Error message
    """
    with _status_lock:
        _parse_status["total_failed"] += 1
        if error:
            logger.error(f"Parse failed: {error}")

    logger.debug(f"Failure count: {_parse_status['total_failed']}")


def reset_status() -> None:
    """Reset status parsing ke nilai awal"""
    with _status_lock:
        _parse_status.update(
            {
                "is_running": False,
                "job_id": None,
                "current_task": None,
                "last_run": None,
                "last_success": None,
                "total_parsed": 0,
                "total_failed": 0,
                "error": None,
                "progress": 0,
                "total_items": 0,
                "processed_items": 0,
            }
        )

    logger.info("Parsing status reset")


def is_parsing_running() -> bool:
    """
    Cek apakah parsing sedang berjalan

    Returns:
        True jika parsing sedang berjalan
    """
    with _status_lock:
        return _parse_status["is_running"]


def get_job_id() -> Optional[str]:
    """
    Get ID dari job yang sedang berjalan

    Returns:
        Job ID atau None jika tidak ada job yang berjalan
    """
    with _status_lock:
        return _parse_status["job_id"]


def get_progress() -> Dict[str, int]:
    """
    Get progress parsing

    Returns:
        Dictionary dengan progress, processed_items, dan total_items
    """
    with _status_lock:
        return {
            "progress": _parse_status["progress"],
            "processed_items": _parse_status["processed_items"],
            "total_items": _parse_status["total_items"],
        }
