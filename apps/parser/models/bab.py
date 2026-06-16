"""
Pydantic Models for Bab Table
Models for bab table validation and serialization only
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


# ========================================
# Models for Bab
# ========================================


class BabBase(BaseModel):
    """Base model for Bab"""

    peraturan_id: str = Field(..., description="Foreign key to peraturan table")
    nomor_bab: str = Field(..., min_length=1, description="Bab number (I, II, III, etc.)")
    judul_bab: Optional[str] = Field(None, description="Bab title")
    urutan: int = Field(..., ge=0, description="Bab order within peraturan")


class BabCreate(BabBase):
    """Model for creating new bab"""

    pass


class BabUpdate(BaseModel):
    """Model for updating bab"""

    nomor_bab: Optional[str] = Field(None, min_length=1)
    judul_bab: Optional[str] = Field(None)
    urutan: Optional[int] = Field(None, ge=0)


class BabInDB(BabBase):
    """Model for bab in database"""

    id: int = Field(..., description="Auto-increment ID")
    created_at: datetime = Field(default_factory=datetime.now, description="Time bab was created")
    updated_at: datetime = Field(default_factory=datetime.now, description="Time bab was updated")

    class Config:
        from_attributes = True


class BabResponse(BabInDB):
    """Model for bab API response"""

    pass


class BabWithPasalCount(BabResponse):
    """Model for bab with pasal count"""

    total_pasal: int = Field(0, description="Total pasal in bab")


class BabWithPeraturanInfo(BabResponse):
    """Model for bab with peraturan info"""

    judul_peraturan: Optional[str] = Field(None, description="Peraturan title")
    nomor_peraturan: str = Field(..., description="Peraturan number")
    tahun_peraturan: int = Field(..., description="Peraturan year")
    kategori_peraturan: str = Field(..., description="Peraturan category")
    jenis_peraturan: Optional[str] = Field(None, description="Peraturan type")


# ========================================
# Models for List and Filter
# ========================================


class BabListResponse(BaseModel):
    """Model for bab list response"""

    total: int = Field(..., description="Total bab count")
    peraturan_id: str = Field(..., description="Peraturan ID")
    items: List[BabResponse] = Field(..., description="List of bab")


class BabFilter(BaseModel):
    """Model for bab filter/query"""

    skip: int = Field(0, ge=0, description="Offset for pagination")
    limit: int = Field(50, ge=1, le=100, description="Result limit per page")


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
    ayat_list: List[AyatNode] = Field(default_factory=list, description="List of ayat in pasal")

    class Config:
        from_attributes = True


class BabNode(BaseModel):
    """Model for bab in tree structure (nested within peraturan)"""

    id: int = Field(..., description="Bab ID")
    nomor_bab: str = Field(..., description="Bab number")
    judul_bab: Optional[str] = Field(None, description="Bab title")
    urutan: int = Field(..., description="Bab order")
    pasal_list: List[PasalNode] = Field(default_factory=list, description="List of pasal in bab")

    class Config:
        from_attributes = True
