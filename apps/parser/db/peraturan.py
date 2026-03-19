"""
Database Operations untuk Peraturan
CRUD operations menggunakan PostgreSQL dengan asyncpg
"""

import asyncpg
from typing import List, Dict, Optional, Any
from datetime import datetime
import logging
from contextlib import asynccontextmanager

logger = logging.getLogger(__name__)

# Connection pool configuration
_db_pool: Optional[asyncpg.Pool] = None


async def init_db_pool(
    host: str = "localhost",
    port: int = 5432,
    database: str = "peraturan_db",
    user: str = "postgres",
    password: str = "postgres",
    min_connections: int = 1,
    max_connections: int = 10
) -> None:
    """
    Initialize database connection pool

    Args:
        host: Database host
        port: Database port
        database: Database name
        user: Database user
        password: Database password
        min_connections: Minimum connections in pool
        max_connections: Maximum connections in pool
    """
    global _db_pool

    try:
        dsn = f"postgresql://{user}:{password}@{host}:{port}/{database}"
        _db_pool = await asyncpg.create_pool(
            dsn,
            min_size=min_connections,
            max_size=max_connections,
            command_timeout=60
        )
        logger.info("Database connection pool initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database pool: {e}")
        raise


@asynccontextmanager
async def get_db_connection():
    """
    Context manager untuk mendapatkan database connection dari pool

    Yields:
        asyncpg connection object
    """
    if _db_pool is None:
        raise RuntimeError("Database pool not initialized. Call init_db_pool() first.")

    async with _db_pool.acquire() as conn:
        try:
            yield conn
        except Exception as e:
            logger.error(f"Database connection error: {e}")
            raise


# ========================================
# CRUD Operations untuk Peraturan
# ========================================

async def create_peraturan(peraturan_data: Dict[str, Any]) -> str:
    """
    Create peraturan baru di database

    Args:
        peraturan_data: Dictionary data peraturan

    Returns:
        ID peraturan yang dibuat
    """
    insert_query = """
    INSERT INTO peraturan (
        id, judul, nomor, tahun, kategori, url, pdf_url,
        jenis_peraturan, pemrakarsa, tentang, tempat_penetapan,
        tanggal_ditetapkan, pejabat_menetapkan, status_peraturan,
        jumlah_dilihat, jumlah_download, tanggal_diundangkan,
        tanggal_disahkan, deskripsi, metadata, parsed_at
    )
    VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12,
            $13, $14, $15, $16, $17, $18, $19, $20, $21)
    ON CONFLICT (id) DO UPDATE SET
        judul = EXCLUDED.judul,
        nomor = EXCLUDED.nomor,
        tahun = EXCLUDED.tahun,
        kategori = EXCLUDED.kategori,
        url = EXCLUDED.url,
        pdf_url = EXCLUDED.pdf_url,
        jenis_peraturan = EXCLUDED.jenis_peraturan,
        pemrakarsa = EXCLUDED.pemrakarsa,
        tentang = EXCLUDED.tentang,
        tempat_penetapan = EXCLUDED.tempat_penetapan,
        tanggal_ditetapkan = EXCLUDED.tanggal_ditetapkan,
        pejabat_menetapkan = EXCLUDED.pejabat_menetapkan,
        status_peraturan = EXCLUDED.status_peraturan,
        jumlah_dilihat = EXCLUDED.jumlah_dilihat,
        jumlah_download = EXCLUDED.jumlah_download,
        tanggal_diundangkan = EXCLUDED.tanggal_diundangkan,
        tanggal_disahkan = EXCLUDED.tanggal_disahkan,
        deskripsi = EXCLUDED.deskripsi,
        metadata = EXCLUDED.metadata,
        updated_at = CURRENT_TIMESTAMP,
        parsed_at = EXCLUDED.parsed_at
    RETURNING id
    """

    try:
        async with get_db_connection() as conn:
            peraturan_id = await conn.fetchval(
                insert_query,
                peraturan_data.get('id'),
                peraturan_data.get('judul'),
                peraturan_data.get('nomor'),
                peraturan_data.get('tahun'),
                peraturan_data.get('kategori'),
                peraturan_data.get('url'),
                peraturan_data.get('pdf_url'),
                peraturan_data.get('jenis_peraturan'),
                peraturan_data.get('pemrakarsa'),
                peraturan_data.get('tentang'),
                peraturan_data.get('tempat_penetapan'),
                peraturan_data.get('tanggal_ditetapkan'),
                peraturan_data.get('pejabat_menetapkan'),
                peraturan_data.get('status_peraturan', 'Berlaku'),
                peraturan_data.get('jumlah_dilihat', 0),
                peraturan_data.get('jumlah_download', 0),
                peraturan_data.get('tanggal_diundangkan'),
                peraturan_data.get('tanggal_disahkan'),
                peraturan_data.get('deskripsi'),
                peraturan_data.get('metadata', {}),
                peraturan_data.get('parsed_at')
            )
            logger.info(f"Peraturan created/updated: {peraturan_id}")
            return peraturan_id
    except Exception as e:
        logger.error(f"Failed to create peraturan: {e}")
        raise


