"""
Pydantic Models for Ayat Table
Models for ayat table validation and serialization only
"""

from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Dict, Any
from datetime import datetime


# ========================================
# Models for Ayat
# ========================================


class AyatBase(BaseModel):
    """Base model for Ayat"""

    pasal_id: int = Field(..., description="Foreign key to pasals table")
    bab_id: Optional[int] = Field(None, description="Foreign key to bab table (denormalized)")
    peraturan_id: Optional[str] = Field(
        None, description="Foreign key to peraturan table (denormalized)"
    )
    nomor_ayat: str = Field(..., min_length=1, description="Ayat number ((1), (2), (3), etc.)")
    konten_ayat: str = Field(..., min_length=1, description="Ayat content")
    urutan: int = Field(..., ge=0, description="Ayat order within pasal")


class AyatCreate(AyatBase):
    """Model for creating new ayat"""

    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")


class AyatUpdate(BaseModel):
    """Model for updating ayat"""

    nomor_ayat: Optional[str] = Field(None, min_length=1)
    konten_ayat: Optional[str] = Field(None, min_length=1)
    urutan: Optional[int] = Field(None, ge=0)
    metadata: Optional[Dict[str, Any]] = None


class AyatInDB(AyatBase):
    """Model for ayat in database"""

    id: int = Field(..., description="Auto-increment ID")
    metadata: Optional[Dict[str, Any]] = None
    created_at: datetime = Field(default_factory=datetime.now, description="Time ayat was created")
    updated_at: datetime = Field(default_factory=datetime.now, description="Time ayat was updated")

    class Config:
        from_attributes = True


class AyatResponse(AyatInDB):
    """Model for ayat API response"""

    pass


class AyatWithPasalInfo(AyatResponse):
    """Model for ayat with pasal info"""

    nomor_pasal: str = Field(..., description="Pasal number")
    judul_pasal: Optional[str] = Field(None, description="Pasal title")
    pasal_urutan: Optional[int] = Field(None, description="Pasal order")


class AyatWithBabInfo(AyatResponse):
    """Model for ayat with bab info"""

    nomor_bab: Optional[str] = Field(None, description="Bab number")
    judul_bab: Optional[str] = Field(None, description="Bab title")
    bab_urutan: Optional[int] = Field(None, description="Bab order")


class AyatWithPasalBabPeraturan(AyatResponse):
    """Model for ayat with pasal, bab, and peraturan info"""

    nomor_pasal: str = Field(..., description="Pasal number")
    judul_pasal: Optional[str] = Field(None, description="Pasal title")
    pasal_urutan: Optional[int] = Field(None, description="Pasal order")
    nomor_bab: Optional[str] = Field(None, description="Bab number")
    judul_bab: Optional[str] = Field(None, description="Bab title")
    bab_urutan: Optional[int] = Field(None, description="Bab order")
    judul_peraturan: Optional[str] = Field(None, description="Peraturan title")
    nomor_peraturan: str = Field(..., description="Peraturan number")
    tahun_peraturan: int = Field(..., description="Peraturan year")
    kategori_peraturan: str = Field(..., description="Peraturan category")
    jenis_peraturan: Optional[str] = Field(None, description="Peraturan type")
    tentang: Optional[str] = Field(None, description="Peraturan topic")


# ========================================
# Models for List and Filter
# ========================================


class AyatListResponse(BaseModel):
    """Model for ayat list response"""

    total: int = Field(..., description="Total ayat count")
    pasal_id: int = Field(..., description="Pasal ID")
    items: List[AyatResponse] = Field(..., description="List of ayat")


class AyatFilter(BaseModel):
    """Model for ayat filter/query"""

    skip: int = Field(0, ge=0, description="Offset for pagination")
    limit: int = Field(50, ge=1, le=100, description="Result limit per page")
    search: Optional[str] = Field(None, description="Search string in number/content")
    sort_by: Optional[str] = Field(None, description="Field for sorting")
    sort_order: str = Field("desc", pattern="^(asc|desc)$", description="Sort order")

    @field_validator("sort_by")
    @classmethod
    def validate_sort_by(cls, v):
        """Validate sortable fields"""
        if v:
            sort_fields = ["nomor_ayat", "konten_ayat", "urutan", "created_at", "updated_at"]
            if v not in sort_fields:
                raise ValueError(f"Sort by must be one of: {', '.join(sort_fields)}")
        return v


class AyatNode(BaseModel):
    """Model for ayat in tree structure (nested within pasal)"""

    id: int = Field(..., description="Ayat ID")
    nomor_ayat: str = Field(..., description="Ayat number")
    konten_ayat: str = Field(..., description="Ayat content")
    urutan: int = Field(..., description="Ayat order")

    class Config:
        from_attributes = True
