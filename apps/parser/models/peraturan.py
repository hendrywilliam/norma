"""
Data Models untuk Peraturan
Pydantic models untuk validation dan serialization tabel peraturan saja
"""

from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Dict, Any
from datetime import datetime


class PeraturanBase(BaseModel):
    """Base model untuk Peraturan"""

    judul: Optional[str] = Field(None, min_length=1, description="Judul peraturan")
    nomor: str = Field(..., min_length=1, description="Nomor peraturan")
    tahun: int = Field(..., gt=1900, lt=2100, description="Tahun peraturan")
    kategori: str = Field(
        ..., min_length=1, description="Kategori peraturan (UU, PP, Perpres, dll)"
    )
    url: str = Field(..., min_length=1, description="URL sumber dari peraturan.go.id")
    pdf_url: Optional[str] = Field(None, description="URL PDF peraturan")
    jenis_peraturan: Optional[str] = Field(None, description="Jenis peraturan lengkap")
    pemrakarsa: Optional[str] = Field(None, description="Pemrakarsa peraturan")
    tentang: Optional[str] = Field(None, description="Topik/judul peraturan")
    tempat_penetapan: Optional[str] = Field(None, description="Tempat peraturan ditetapkan")
    tanggal_ditetapkan: Optional[datetime] = Field(None, description="Tanggal peraturan ditetapkan")
    pejabat_menetapkan: Optional[str] = Field(None, description="Pejabat yang menetapkan peraturan")
    status_peraturan: Optional[str] = Field("Berlaku", description="Status peraturan")
    jumlah_dilihat: Optional[int] = Field(0, ge=0, description="Jumlah dilihat")
    jumlah_download: Optional[int] = Field(0, ge=0, description="Jumlah didownload")
    tanggal_disahkan: Optional[datetime] = Field(None, description="Tanggal peraturan disahkan")
    tanggal_diundangkan: Optional[datetime] = Field(
        None, description="Tanggal peraturan diundangkan"
    )
    deskripsi: Optional[str] = Field(None, description="Deskripsi singkat peraturan")

    @field_validator("kategori")
    @classmethod
    def validate_kategori(cls, v):
        """Validasi kategori peraturan"""
        kategori_valid = [
            "UU",
            "PP",
            "Perpres",
            "Permen",
            "Perpuu",
            "Tap MPR",
            "UU MD3",
            "PPA",
            "Perbup",
            "Perwal",
            "Perda",
            "Perwali",
            "Lainnya",
        ]
        if v not in kategori_valid:
            raise ValueError(f"Kategori harus salah dari: {', '.join(kategori_valid)}")
        return v

    @field_validator("url", "pdf_url")
    @classmethod
    def validate_url(cls, v):
        """Validasi URL format"""
        if v and not (v.startswith("http://") or v.startswith("https://")):
            raise ValueError("URL harus dimulai dengan http:// atau https://")
        return v


class PeraturanCreate(PeraturanBase):
    """Model untuk create peraturan baru"""

    metadata: Optional[Dict[str, Any]] = Field(None, description="Metadata tambahan")


class PeraturanUpdate(BaseModel):
    """Model untuk update peraturan"""

    judul: Optional[str] = Field(None, min_length=1)
    nomor: Optional[str] = Field(None, min_length=1)
    tahun: Optional[int] = Field(None, gt=1900, lt=2100)
    kategori: Optional[str] = Field(None, min_length=1)
    url: Optional[str] = Field(None, min_length=1)
    pdf_url: Optional[str] = Field(None)
    jenis_peraturan: Optional[str] = Field(None)
    pemrakarsa: Optional[str] = Field(None)
    tentang: Optional[str] = Field(None)
    tempat_penetapan: Optional[str] = Field(None)
    tanggal_ditetapkan: Optional[datetime] = None
    pejabat_menetapkan: Optional[str] = Field(None)
    status_peraturan: Optional[str] = Field(None)
    jumlah_dilihat: Optional[int] = Field(None, ge=0)
    jumlah_download: Optional[int] = Field(None, ge=0)
    tanggal_disahkan: Optional[datetime] = None
    tanggal_diundangkan: Optional[datetime] = None
    deskripsi: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class PeraturanInDB(PeraturanBase):
    """Model untuk peraturan di database"""

    id: str = Field(..., description="Unique ID peraturan")
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


class PeraturanSummary(BaseModel):
    """Model untuk summary peraturan (tanpa konten lengkap)"""

    id: str
    judul: Optional[str]
    nomor: str
    tahun: int
    kategori: str
    jenis_peraturan: Optional[str]
    tentang: Optional[str]
    status_peraturan: Optional[str]
    url: str
    pdf_url: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class PeraturanDetail(BaseModel):
    """Model untuk detail peraturan dengan count bab, pasal, ayat"""

    id: str
    judul: Optional[str]
    nomor: str
    tahun: int
    kategori: str
    jenis_peraturan: Optional[str]
    tentang: Optional[str]
    status_peraturan: Optional[str]
    url: str
    pdf_url: Optional[str]
    created_at: datetime
    updated_at: datetime
    parsed_at: Optional[datetime]
    reparse_count: int
    total_bab: int = 0
    total_pasal: int = 0
    total_ayat: int = 0

    class Config:
        from_attributes = True