async def get_peraturan_by_id(peraturan_id: str) -> Optional[Dict[str, Any]]:
    """
    Get peraturan by ID

    Args:
        peraturan_id: ID peraturan

    Returns:
        Dictionary data peraturan atau None jika tidak ditemukan
    """
    select_query = """
    SELECT id, judul, nomor, tahun, kategori, url, pdf_url,
           jenis_peraturan, pemrakarsa, tentang, tempat_penetapan,
           tanggal_ditetapkan, pejabat_menetapkan, status_peraturan,
           jumlah_dilihat, jumlah_download, tanggal_diundangkan,
           tanggal_disahkan, deskripsi, metadata,
           created_at, updated_at, parsed_at, reparse_count, last_reparse_at
    FROM peraturan
    WHERE id = $1
    """

    try:
        async with get_db_connection() as conn:
            result = await conn.fetchrow(select_query, peraturan_id)
            return dict(result) if result else None
    except Exception as e:
        logger.error(f"Failed to get peraturan {peraturan_id}: {e}")
        return None


async def get_peraturan_list(
    skip: int = 0,
    limit: int = 20,
    category: Optional[str] = None,
    year: Optional[int] = None,
    jenis: Optional[str] = None,
    status: Optional[str] = None,
    search: Optional[str] = None,
    sort_by: Optional[str] = None,
    sort_order: str = "desc"
) -> Dict[str, Any]:
    """
    Get list peraturan dengan filter dan pagination

    Args:
        skip: Offset untuk pagination
        limit: Limit hasil per page
        category: Filter kategori
        year: Filter tahun
        jenis: Filter jenis peraturan
        status: Filter status peraturan
        search: Search string
        sort_by: Field untuk sorting
        sort_order: Urutan sorting (asc/desc)

    Returns:
        Dictionary dengan total, skip, limit, dan items
    """
    # Build query
    conditions = []
    params = []
    param_count = 0

    if category:
        param_count += 1
        conditions.append(f"kategori = ${param_count}")
        params.append(category)

    if year:
        param_count += 1
        conditions.append(f"tahun = ${param_count}")
        params.append(year)

    if jenis:
        param_count += 1
        conditions.append(f"jenis_peraturan = ${param_count}")
        params.append(jenis)

    if status:
        param_count += 1
        conditions.append(f"status_peraturan = ${param_count}")
        params.append(status)

    if search:
        param_count += 1
        conditions.append(f"to_tsvector('indonesian', judul || ' ' || COALESCE(nomor, '') || ' ' || COALESCE(tentang, '')) @@ plainto_tsquery('indonesian', ${param_count})")
        params.append(search)

    where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""

    # Sorting
    if sort_by:
        order_clause = f"ORDER BY {sort_by} {sort_order.upper()}"
    else:
        order_clause = "ORDER BY created_at DESC"

    # Get total count
    count_query = f"SELECT COUNT(*) FROM peraturan {where_clause}"

    # Get data
    data_query = f"""
    SELECT id, judul, nomor, tahun, kategori, url, pdf_url,
           jenis_peraturan, pemrakarsa, tentang, status_peraturan,
           created_at, updated_at, parsed_at, reparse_count,
           (SELECT COUNT(*) FROM pasals WHERE peraturan_id = peraturan.id) as total_pasal
    FROM peraturan
    {where_clause}
    {order_clause}
    LIMIT ${param_count + 1} OFFSET ${param_count + 2}
    """
    params.extend([limit, skip])

    try:
        async with get_db_connection() as conn:
            # Get total count
            total = await conn.fetchval(count_query, *params)

            # Get data
            items = await conn.fetch(data_query, *params)

            return {
                "total": total,
                "skip": skip,
                "limit": limit,
                "items": [dict(item) for item in items]
            }
    except Exception as e:
        logger.error(f"Failed to get peraturan list: {e}")
        return {
            "total": 0,
            "skip": skip,
            "limit": limit,
            "items": []
        }


