"""
Pydantic Models for Pasal Table
Models for pasal table validation and serialization only
"""

from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Dict, Any
from datetime import datetime


# ========================================
# Models for Pasal
# ========================================


class PasalBase(BaseModel):
    """Base model for Pasal"""

    peraturan_id: str = Field(..., description="Foreign key to peraturan table")
    bab_id: Optional[int] = Field(None, description="Foreign key to bab table")
    nomor_pasal: str = Field(..., min_length=1, description="Pasal number (Pasal 1, Pasal 2, etc.)")
    judul_pasal: Optional[str] = Field(None, description="Pasal title")
    konten_pasal: str = Field(..., min_length=1, description="Full pasal content")
    urutan: int = Field(..., ge=0, description="Pasal order within peraturan")


class PasalCreate(PasalBase):
    """Model for creating new pasal"""

    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")


class PasalUpdate(BaseModel):
    """Model for updating pasal"""

    bab_id: Optional[int] = Field(None)
    nomor_pasal: Optional[str] = Field(None, min_length=1)
    judul_pasal: Optional[str] = Field(None)
    konten_pasal: Optional[str] = Field(None, min_length=1)
    urutan: Optional[int] = Field(None, ge=0)
    metadata: Optional[Dict[str, Any]] = None


class PasalInDB(PasalBase):
    """Model for pasal in database"""

    id: int = Field(..., description="Auto-increment ID")
    metadata: Optional[Dict[str, Any]] = None
    created_at: datetime = Field(default_factory=datetime.now, description="Time pasal was created")
    updated_at: datetime = Field(default_factory=datetime.now, description="Time pasal was updated")

    class Config:
        from_attributes = True


class PasalResponse(PasalInDB):
    """Model for pasal API response"""

    pass


class PasalWithAyatCount(PasalResponse):
    """Model for pasal with ayat count"""

    total_ayat: int = Field(0, description="Total ayat in pasal")


class PasalWithBabPeraturan(PasalResponse):
    """Model for pasal with bab and peraturan info"""

    nomor_bab: Optional[str] = Field(None, description="Bab number")
    judul_bab: Optional[str] = Field(None, description="Bab title")
    bab_urutan: Optional[int] = Field(None, description="Bab order")
    judul_peraturan: Optional[str] = Field(None, description="Peraturan title")
    nomor_peraturan: str = Field(..., description="Peraturan number")
    tahun_peraturan: int = Field(..., description="Peraturan year")
    kategori_peraturan: str = Field(..., description="Peraturan category")
    jenis_peraturan: Optional[str] = Field(None, description="Peraturan type")
    tentang: Optional[str] = Field(None, description="Peraturan topic")
    total_ayat: int = Field(0, description="Total ayat in pasal")
    daftar_ayat: List[str] = Field(default_factory=list, description="List of ayat numbers")


# ========================================
# Models for List and Filter
# ========================================


class PasalListResponse(BaseModel):
    """Model for pasal list response"""

    total: int = Field(..., description="Total pasal count")
    peraturan_id: str = Field(..., description="Peraturan ID")
    bab_id: Optional[int] = Field(None, description="Filter by bab_id")
    items: List[PasalResponse] = Field(..., description="List of pasal")


class PasalFilter(BaseModel):
    """Model for pasal filter/query"""

    bab_id: Optional[int] = Field(None, description="Filter by bab_id")
    skip: int = Field(0, ge=0, description="Offset for pagination")
    limit: int = Field(50, ge=1, le=100, description="Result limit per page")
    search: Optional[str] = Field(None, description="Search string in number/title/content")
    sort_by: Optional[str] = Field(None, description="Field for sorting")
    sort_order: str = Field("desc", pattern="^(asc|desc)$", description="Sort order")

    @field_validator("sort_by")
    @classmethod
    def validate_sort_by(cls, v):
        """Validate sortable fields"""
        if v:
            sort_fields = [
                "nomor_pasal",
                "judul_pasal",
                "konten_pasal",
                "urutan",
                "created_at",
                "updated_at",
            ]
            if v not in sort_fields:
                raise ValueError(f"Sort by must be one of: {', '.join(sort_fields)}")
        return v


class AyatNode(BaseModel):
    """Model for ayat in tree structure"""

    id: int = Field(..., description="Ayat ID")
    nomor_ayat: str = Field(..., description="Ayat number")
    konten_ayat: str = Field(..., description="Ayat content")
    urutan: int = Field(..., description="Ayat order")

    class Config:
        from_attributes = True


class PasalNode(BaseModel):
    """Model for pasal in tree structure (nested within bab or peraturan)"""

    id: int = Field(..., description="Pasal ID")
    nomor_pasal: str = Field(..., description="Pasal number")
    judul_pasal: Optional[str] = Field(None, description="Pasal title")
    konten_pasal: str = Field(..., description="Pasal content")
    urutan: int = Field(..., description="Pasal order")
    ayat_list: List[AyatNode] = Field(default_factory=list, description="List of ayat in pasal")

    class Config:
        from_attributes = True
