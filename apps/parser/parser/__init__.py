"""
Parser module untuk peraturan.go.id
"""

from .scraper import scrape_peraturan, download_pdf
from .pdf_parser import parse_pdf, parse_pdf_from_url, validate_pdf, extract_peraturan_structure, extract_keywords
from .status import (
    get_parse_status,
    update_parse_status,
    start_parsing,
    finish_parsing,
    update_progress,
    increment_success_count,
    increment_failure_count,
    reset_status,
    is_parsing_running,
    get_job_id,
    get_progress
)

__all__ = [
    "scrape_peraturan",
    "download_pdf",
    "parse_pdf",
    "parse_pdf_from_url",
    "validate_pdf",
    "extract_peraturan_structure",
    "extract_keywords",
    "get_parse_status",
    "update_parse_status",
    "start_parsing",
    "finish_parsing",
    "update_progress",
    "increment_success_count",
    "increment_failure_count",
    "reset_status",
    "is_parsing_running",
    "get_job_id",
    "get_progress"
]