async def update_peraturan(peraturan_id: str, update_data: Dict[str, Any]) -> bool:
    """
    Update peraturan

    Args:
        peraturan_id: ID peraturan
        update_data: Dictionary data untuk update

    Returns:
        True jika berhasil, False jika tidak
    """
    # Build SET clause
    set_clauses = []
    params = []
    param_count = 0

    for key, value in update_data.items():
        if key != 'id':  # Skip id
            param_count += 1
            set_clauses.append(f"{key} = ${param_count}")
            params.append(value)

    if not set_clauses:
        return False

    set_clauses.append("updated_at = CURRENT_TIMESTAMP")
    params.append(peraturan_id)

    update_query = f"""
    UPDATE peraturan
    SET {', '.join(set_clauses)}
    WHERE id = ${param_count + 1}
    """

    try:
        async with get_db_connection() as conn:
            result = await conn.execute(update_query, *params)
            affected_rows = result.split(" ")[-1]
            logger.info(f"Updated peraturan {peraturan_id}: {affected_rows} rows")
            return int(affected_rows) > 0
    except Exception as e:
        logger.error(f"Failed to update peraturan {peraturan_id}: {e}")
        return False


async def delete_peraturan(peraturan_id: str) -> bool:
    """
    Delete peraturan

    Args:
        peraturan_id: ID peraturan

    Returns:
        True jika berhasil, False jika tidak
    """
    delete_query = "DELETE FROM peraturan WHERE id = $1"

    try:
        async with get_db_connection() as conn:
            result = await conn.execute(delete_query, peraturan_id)
            affected_rows = result.split(" ")[-1]
            logger.info(f"Deleted peraturan {peraturan_id}: {affected_rows} rows")
            return int(affected_rows) > 0
    except Exception as e:
        logger.error(f"Failed to delete peraturan {peraturan_id}: {e}")
        return False


# ========================================
# CRUD Operations untuk Bab
# ========================================

async def create_bab(bab_data: Dict[str, Any]) -> int:
    """
    Create bab baru di database

    Args:
        bab_data: Dictionary data bab

    Returns:
        ID bab yang dibuat
    """
    insert_query = """
    INSERT INTO bab (
        peraturan_id, nomor_bab, judul_bab, urutan
    )
    VALUES ($1, $2, $3, $4)
    ON CONFLICT (peraturan_id, nomor_bab) DO UPDATE SET
        judul_bab = EXCLUDED.judul_bab,
        urutan = EXCLUDED.urutan,
        updated_at = CURRENT_TIMESTAMP
    RETURNING id
    """

    try:
        async with get_db_connection() as conn:
            bab_id = await conn.fetchval(
                insert_query,
                bab_data.get('peraturan_id'),
                bab_data.get('nomor_bab'),
                bab_data.get('judul_bab'),
                bab_data.get('urutan')
            )
            logger.info(f"Bab created/updated: {bab_id}")
            return bab_id
    except Exception as e:
        logger.error(f"Failed to create bab: {e}")
        raise


async def get_bab_by_id(bab_id: int) -> Optional[Dict[str, Any]]:
    """
    Get bab by ID

    Args:
        bab_id: ID bab

    Returns:
        Dictionary data bab atau None
    """
    select_query = """
    SELECT id, peraturan_id, nomor_bab, judul_bab, urutan,
           created_at, updated_at
    FROM bab
    WHERE id = $1
    """

    try:
        async with get_db_connection() as conn:
            result = await conn.fetchrow(select_query, bab_id)
            return dict(result) if result else None
    except Exception as e:
        logger.error(f"Failed to get bab {bab_id}: {e}")
        return None


