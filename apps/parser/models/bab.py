"""
Pydantic Models untuk Tabel Bab
Models untuk validation dan serialization tabel bab saja
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


# ========================================
# Models untuk Bab
# ========================================

class BabBase(BaseModel):
    """Base model untuk Bab"""

    peraturan_id: str = Field(..., description="Foreign key ke tabel peraturan")
    nomor_bab: str = Field(..., min_length=1, description="Nomor bab (I, II, III, dll)")
    judul_bab: Optional[str] = Field(None, description="Judul bab")
    urutan: int = Field(..., ge=0, description="Urutan bab dalam peraturan")


class BabCreate(BabBase):
    """Model untuk create bab baru"""

    pass


class BabUpdate(BaseModel):
    """Model untuk update bab"""

    nomor_bab: Optional[str] = Field(None, min_length=1)
    judul_bab: Optional[str] = Field(None)
    urutan: Optional[int] = Field(None, ge=0)


class BabInDB(BabBase):
    """Model untuk bab di database"""

    id: int = Field(..., description="Auto-increment ID")
    created_at: datetime = Field(default_factory=datetime.now, description="Waktu bab dibuat")
    updated_at: datetime = Field(default_factory=datetime.now, description="Waktu bab diupdate")

    class Config:
        from_attributes = True


class BabResponse(BabInDB):
    """Model untuk response API bab"""

    pass


class BabWithPasalCount(BabResponse):
    """Model untuk bab dengan count pasal"""

    total_pasal: int = Field(0, description="Total pasal dalam bab")


class BabWithPeraturanInfo(BabResponse):
    """Model untuk bab dengan info peraturan"""

    judul_peraturan: Optional[str] = Field(None, description="Judul peraturan")
    nomor_peraturan: str = Field(..., description="Nomor peraturan")
    tahun_peraturan: int = Field(..., description="Tahun peraturan")
    kategori_peraturan: str = Field(..., description="Kategori peraturan")
    jenis_peraturan: Optional[str] = Field(None, description="Jenis peraturan")


# ========================================
# Models untuk List dan Filter
# ========================================

class BabListResponse(BaseModel):
    """Model untuk list bab response"""

    total: int = Field(..., description="Total jumlah bab")
    peraturan_id: str = Field(..., description="ID peraturan")
    items: List[BabResponse] = Field(..., description="List bab")


class BabFilter(BaseModel):
    """Model untuk filter/query bab"""

    skip: int = Field(0, ge=0, description="Offset untuk pagination")
    limit: int = Field(50, ge=1, le=100, description="Limit hasil per page")
