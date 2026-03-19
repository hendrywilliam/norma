"""
Pydantic Models untuk Tabel Pasal
Models untuk validation dan serialization tabel pasal saja
"""

from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Dict, Any
from datetime import datetime


# ========================================
# Models untuk Pasal
# ========================================

class PasalBase(BaseModel):
    """Base model untuk Pasal"""

    peraturan_id: str = Field(..., description="Foreign key ke tabel peraturan")
    bab_id: Optional[int] = Field(None, description="Foreign key ke tabel bab")
    nomor_pasal: str = Field(..., min_length=1, description="Nomor pasal (Pasal 1, Pasal 2, dll)")
    judul_pasal: Optional[str] = Field(None, description="Judul pasal")
    konten_pasal: str = Field(..., min_length=1, description="Konten lengkap pasal")
    urutan: int = Field(..., ge=0, description="Urutan pasal dalam peraturan")


class PasalCreate(PasalBase):
    """Model untuk create pasal baru"""

    metadata: Optional[Dict[str, Any]] = Field(None, description="Metadata tambahan")


class PasalUpdate(BaseModel):
    """Model untuk update pasal"""

    bab_id: Optional[int] = Field(None)
    nomor_pasal: Optional[str] = Field(None, min_length=1)
    judul_pasal: Optional[str] = Field(None)
    konten_pasal: Optional[str] = Field(None, min_length=1)
    urutan: Optional[int] = Field(None, ge=0)
    metadata: Optional[Dict[str, Any]] = None


class PasalInDB(PasalBase):
    """Model untuk pasal di database"""

    id: int = Field(..., description="Auto-increment ID")
    metadata: Optional[Dict[str, Any]] = None
    created_at: datetime = Field(default_factory=datetime.now, description="Waktu pasal dibuat")
    updated_at: datetime = Field(default_factory=datetime.now, description="Waktu pasal diupdate")

    class Config:
        from_attributes = True


class PasalResponse(PasalInDB):
    """Model untuk response API pasal"""

    pass


class PasalWithAyatCount(PasalResponse):
    """Model untuk pasal dengan count ayat"""

    total_ayat: int = Field(0, description="Total ayat dalam pasal")


class PasalWithBabPeraturan(PasalResponse):
    """Model untuk pasal dengan info bab dan peraturan"""

    nomor_bab: Optional[str] = Field(None, description="Nomor bab")
    judul_bab: Optional[str] = Field(None, description="Judul bab")
    bab_urutan: Optional[int] = Field(None, description="Urutan bab")
    judul_peraturan: Optional[str] = Field(None, description="Judul peraturan")
    nomor_peraturan: str = Field(..., description="Nomor peraturan")
    tahun_peraturan: int = Field(..., description="Tahun peraturan")
    kategori_peraturan: str = Field(..., description="Kategori peraturan")
    jenis_peraturan: Optional[str] = Field(None, description="Jenis peraturan")
    tentang: Optional[str] = Field(None, description="Topik peraturan")
    total_ayat: int = Field(0, description="Total ayat dalam pasal")
    daftar_ayat: List[str] = Field(default_factory=list, description="List nomor ayat")


# ========================================
# Models untuk List dan Filter
# ========================================

class PasalListResponse(BaseModel):
    """Model untuk list pasal response"""

    total: int = Field(..., description="Total jumlah pasal")
    peraturan_id: str = Field(..., description="ID peraturan")
    bab_id: Optional[int] = Field(None, description="Filter by bab_id")
    items: List[PasalResponse] = Field(..., description="List pasal")


class PasalFilter(BaseModel):
    """Model untuk filter/query pasal"""

    bab_id: Optional[int] = Field(None, description="Filter by bab_id")
    skip: int = Field(0, ge=0, description="Offset untuk pagination")
    limit: int = Field(50, ge=1, le=100, description="Limit hasil per page")
    search: Optional[str] = Field(None, description="Search string di nomor/judul/konten")
    sort_by: Optional[str] = Field(None, description="Field untuk sorting")
    sort_order: str = Field("desc", pattern="^(asc|desc)$", description="Urutan sorting")

    @field_validator('sort_by')
    @classmethod
    def validate_sort_by(cls, v):
        """Validasi field yang bisa di-sort"""
        if v:
            sort_fields = ['nomor_pasal', 'judul_pasal', 'konten_pasal', 'urutan', 'created_at', 'updated_at']
            if v not in sort_fields:
                raise ValueError(f'Sort by harus salah dari: {", ".join(sort_fields)}')
        return v