async def get_bab_list(
    peraturan_id: str,
    skip: int = 0,
    limit: int = 50
) -> Dict[str, Any]:
    """
    Get list bab by peraturan_id dengan pagination

    Args:
        peraturan_id: ID peraturan
        skip: Offset untuk pagination
        limit: Limit hasil per page

    Returns:
        Dictionary dengan total, skip, limit, dan items
    """
    # Get total count
    count_query = "SELECT COUNT(*) FROM bab WHERE peraturan_id = $1"

    # Get data
    data_query = """
    SELECT id, peraturan_id, nomor_bab, judul_bab, urutan,
           created_at, updated_at,
           (SELECT COUNT(*) FROM pasals WHERE bab_id = bab.id) as total_pasal
    FROM bab
    WHERE peraturan_id = $1
    ORDER BY urutan ASC
    LIMIT $2 OFFSET $3
    """

    try:
        async with get_db_connection() as conn:
            # Get total count
            total = await conn.fetchval(count_query, peraturan_id)

            # Get data
            items = await conn.fetch(data_query, peraturan_id, limit, skip)

            return {
                "total": total,
                "skip": skip,
                "limit": limit,
                "items": [dict(item) for item in items]
            }
    except Exception as e:
        logger.error(f"Failed to get bab list for {peraturan_id}: {e}")
        return {
            "total": 0,
            "skip": skip,
            "limit": limit,
            "items": []
        }


async def update_bab(bab_id: int, update_data: Dict[str, Any]) -> bool:
    """
    Update bab

    Args:
        bab_id: ID bab
        update_data: Dictionary data untuk update

    Returns:
        True jika berhasil, False jika tidak
    """
    # Build SET clause
    set_clauses = []
    params = []
    param_count = 0

    for key, value in update_data.items():
        if key != 'id':  # Skip id
            param_count += 1
            set_clauses.append(f"{key} = ${param_count}")
            params.append(value)

    if not set_clauses:
        return False

    set_clauses.append("updated_at = CURRENT_TIMESTAMP")
    params.append(bab_id)

    update_query = f"""
    UPDATE bab
    SET {', '.join(set_clauses)}
    WHERE id = ${param_count + 1}
    """

    try:
        async with get_db_connection() as conn:
            result = await conn.execute(update_query, *params)
            affected_rows = result.split(" ")[-1]
            return int(affected_rows) > 0
    except Exception as e:
        logger.error(f"Failed to update bab {bab_id}: {e}")
        return False


async def delete_bab(bab_id: int) -> bool:
    """
    Delete bab

    Args:
        bab_id: ID bab

    Returns:
        True jika berhasil, False jika tidak
    """
    delete_query = "DELETE FROM bab WHERE id = $1"

    try:
        async with get_db_connection() as conn:
            result = await conn.execute(delete_query, bab_id)
            affected_rows = result.split(" ")[-1]
            return int(affected_rows) > 0
    except Exception as e:
        logger.error(f"Failed to delete bab {bab_id}: {e}")
        return False


# ========================================
# CRUD Operations untuk Pasals
# ========================================

async def create_pasal(pasal_data: Dict[str, Any]) -> int:
    """
    Create pasal baru di database

    Args:
        pasal_data: Dictionary data pasal

    Returns:
        ID pasal yang dibuat
    """
    insert_query = """
    INSERT INTO pasals (
        peraturan_id, bab_id, nomor_pasal, judul_pasal,
        konten_pasal, urutan, metadata
    )
    VALUES ($1, $2, $3, $4, $5, $6, $7)
    ON CONFLICT (peraturan_id, nomor_pasal) DO UPDATE SET
        bab_id = EXCLUDED.bab_id,
        judul_pasal = EXCLUDED.judul_pasal,
        konten_pasal = EXCLUDED.konten_pasal,
        urutan = EXCLUDED.urutan,
        metadata = EXCLUDED.metadata,
        updated_at = CURRENT_TIMESTAMP
    RETURNING id
    """

    try:
        async with get_db_connection() as conn:
            pasal_id = await conn.fetchval(
                insert_query,
                pasal_data.get('peraturan_id'),
                pasal_data.get('bab_id'),
                pasal_data.get('nomor_pasal'),
                pasal_data.get('judul_pasal'),
                pasal_data.get('konten_pasal'),
                pasal_data.get('urutan'),
                pasal_data.get('metadata', {})
            )
            logger.info(f"Pasal created/updated: {pasal_id}")
            return pasal_id
    except Exception as e:
        logger.error(f"Failed to create pasal: {e}")
        raise


