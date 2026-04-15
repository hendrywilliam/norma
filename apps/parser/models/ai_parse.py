"""
Models for AI-based PDF parsing
Pydantic models for AI parsing requests and responses
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class AIParseRequest(BaseModel):
    """Request model for AI-based PDF parsing"""

    pdf_url: Optional[str] = Field(None, description="URL to PDF file")
    peraturan_id: str = Field(..., description="ID of the peraturan")
    api_key: str = Field(..., description="GLM API key")
    model: str = Field(default="GLM-4.6V", description="GLM model to use")
    concurrency: int = Field(
        default=5, ge=1, le=10, description="Number of concurrent page processing"
    )
    scale: float = Field(default=2.0, ge=1.0, le=4.0, description="Image scale factor for quality")
    use_fallback: bool = Field(
        default=True, description="Use text-based parsing if AI parsing fails"
    )


class AIParsePerPageResult(BaseModel):
    """Result for a single page from AI parsing"""

    page_number: int = Field(..., description="Page number (1-indexed)")
    bab_count: int = Field(0, description="Number of BAB found on this page")
    pasal_count: int = Field(0, description="Number of Pasal found on this page")
    ayat_count: int = Field(0, description="Number of Ayat found on this page")
    confidence: float = Field(0.0, ge=0.0, le=1.0, description="Confidence score for this page")
    raw_text: str = Field("", description="Raw text extracted from the page")
    processing_time_ms: Optional[int] = Field(None, description="Processing time in milliseconds")


class AIParseResult(BaseModel):
    """Result model for AI-based PDF parsing"""

    success: bool = Field(..., description="Whether parsing was successful")
    peraturan_id: str = Field(..., description="ID of the peraturan")
    bab_list: List[Dict[str, Any]] = Field(
        default_factory=list, description="List of BAB extracted"
    )
    pasal_list: List[Dict[str, Any]] = Field(
        default_factory=list, description="List of Pasal extracted"
    )
    ayat_list: List[Dict[str, Any]] = Field(
        default_factory=list, description="List of Ayat extracted"
    )
    full_text: str = Field("", description="Full text extracted from all pages")
    page_count: int = Field(0, description="Total number of pages processed")
    pages_processed: int = Field(0, description="Number of pages successfully processed")
    confidence: float = Field(0.0, ge=0.0, le=1.0, description="Average confidence score")
    page_results: List[AIParsePerPageResult] = Field(
        default_factory=list, description="Results per page"
    )
    processing_time_seconds: float = Field(0.0, description="Total processing time in seconds")
    used_fallback: bool = Field(False, description="Whether fallback parsing was used")
    error: Optional[str] = Field(None, description="Error message if parsing failed")

    class Config:
        from_attributes = True


class GLMConfigModel(BaseModel):
    """Configuration for GLM API"""

    api_key: str = Field(..., description="GLM API key")
    model: str = Field(default="GLM-4.6V", description="GLM model to use")
    max_tokens: int = Field(
        default=4096, ge=256, le=8192, description="Maximum tokens for response"
    )
    temperature: float = Field(
        default=0.1, ge=0.0, le=1.0, description="Temperature for response generation"
    )
    timeout: int = Field(default=120, ge=30, le=300, description="Timeout in seconds")


class AIParsingStatus(BaseModel):
    """Status model for AI parsing job"""

    job_id: str = Field(..., description="Unique job ID")
    status: str = Field(..., description="Status: queued, running, completed, failed")
    peraturan_id: str = Field(..., description="ID of the peraturan being parsed")
    progress: int = Field(0, ge=0, le=100, description="Progress percentage")
    current_page: int = Field(0, description="Current page being processed")
    total_pages: int = Field(0, description="Total pages to process")
    started_at: Optional[datetime] = Field(None, description="When parsing started")
    completed_at: Optional[datetime] = Field(None, description="When parsing completed")
    error: Optional[str] = Field(None, description="Error message if failed")
    result: Optional[AIParseResult] = Field(None, description="Parsing result if completed")

    class Config:
        from_attributes = True


class AIBatchParseRequest(BaseModel):
    """Request model for batch AI-based PDF parsing"""

    peraturan_ids: List[str] = Field(
        ..., min_length=1, description="List of peraturan IDs to parse"
    )
    model: str = Field(default="GLM-4.6V", description="GLM model to use")
    concurrency: int = Field(
        default=5, ge=1, le=10, description="Number of concurrent page processing"
    )


class AIBatchParseResult(BaseModel):
    """Result model for batch AI-based PDF parsing"""

    success: bool = Field(..., description="Whether batch parsing was successful")
    total: int = Field(..., description="Total peraturan to parse")
    successful: int = Field(0, description="Number of successful parses")
    failed: int = Field(0, description="Number of failed parses")
    results: List[AIParseResult] = Field(
        default_factory=list, description="Results for each peraturan"
    )
    processing_time_seconds: float = Field(0.0, description="Total processing time in seconds")

    class Config:
        from_attributes = True


class AyatParsedNode(BaseModel):
    """Model untuk ayat yang di-parse oleh AI"""

    nomor_ayat: str = Field(..., description="Nomor ayat ((1), (2), dst)")
    konten_ayat: str = Field(..., description="Konten ayat")
    urutan: int = Field(..., description="Urutan ayat dalam pasal")


class PasalParsedNode(BaseModel):
    """Model untuk pasal yang di-parse oleh AI"""

    nomor_pasal: str = Field(..., description="Nomor pasal")
    judul_pasal: Optional[str] = Field(None, description="Judul pasal")
    konten_pasal: str = Field(..., description="Konten pasal")
    urutan: int = Field(..., description="Urutan pasal dalam peraturan")
    ayat_list: List[AyatParsedNode] = Field(
        default_factory=list, description="List ayat dalam pasal"
    )


class BabParsedNode(BaseModel):
    """Model untuk bab yang di-parse oleh AI"""

    nomor_bab: str = Field(..., description="Nomor bab (I, II, III, dst)")
    judul_bab: Optional[str] = Field(None, description="Judul bab")
    urutan: int = Field(..., description="Urutan bab dalam peraturan")
    pasal_list: List[PasalParsedNode] = Field(
        default_factory=list, description="List pasal dalam bab"
    )


class AIParseTreeResult(BaseModel):
    """Result model for AI parsing dengan struktur tree (nested)

    Struktur tree:
    - Peraturan
      ├── bab_list: List[BabParsedNode]
      │   └── BabParsedNode
      │       └── pasal_list: List[PasalParsedNode]
      │           └── PasalParsedNode
      │               └── ayat_list: List[AyatParsedNode]
      └── pasal_tanpa_bab_list: List[PasalParsedNode]
          └── PasalParsedNode
              └── ayat_list: List[AyatParsedNode]
    """

    success: bool = Field(..., description="Whether parsing was successful")
    peraturan_id: str = Field(..., description="ID of the peraturan")
    bab_list: List[BabParsedNode] = Field(
        default_factory=list, description="List bab dengan pasal nested"
    )
    pasal_tanpa_bab_list: List[PasalParsedNode] = Field(
        default_factory=list, description="List pasal tanpa bab (standalone)"
    )
    full_text: str = Field("", description="Full text extracted from all pages")
    page_count: int = Field(0, description="Total number of pages processed")
    pages_processed: int = Field(0, description="Number of pages successfully processed")
    confidence: float = Field(0.0, ge=0.0, le=1.0, description="Average confidence score")
    processing_time_seconds: float = Field(0.0, description="Total processing time in seconds")
    used_fallback: bool = Field(False, description="Whether fallback parsing was used")
    error: Optional[str] = Field(None, description="Error message if parsing failed")

    class Config:
        from_attributes = True
