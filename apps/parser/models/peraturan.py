"""
Data Models untuk Peraturan
Pydantic models untuk validation dan serialization
"""

from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Dict, Any
from datetime import datetime


class PeraturanBase(BaseModel):
    """Base model untuk Peraturan"""

    judul: str = Field(..., min_length=1, description="Judul peraturan")
    nomor: str = Field(..., min_length=1, description="Nomor peraturan")
    tahun: int = Field(..., gt=1900, lt=2100, description="Tahun peraturan")
    kategori: str = Field(..., min_length=1, description="Kategori peraturan (UU, PP, Perpres, dll)")
    url: str = Field(..., min_length=1, description="URL sumber dari peraturan.go.id")
    pdf_url: Optional[str] = Field(None, description="URL PDF peraturan")
    tanggal_disahkan: Optional[datetime] = Field(None, description="Tanggal peraturan disahkan")
    tanggal_diundangkan: Optional[datetime] = Field(None, description="Tanggal peraturan diundangkan")
    deskripsi: Optional[str] = Field(None, description="Deskripsi singkat peraturan")

    @field_validator('kategori')
    @classmethod
    def validate_kategori(cls, v):
        """Validasi kategori peraturan"""
        kategori_valid = ['UU', 'PP', 'Perpres', 'Permen', 'Perpuu', 'Tap MPR', 'UU MD3',
                         'PPA', 'Perbup', 'Perwal', 'Perda', 'Perwali', 'Lainnya']
        if v not in kategori_valid:
            raise ValueError(f'Kategori harus salah dari: {", ".join(kategori_valid)}')
        return v

    @field_validator('url', 'pdf_url')
    @classmethod
    def validate_url(cls, v):
        """Validasi URL format"""
        if v and not (v.startswith('http://') or v.startswith('https://')):
            raise ValueError('URL harus dimulai dengan http:// atau https://')
        return v


class PeraturanCreate(PeraturanBase):
    """Model untuk create peraturan baru"""

    konten: Optional[str] = Field(None, description="Konten lengkap dari PDF")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Metadata tambahan")


class PeraturanUpdate(BaseModel):
    """Model untuk update peraturan"""

    judul: Optional[str] = Field(None, min_length=1)
    nomor: Optional[str] = Field(None, min_length=1)
    tahun: Optional[int] = Field(None, gt=1900, lt=2100)
    kategori: Optional[str] = Field(None, min_length=1)
    url: Optional[str] = Field(None, min_length=1)
    pdf_url: Optional[str] = Field(None)
    tanggal_disahkan: Optional[datetime] = None
    tanggal_diundangkan: Optional[datetime] = None
    deskripsi: Optional[str] = None
    konten: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class PeraturanInDB(PeraturanBase):
    """Model untuk peraturan di database"""

    id: str = Field(..., description="Unique ID peraturan")
    konten: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    created_at: datetime = Field(default_factory=datetime.now, description="Waktu record dibuat")
    updated_at: datetime = Field(default_factory=datetime.now, description="Waktu record diupdate")
    parsed_at: Optional[datetime] = Field(None, description="Waktu parsing terakhir")
    reparse_count: int = Field(0, description="Berapa kali peraturan di-reparse")
    last_reparse_at: Optional[datetime] = Field(None, description="Waktu terakhir reparse")

    class Config:
        from_attributes = True  # Untuk ORM mode


class PeraturanResponse(PeraturanInDB):
    """Model untuk response API"""

    pass


class PeraturanListResponse(BaseModel):
    """Model untuk list peraturan response"""

    total: int = Field(..., description="Total jumlah peraturan")
    skip: int = Field(..., description="Offset untuk pagination")
    limit: int = Field(..., description="Limit hasil per page")
    items: List[PeraturanResponse] = Field(..., description="List peraturan")


class PeraturanFilter(BaseModel):
    """Model untuk filter/query peraturan"""

    category: Optional[str] = Field(None, description="Filter kategori")
    year: Optional[int] = Field(None, description="Filter tahun")
    search: Optional[str] = Field(None, description="Search string di judul/nomor")
    skip: int = Field(0, ge=0, description="Offset untuk pagination")
    limit: int = Field(20, ge=1, le=100, description="Limit hasil per page")
    sort_by: Optional[str] = Field(None, description="Field untuk sorting")
    sort_order: str = Field("desc", pattern="^(asc|desc)$", description="Urutan sorting")

    @field_validator('sort_by')
    @classmethod
    def validate_sort_by(cls, v):
        """Validasi field yang bisa di-sort"""
        if v:
            sort_fields = ['judul', 'nomor', 'tahun', 'kategori', 'created_at', 'updated_at']
            if v not in sort_fields:
                raise ValueError(f'Sort by harus salah dari: {", ".join(sort_fields)}')
        return v


class PeraturanSummary(BaseModel):
    """Model untuk summary peraturan (tanpa konten lengkap)"""

    id: str
    judul: str
    nomor: str
    tahun: int
    kategori: str
    tanggal_disahkan: Optional[datetime]
    url: str
    created_at: datetime

    class Config:
        from_attributes = True


class PeraturanMetadata(BaseModel):
    """Model untuk metadata peraturan dari PDF"""

    page_count: int = Field(0, description="Total halaman PDF")
    char_count: int = Field(0, description="Total karakter konten")
    structure: Dict[str, List[str]] = Field(default_factory=dict, description="Struktur peraturan (bab, pasal, ayat)")
    keywords: List[str] = Field(default_factory=list, description="Keywords yang diekstrak")

    class Config:
        from_attributes = True


class ParseResult(BaseModel):
    """Model untuk hasil parsing PDF"""

    success: bool = Field(..., description="Apakah parsing berhasil")
    peraturan_id: Optional[str] = Field(None, description="ID peraturan yang diparse")
    error: Optional[str] = Field(None, description="Error message jika gagal")
    parsed_data: Optional[Dict[str, Any]] = Field(None, description="Data hasil parsing")

    class Config:
        from_attributes = True