async def get_pasal_by_id(pasal_id: int) -> Optional[Dict[str, Any]]:
    """
    Get pasal by ID

    Args:
        pasal_id: ID pasal

    Returns:
        Dictionary data pasal atau None
    """
    select_query = """
    SELECT id, peraturan_id, bab_id, nomor_pasal, judul_pasal,
           konten_pasal, urutan, metadata, created_at, updated_at
    FROM pasals
    WHERE id = $1
    """

    try:
        async with get_db_connection() as conn:
            result = await conn.fetchrow(select_query, pasal_id)
            return dict(result) if result else None
    except Exception as e:
        logger.error(f"Failed to get pasal {pasal_id}: {e}")
        return None


async def get_pasal_list(
    peraturan_id: str,
    bab_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 50
) -> Dict[str, Any]:
    """
    Get list pasal by peraturan_id atau bab_id dengan pagination

    Args:
        peraturan_id: ID peraturan
        bab_id: Filter by bab_id (optional)
        skip: Offset untuk pagination
        limit: Limit hasil per page

    Returns:
        Dictionary dengan total, skip, limit, dan items
    """
    # Build query
    conditions = ["peraturan_id = $1"]
    params = [peraturan_id]
    param_count = 1

    if bab_id:
        param_count += 1
        conditions.append(f"bab_id = ${param_count}")
        params.append(bab_id)

    where_clause = f"WHERE {' AND '.join(conditions)}"

    # Get total count
    count_query = f"SELECT COUNT(*) FROM pasals {where_clause}"

    # Get data
    data_query = """
    SELECT id, peraturan_id, bab_id, nomor_pasal, judul_pasal,
           konten_pasal, urutan, metadata, created_at, updated_at,
           (SELECT COUNT(*) FROM ayats WHERE pasal_id = pasals.id) as total_ayat
    FROM pasals
    {where_clause}
    ORDER BY urutan ASC
    LIMIT ${param_count + 1} OFFSET ${param_count + 2}
    """
    params.extend([limit, skip])

    try:
        async with get_db_connection() as conn:
            # Get total count
            total = await conn.fetchval(count_query, *params)

            # Get data
            items = await conn.fetch(data_query, *params)

            return {
                "total": total,
                "skip": skip,
                "limit": limit,
                "items": [dict(item) for item in items]
            }
    except Exception as e:
        logger.error(f"Failed to get pasal list: {e}")
        return {
            "total": 0,
            "skip": skip,
            "limit": limit,
            "items": []
        }


async def update_pasal(pasal_id: int, update_data: Dict[str, Any]) -> bool:
    """
    Update pasal

    Args:
        pasal_id: ID pasal
        update_data: Dictionary data untuk update

    Returns:
        True jika berhasil, False jika tidak
    """
    # Build SET clause
    set_clauses = []
    params = []
    param_count = 0

    for key, value in update_data.items():
        if key != 'id':  # Skip id
            param_count += 1
            set_clauses.append(f"{key} = ${param_count}")
            params.append(value)

    if not set_clauses:
        return False

    set_clauses.append("updated_at = CURRENT_TIMESTAMP")
    params.append(pasal_id)

    update_query = f"""
    UPDATE pasals
    SET {', '.join(set_clauses)}
    WHERE id = ${param_count + 1}
    """

    try:
        async with get_db_connection() as conn:
            result = await conn.execute(update_query, *params)
            affected_rows = result.split(" ")[-1]
            return int(affected_rows) > 0
    except Exception as e:
        logger.error(f"Failed to update pasal {pasal_id}: {e}")
        return False


async def delete_pasal(pasal_id: int) -> bool:
    """
    Delete pasal

    Args:
        pasal_id: ID pasal

    Returns:
        True jika berhasil, False jika tidak
    """
    delete_query = "DELETE FROM pasals WHERE id = $1"

    try:
        async with get_db_connection() as conn:
            result = await conn.execute(delete_query, pasal_id)
            affected_rows = result.split(" ")[-1]
            return int(affected_rows) > 0
    except Exception as e:
        logger.error(f"Failed to delete pasal {pasal_id}: {e}")
        return False


# ========================================
# CRUD Operations untuk Ayats
# ========================================

