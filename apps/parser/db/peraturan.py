"""
Peraturan Database Functions
Wrapper functions untuk repository layer
"""

from typing import List, Dict, Optional, Any
from repositories.peraturan import peraturan_repository

# Import repositories untuk bab, pasal, ayat
try:
    from repositories.bab import bab_repository
except ImportError:
    bab_repository = None

try:
    from repositories.pasal import pasal_repository
except ImportError:
    pasal_repository = None

try:
    from repositories.ayat import ayat_repository
except ImportError:
    ayat_repository = None


# ========================================
# Peraturan Functions
# ========================================

async def get_peraturan_by_id(peraturan_id: str) -> Optional[Dict[str, Any]]:
    """Get peraturan by ID"""
    return await peraturan_repository.get_by_id(peraturan_id)


async def get_peraturan_list(
    skip: int = 0,
    limit: int = 20,
    category: Optional[str] = None,
    year: Optional[int] = None,
    jenis: Optional[str] = None,
    status: Optional[str] = None,
    search: Optional[str] = None
) -> Dict[str, Any]:
    """Get list peraturan dengan filter"""
    return await peraturan_repository.get_list(
        skip=skip,
        limit=limit,
        category=category,
        year=year,
        jenis=jenis,
        status=status,
        search=search
    )


async def get_peraturan_complete(peraturan_id: str) -> Optional[Dict[str, Any]]:
    """Get peraturan lengkap dengan bab, pasal, ayat"""
    peraturan = await get_peraturan_by_id(peraturan_id)

    if not peraturan:
        return None

    bab_list = []
    pasal_list = []
    ayat_list = []

    if bab_repository:
        bab_result = await bab_repository.get_list(peraturan_id=peraturan_id)
        bab_list = bab_result.get("items", [])

    if pasal_repository:
        pasal_result = await pasal_repository.get_list(peraturan_id=peraturan_id)
        pasal_list = pasal_result.get("items", [])

    if ayat_repository:
        ayat_list = await ayat_repository.get_list_by_peraturan(peraturan_id)

    return {
        "peraturan": peraturan,
        "bab_list": bab_list,
        "pasal_list": pasal_list,
        "ayat_list": ayat_list
    }


async def update_peraturan(peraturan_id: str, update_data: Dict[str, Any]) -> bool:
    """Update peraturan"""
    return await peraturan_repository.update(peraturan_id, update_data)


async def save_peraturan_complete(
    peraturan_data: Dict[str, Any],
    bab_list: List[Dict[str, Any]] = None,
    pasal_list: List[Dict[str, Any]] = None,
    ayat_list: List[Dict[str, Any]] = None
) -> str:
    """Save peraturan lengkap dengan bab, pasal, ayat"""
    # Save peraturan
    peraturan_id = await peraturan_repository.create(peraturan_data)

    # Save bab
    if bab_list and bab_repository:
        for bab_data in bab_list:
            bab_data['peraturan_id'] = peraturan_id
            await bab_repository.create(bab_data)

    # Save pasal
    if pasal_list and pasal_repository:
        for pasal_data in pasal_list:
            pasal_data['peraturan_id'] = peraturan_id
            await pasal_repository.create(pasal_data)

    # Save ayat
    if ayat_list and ayat_repository:
        for ayat_data in ayat_list:
            await ayat_repository.create(ayat_data)

    return peraturan_id


# ========================================
# Bab Functions
# ========================================

async def get_bab_by_id(bab_id: int) -> Optional[Dict[str, Any]]:
    """Get bab by ID"""
    if bab_repository:
        return await bab_repository.get_by_id(bab_id)
    return None


async def get_bab_list(
    peraturan_id: str,
    skip: int = 0,
    limit: int = 50
) -> Dict[str, Any]:
    """Get list bab untuk peraturan"""
    if bab_repository:
        return await bab_repository.get_list(
            peraturan_id=peraturan_id,
            skip=skip,
            limit=limit
        )
    return {"items": []}


# ========================================
# Pasal Functions
# ========================================

async def get_pasal_by_id(pasal_id: int) -> Optional[Dict[str, Any]]:
    """Get pasal by ID"""
    if pasal_repository:
        return await pasal_repository.get_by_id(pasal_id)
    return None


async def get_pasal_list(
    peraturan_id: str,
    bab_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 50
) -> Dict[str, Any]:
    """Get list pasal untuk peraturan atau bab"""
    if pasal_repository:
        result = await pasal_repository.get_list(
            peraturan_id=peraturan_id,
            bab_id=bab_id,
            skip=skip,
            limit=limit
        )
        return result if result else {"items": []}
    return {"items": []}


# ========================================
# Ayat Functions
# ========================================

async def get_ayat_by_id(ayat_id: int) -> Optional[Dict[str, Any]]:
    """Get ayat by ID"""
    if ayat_repository:
        return await ayat_repository.get_by_id(ayat_id)
    return None


async def get_ayat_list(
    pasal_id: int,
    skip: int = 0,
    limit: int = 50
) -> Dict[str, Any]:
    """Get list ayat untuk pasal"""
    if ayat_repository:
        items = await ayat_repository.get_list_by_pasal(
            pasal_id=pasal_id,
            skip=skip,
            limit=limit
        )
        return {"items": items} if items else {"items": []}
    return {"items": []}
