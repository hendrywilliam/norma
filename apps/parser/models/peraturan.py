"""
Data Models for Peraturan
Pydantic models for peraturan table validation and serialization only
"""

from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Dict, Any
from datetime import datetime


class PeraturanBase(BaseModel):
    """Base model for Peraturan"""

    judul: Optional[str] = Field(None, min_length=1, description="Peraturan title")
    nomor: str = Field(..., min_length=1, description="Peraturan number")
    tahun: int = Field(..., gt=1900, lt=2100, description="Peraturan year")
    kategori: str = Field(
        ..., min_length=1, description="Peraturan category (UU, PP, Perpres, etc.)"
    )
    url: str = Field(..., min_length=1, description="Source URL from peraturan.go.id")
    pdf_url: Optional[str] = Field(None, description="Peraturan PDF URL")
    jenis_peraturan: Optional[str] = Field(None, description="Full peraturan type")
    pemrakarsa: Optional[str] = Field(None, description="Peraturan sponsor")
    tentang: Optional[str] = Field(None, description="Peraturan topic/title")
    tempat_penetapan: Optional[str] = Field(None, description="Place peraturan was enacted")
    tanggal_ditetapkan: Optional[datetime] = Field(None, description="Date peraturan was enacted")
    pejabat_menetapkan: Optional[str] = Field(None, description="Official who enacted the peraturan")
    status_peraturan: Optional[str] = Field("Berlaku", description="Peraturan status")
    jumlah_dilihat: Optional[int] = Field(0, ge=0, description="View count")
    jumlah_download: Optional[int] = Field(0, ge=0, description="Download count")
    tanggal_disahkan: Optional[datetime] = Field(None, description="Date peraturan was ratified")
    tanggal_diundangkan: Optional[datetime] = Field(
        None, description="Date peraturan was promulgated"
    )
    deskripsi: Optional[str] = Field(None, description="Brief peraturan description")

    @field_validator("kategori")
    @classmethod
    def validate_kategori(cls, v):
        """Validate peraturan category"""
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
            raise ValueError(f"Category must be one of: {', '.join(kategori_valid)}")
        return v

    @field_validator("url", "pdf_url")
    @classmethod
    def validate_url(cls, v):
        """Validate URL format"""
        if v and not (v.startswith("http://") or v.startswith("https://")):
            raise ValueError("URL must start with http:// or https://")
        return v


class PeraturanCreate(PeraturanBase):
    """Model for creating new peraturan"""

    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")


class PeraturanUpdate(BaseModel):
    """Model for updating peraturan"""

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
    """Model for peraturan in database"""

    id: str = Field(..., description="Unique peraturan ID")
    metadata: Optional[Dict[str, Any]] = None
    created_at: datetime = Field(default_factory=datetime.now, description="Time record was created")
    updated_at: datetime = Field(default_factory=datetime.now, description="Time record was updated")
    parsed_at: Optional[datetime] = Field(None, description="Last parsing time")
    reparse_count: int = Field(0, description="Number of times peraturan was re-parsed")
    last_reparse_at: Optional[datetime] = Field(None, description="Last reparse time")

    class Config:
        from_attributes = True  # For ORM mode


class PeraturanResponse(PeraturanInDB):
    """Model for API response"""

    pass


class PeraturanSummary(BaseModel):
    """Model for peraturan summary (without full content)"""

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
    """Model for peraturan detail with bab, pasal, ayat counts"""

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
    """Model for peraturan filter/query"""

    category: Optional[str] = Field(None, description="Filter by category")
    year: Optional[int] = Field(None, description="Filter by year")
    jenis: Optional[str] = Field(None, description="Filter by peraturan type")
    status: Optional[str] = Field(None, description="Filter by peraturan status")
    search: Optional[str] = Field(None, description="Search string in title/number")
    skip: int = Field(0, ge=0, description="Offset for pagination")
    limit: int = Field(20, ge=1, le=100, description="Result limit per page")
    sort_by: Optional[str] = Field(None, description="Field for sorting")
    sort_order: str = Field("desc", pattern="^(asc|desc)$", description="Sort order")

    @field_validator("sort_by")
    @classmethod
    def validate_sort_by(cls, v):
        """Validate sortable fields"""
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
                raise ValueError(f"Sort by must be one of: {', '.join(sort_fields)}")
        return v


class PeraturanListResponse(BaseModel):
    """Model for peraturan list response"""

    total: int = Field(..., description="Total peraturan count")
    skip: int = Field(..., description="Offset for pagination")
    limit: int = Field(..., description="Result limit per page")
    items: List[PeraturanResponse] = Field(..., description="List of peraturan")


class PeraturanMetadata(BaseModel):
    """Model for peraturan metadata from PDF"""

    page_count: int = Field(0, description="Total PDF pages")
    char_count: int = Field(0, description="Total content characters")
    bab_count: int = Field(0, description="Total bab extracted")
    pasal_count: int = Field(0, description="Total pasal extracted")
    ayat_count: int = Field(0, description="Total ayat extracted")
    keywords: List[str] = Field(default_factory=list, description="Extracted keywords")

    class Config:
        from_attributes = True


class ParseResult(BaseModel):
    """Model for PDF parsing result"""

    success: bool = Field(..., description="Whether parsing succeeded")
    peraturan_id: Optional[str] = Field(None, description="ID of parsed peraturan")
    error: Optional[str] = Field(None, description="Error message if failed")
    parsed_data: Optional[Dict[str, Any]] = Field(None, description="Parsed data")
    metadata: Optional[PeraturanMetadata] = Field(None, description="Parsing metadata")

    class Config:
        from_attributes = True


class PeraturanFullResponse(BaseModel):
    """Model for full peraturan response with bab, pasal, and ayat"""

    peraturan: PeraturanDetail
    bab_count: int = Field(0, description="Total bab")
    pasal_count: int = Field(0, description="Total pasal")
    ayat_count: int = Field(0, description="Total ayat")
    # Note: Lists are extended in routes.py for full response with nested items


class AyatNode(BaseModel):
    """Model for ayat in tree structure"""

    id: int = Field(..., description="Ayat ID")
    nomor_ayat: str = Field(..., description="Ayat number")
    konten_ayat: str = Field(..., description="Ayat content")
    urutan: int = Field(..., description="Ayat order")

    class Config:
        from_attributes = True


class PasalNode(BaseModel):
    """Model for pasal in tree structure"""

    id: int = Field(..., description="Pasal ID")
    nomor_pasal: str = Field(..., description="Pasal number")
    judul_pasal: Optional[str] = Field(None, description="Pasal title")
    konten_pasal: str = Field(..., description="Pasal content")
    urutan: int = Field(..., description="Pasal order")
    ayat_list: List["AyatNode"] = Field(default_factory=list, description="List of ayat in pasal")

    class Config:
        from_attributes = True


class BabNode(BaseModel):
    """Model for bab in tree structure"""

    id: int = Field(..., description="Bab ID")
    nomor_bab: str = Field(..., description="Bab number")
    judul_bab: Optional[str] = Field(None, description="Bab title")
    urutan: int = Field(..., description="Bab order")
    pasal_list: List["PasalNode"] = Field(default_factory=list, description="List of pasal in bab")

    class Config:
        from_attributes = True


class PeraturanTreeResponse(BaseModel):
    """Model for peraturan response with tree structure (nested)

    Tree structure:
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
        default_factory=list, description="List of bab with nested pasal"
    )
    pasal_tanpa_bab_list: List[PasalNode] = Field(
        default_factory=list, description="List of pasal without bab (standalone)"
    )

    class Config:
        from_attributes = True