async def create_ayat(ayat_data: Dict[str, Any]) -> int:
    """
    Create ayat baru di database

    Args:
        ayat_data: Dictionary data ayat

    Returns:
        ID ayat yang dibuat
    """
    insert_query = """
    INSERT INTO ayats (
        pasal_id, nomor_ayat, konten_ayat, urutan, metadata
    )
    VALUES ($1, $2, $3, $4, $5)
    ON CONFLICT (pasal_id, nomor_ayat) DO UPDATE SET
        konten_ayat = EXCLUDED.konten_ayat,
        urutan = EXCLUDED.urutan,
        metadata = EXCLUDED.metadata,
        updated_at = CURRENT_TIMESTAMP
    RETURNING id
    """

    try:
        async with get_db_connection() as conn:
            ayat_id = await conn.fetchval(
                insert_query,
                ayat_data.get('pasal_id'),
                ayat_data.get('nomor_ayat'),
                ayat_data.get('konten_ayat'),
                ayat_data.get('urutan'),
                ayat_data.get('metadata', {})
            )
            logger.info(f"Ayat created/updated: {ayat_id}")
            return ayat_id
    except Exception as e:
        logger.error(f"Failed to create ayat: {e}")
        raise


async def get_ayat_by_id(ayat_id: int) -> Optional[Dict[str, Any]]:
    """
    Get ayat by ID

    Args:
        ayat_id: ID ayat

    Returns:
        Dictionary data ayat atau None
    """
    select_query = """
    SELECT id, pasal_id, nomor_ayat, konten_ayat,
           urutan, metadata, created_at, updated_at
    FROM ayats
    WHERE id = $1
    """

    try:
        async with get_db_connection() as conn:
            result = await conn.fetchrow(select_query, ayat_id)
            return dict(result) if result else None
    except Exception as e:
        logger.error(f"Failed to get ayat {ayat_id}: {e}")
        return None


async def get_ayat_list(
    pasal_id: int,
    skip: int = 0,
    limit: int = 50
) -> Dict[str, Any]:
    """
    Get list ayat by pasal_id dengan pagination

    Args:
        pasal_id: ID pasal
        skip: Offset untuk pagination
        limit: Limit hasil per page

    Returns:
        Dictionary dengan total, skip, limit, dan items
    """
    # Get total count
    count_query = "SELECT COUNT(*) FROM ayats WHERE pasal_id = $1"

    # Get data
    data_query = """
    SELECT id, pasal_id, nomor_ayat, konten_ayat,
           urutan, metadata, created_at, updated_at
    FROM ayats
    WHERE pasal_id = $1
    ORDER BY urutan ASC
    LIMIT $2 OFFSET $3
    """

    try:
        async with get_db_connection() as conn:
            # Get total count
            total = await conn.fetchval(count_query, pasal_id)

            # Get data
            items = await conn.fetch(data_query, pasal_id, limit, skip)

            return {
                "total": total,
                "skip": skip,
                "limit": limit,
                "items": [dict(item) for item in items]
            }
    except Exception as e:
        logger.error(f"Failed to get ayat list for pasal {pasal_id}: {e}")
        return {
            "total": 0,
            "skip": skip,
            "limit": limit,
            "items": []
        }


async def update_ayat(ayat_id: int, update_data: Dict[str, Any]) -> bool:
    """
    Update ayat

    Args:
        ayat_id: ID ayat
        update_data: Dictionary data untuk update

    Returns:
        True jika berhasil, False jika tidak
    """
    # Build SET clause
    set_clauses = []
    params = []
    param_count = 0

    for key, value in update_data.items():
        if key != 'id':  # Skip id
            param_count += 1
            set_clauses.append(f"{key} = ${param_count}")
            params.append(value)

    if not set_clauses:
        return False

    set_clauses.append("updated_at = CURRENT_TIMESTAMP")
    params.append(ayat_id)

    update_query = f"""
    UPDATE ayats
    SET {', '.join(set_clauses)}
    WHERE id = ${param_count + 1}
    """

    try:
        async with get_db_connection() as conn:
            result = await conn.execute(update_query, *params)
            affected_rows = result.split(" ")[-1]
            return int(affected_rows) > 0
    except Exception as e:
        logger.error(f"Failed to update ayat {ayat_id}: {e}")
        return False


async def delete_ayat(ayat_id: int) -> bool:
    """
    Delete ayat

    Args:
        ayat_id: ID ayat

    Returns:
        True jika berhasil, False jika tidak
    """
    delete_query = "DELETE FROM ayats WHERE id = $1"

    try:
        async with get_db_connection() as conn:
            result = await conn.execute(delete_query, ayat_id)
            affected_rows = result.split(" ")[-1]
            return int(affected_rows) > 0
    except Exception as e:
        logger.error(f"Failed to delete ayat {ayat_id}: {e}")
        return False


