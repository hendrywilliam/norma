"""
Pydantic Models untuk Tabel Ayat
Models untuk validation dan serialization tabel ayat saja
"""

from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Dict, Any
from datetime import datetime


# ========================================
# Models untuk Ayat
# ========================================

class AyatBase(BaseModel):
    """Base model untuk Ayat"""

    pasal_id: int = Field(..., description="Foreign key ke tabel pasals")
    nomor_ayat: str = Field(..., min_length=1, description="Nomor ayat ((1), (2), (3), dll)")
    konten_ayat: str = Field(..., min_length=1, description="Konten ayat")
    urutan: int = Field(..., ge=0, description="Urutan ayat dalam pasal")


class AyatCreate(AyatBase):
    """Model untuk create ayat baru"""

    metadata: Optional[Dict[str, Any]] = Field(None, description="Metadata tambahan")


class AyatUpdate(BaseModel):
    """Model untuk update ayat"""

    nomor_ayat: Optional[str] = Field(None, min_length=1)
    konten_ayat: Optional[str] = Field(None, min_length=1)
    urutan: Optional[int] = Field(None, ge=0)
    metadata: Optional[Dict[str, Any]] = None


class AyatInDB(AyatBase):
    """Model untuk ayat di database"""

    id: int = Field(..., description="Auto-increment ID")
    metadata: Optional[Dict[str, Any]] = None
    created_at: datetime = Field(default_factory=datetime.now, description="Waktu ayat dibuat")
    updated_at: datetime = Field(default_factory=datetime.now, description="Waktu ayat diupdate")

    class Config:
        from_attributes = True


class AyatResponse(AyatInDB):
    """Model untuk response API ayat"""

    pass


class AyatWithPasalInfo(AyatResponse):
    """Model untuk ayat dengan info pasal"""

    nomor_pasal: str = Field(..., description="Nomor pasal")
    judul_pasal: Optional[str] = Field(None, description="Judul pasal")
    pasal_urutan: Optional[int] = Field(None, description="Urutan pasal")


class AyatWithBabInfo(AyatResponse):
    """Model untuk ayat dengan info bab"""

    nomor_bab: Optional[str] = Field(None, description="Nomor bab")
    judul_bab: Optional[str] = Field(None, description="Judul bab")
    bab_urutan: Optional[int] = Field(None, description="Urutan bab")


class AyatWithPasalBabPeraturan(AyatResponse):
    """Model untuk ayat dengan info pasal, bab, dan peraturan"""

    nomor_pasal: str = Field(..., description="Nomor pasal")
    judul_pasal: Optional[str] = Field(None, description="Judul pasal")
    pasal_urutan: Optional[int] = Field(None, description="Urutan pasal")
    nomor_bab: Optional[str] = Field(None, description="Nomor bab")
    judul_bab: Optional[str] = Field(None, description="Judul bab")
    bab_urutan: Optional[int] = Field(None, description="Urutan bab")
    pasal_id: Optional[int] = Field(None, description="ID pasal (dari query)")
    peraturan_id: str = Field(..., description="ID peraturan")
    judul_peraturan: Optional[str] = Field(None, description="Judul peraturan")
    nomor_peraturan: str = Field(..., description="Nomor peraturan")
    tahun_peraturan: int = Field(..., description="Tahun peraturan")
    kategori_peraturan: str = Field(..., description="Kategori peraturan")
    jenis_peraturan: Optional[str] = Field(None, description="Jenis peraturan")
    tentang: Optional[str] = Field(None, description="Topik peraturan")


# ========================================
# Models untuk List dan Filter
# ========================================

class AyatListResponse(BaseModel):
    """Model untuk list ayat response"""

    total: int = Field(..., description="Total jumlah ayat")
    pasal_id: int = Field(..., description="ID pasal")
    items: List[AyatResponse] = Field(..., description="List ayat")


class AyatFilter(BaseModel):
    """Model untuk filter/query ayat"""

    skip: int = Field(0, ge=0, description="Offset untuk pagination")
    limit: int = Field(50, ge=1, le=100, description="Limit hasil per page")
    search: Optional[str] = Field(None, description="Search string di nomor/konten")
    sort_by: Optional[str] = Field(None, description="Field untuk sorting")
    sort_order: str = Field("desc", pattern="^(asc|desc)$", description="Urutan sorting")

    @field_validator('sort_by')
    @classmethod
    def validate_sort_by(cls, v):
        """Validasi field yang bisa di-sort"""
        if v:
            sort_fields = ['nomor_ayat', 'konten_ayat', 'urutan', 'created_at', 'updated_at']
            if v not in sort_fields:
                raise ValueError(f'Sort by harus salah dari: {", ".join(sort_fields)}')
        return v