class PeraturanFilter(BaseModel):
    """Model untuk filter/query peraturan"""

    category: Optional[str] = Field(None, description="Filter kategori")
    year: Optional[int] = Field(None, description="Filter tahun")
    jenis: Optional[str] = Field(None, description="Filter jenis peraturan")
    status: Optional[str] = Field(None, description="Filter status peraturan")
    search: Optional[str] = Field(None, description="Search string di judul/nomor")
    skip: int = Field(0, ge=0, description="Offset untuk pagination")
    limit: int = Field(20, ge=1, le=100, description="Limit hasil per page")
    sort_by: Optional[str] = Field(None, description="Field untuk sorting")
    sort_order: str = Field("desc", pattern="^(asc|desc)$", description="Urutan sorting")

    @field_validator("sort_by")
    @classmethod
    def validate_sort_by(cls, v):
        """Validasi field yang bisa di-sort"""
        if v:
            sort_fields = [
                "judul",
                "nomor",
                "tahun",
                "kategori",
                "created_at",
                "updated_at",
                "parsed_at",
            ]
            if v not in sort_fields:
                raise ValueError(f"Sort by harus salah dari: {', '.join(sort_fields)}")
        return v


class PeraturanListResponse(BaseModel):
    """Model untuk list peraturan response"""

    total: int = Field(..., description="Total jumlah peraturan")
    skip: int = Field(..., description="Offset untuk pagination")
    limit: int = Field(..., description="Limit hasil per page")
    items: List[PeraturanResponse] = Field(..., description="List peraturan")


class PeraturanMetadata(BaseModel):
    """Model untuk metadata peraturan dari PDF"""

    page_count: int = Field(0, description="Total halaman PDF")
    char_count: int = Field(0, description="Total karakter konten")
    bab_count: int = Field(0, description="Total bab yang diekstrak")
    pasal_count: int = Field(0, description="Total pasal yang diekstrak")
    ayat_count: int = Field(0, description="Total ayat yang diekstrak")
    keywords: List[str] = Field(default_factory=list, description="Keywords yang diekstrak")

    class Config:
        from_attributes = True


class ParseResult(BaseModel):
    """Model untuk hasil parsing PDF"""

    success: bool = Field(..., description="Apakah parsing berhasil")
    peraturan_id: Optional[str] = Field(None, description="ID peraturan yang diparse")
    error: Optional[str] = Field(None, description="Error message jika gagal")
    parsed_data: Optional[Dict[str, Any]] = Field(None, description="Data hasil parsing")
    metadata: Optional[PeraturanMetadata] = Field(None, description="Metadata parsing")

    class Config:
        from_attributes = True


class PeraturanFullResponse(BaseModel):
    """Model untuk response peraturan lengkap dengan bab, pasal, dan ayat"""

    peraturan: PeraturanDetail
    bab_count: int = Field(0, description="Total bab")
    pasal_count: int = Field(0, description="Total pasal")
    ayat_count: int = Field(0, description="Total ayat")
    # Note: Lists are extended in routes.py for full response with nested items


class AyatNode(BaseModel):
    """Model untuk ayat dalam struktur tree"""

    id: int = Field(..., description="ID ayat")
    nomor_ayat: str = Field(..., description="Nomor ayat")
    konten_ayat: str = Field(..., description="Konten ayat")
    urutan: int = Field(..., description="Urutan ayat")

    class Config:
        from_attributes = True


class PasalNode(BaseModel):
    """Model untuk pasal dalam struktur tree"""

    id: int = Field(..., description="ID pasal")
    nomor_pasal: str = Field(..., description="Nomor pasal")
    judul_pasal: Optional[str] = Field(None, description="Judul pasal")
    konten_pasal: str = Field(..., description="Konten pasal")
    urutan: int = Field(..., description="Urutan pasal")
    ayat_list: List["AyatNode"] = Field(default_factory=list, description="List ayat dalam pasal")

    class Config:
        from_attributes = True


class BabNode(BaseModel):
    """Model untuk bab dalam struktur tree"""

    id: int = Field(..., description="ID bab")
    nomor_bab: str = Field(..., description="Nomor bab")
    judul_bab: Optional[str] = Field(None, description="Judul bab")
    urutan: int = Field(..., description="Urutan bab")
    pasal_list: List["PasalNode"] = Field(default_factory=list, description="List pasal dalam bab")

    class Config:
        from_attributes = True


class PeraturanTreeResponse(BaseModel):
    """Model untuk response peraturan dengan struktur tree (nested)

    Struktur tree:
    - Peraturan
      ├── bab_list: List[BabNode]
      │   └── BabNode
      │       └── pasal_list: List[PasalNode]
      │           └── PasalNode
      │               └── ayat_list: List[AyatNode]
      └── pasal_tanpa_bab_list: List[PasalNode]
          └── PasalNode
              └── ayat_list: List[AyatNode]
    """

    peraturan: PeraturanDetail
    bab_list: List[BabNode] = Field(
        default_factory=list, description="List bab dengan pasal nested"
    )
    pasal_tanpa_bab_list: List[PasalNode] = Field(
        default_factory=list, description="List pasal tanpa bab (standalone)"
    )

    class Config:
        from_attributes = True