# ========================================
# Helper Functions untuk Peraturan Lengkap
# ========================================

async def save_peraturan_complete(
    peraturan_data: Dict[str, Any],
    bab_list: List[Dict[str, Any]],
    pasal_list: List[Dict[str, Any]],
    ayat_list: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Save peraturan lengkap dengan bab, pasals, dan ayats dalam satu transaction

    Args:
        peraturan_data: Data peraturan
        bab_list: List data bab
        pasal_list: List data pasal
        ayat_list: List data ayat

    Returns:
        Dictionary dengan peraturan_id, bab_ids, pasal_ids, ayat_ids
    """
    async with get_db_connection() as conn:
        async with conn.transaction():
            try:
                # 1. Create/update peraturan
                peraturan_id = await create_peraturan(peraturan_data)

                # 2. Create/update bab
                bab_ids = {}
                for bab_data in bab_list:
                    bab_data_with_id = {**bab_data, "peraturan_id": peraturan_id}
                    bab_id = await create_bab(bab_data_with_id)
                    bab_ids[bab_data["nomor_bab"]] = bab_id

                # 3. Create/update pasals
                pasal_ids = {}
                for pasal_data in pasal_list:
                    # Find bab_id from nomor_bab
                    bab_id = bab_ids.get(pasal_data.get("bab_id"))

                    pasal_data_with_id = {
                        **pasal_data,
                        "peraturan_id": peraturan_id,
                        "bab_id": bab_id
                    }
                    pasal_id = await create_pasal(pasal_data_with_id)
                    pasal_ids[pasal_data["nomor_pasal"]] = pasal_id

                # 4. Create/update ayats
                ayat_ids = {}
                for ayat_data in ayat_list:
                    # Find pasal_id from nomor_pasal
                    pasal_id = pasal_ids.get(ayat_data.get("pasal_id"))

                    ayat_data_with_id = {
                        **ayat_data,
                        "pasal_id": pasal_id
                    }
                    ayat_id = await create_ayat(ayat_data_with_id)
                    ayat_ids[f"{ayat_data['pasal_id']}-{ayat_data['nomor_ayat']}"] = ayat_id

                # 5. Update peraturan metadata
                await update_peraturan(peraturan_id, {
                    "parsed_at": datetime.now(),
                    "metadata": {
                        "bab_count": len(bab_list),
                        "pasal_count": len(pasal_list),
                        "ayat_count": len(ayat_list)
                    }
                })

                logger.info(f"Successfully saved complete peraturan {peraturan_id}")

                return {
                    "peraturan_id": peraturan_id,
                    "bab_ids": bab_ids,
                    "pasal_ids": pasal_ids,
                    "ayat_ids": ayat_ids
                }

            except Exception as e:
                logger.error(f"Failed to save complete peraturan: {e}")
                raise


async def get_peraturan_complete(peraturan_id: str) -> Optional[Dict[str, Any]]:
    """
    Get peraturan lengkap dengan semua bab, pasals, dan ayats

    Args:
        peraturan_id: ID peraturan

    Returns:
        Dictionary dengan peraturan, bab_list, pasal_list, ayat_list
    """
    try:
        # Get peraturan
        peraturan = await get_peraturan_by_id(peraturan_id)
        if not peraturan:
            return None

        # Get bab list
        bab_result = await get_bab_list(peraturan_id, limit=1000)
        bab_list = bab_result["items"]

        # Get pasal list
        pasal_result = await get_pasal_list(peraturan_id, limit=1000)
        pasal_list = pasal_result["items"]

        # Get ayat list untuk semua pasal
        ayat_list = []
        for pasal in pasal_list:
            ayat_result = await get_ayat_list(pasal["id"], limit=1000)
            for ayat in ayat_result["items"]:
                ayat_list.append(ayat)

        return {
            "peraturan": peraturan,
            "bab_list": bab_list,
            "pasal_list": pasal_list,
            "ayat_list": ayat_list
        }

    except Exception as e:
        logger.error(f"Failed to get complete peraturan {peraturan_id}: {e}")
        return None


async def close_db_pool() -> None:
    """Close database connection pool"""
    global _db_pool
    if _db_pool:
        await _db_pool.close()
        _db_pool = None
        logger.info("Database connection pool closed")
