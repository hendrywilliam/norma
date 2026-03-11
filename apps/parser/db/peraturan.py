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
    password: str = "password",
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


async def create_tables() -> None:
    """Create tables untuk peraturan"""
    create_table_query = """
    CREATE TABLE IF NOT EXISTS peraturan (
        id VARCHAR(255) PRIMARY KEY,
        judul VARCHAR(1000) NOT NULL,
        nomor VARCHAR(100) NOT NULL,
        tahun INTEGER NOT NULL,
        kategori VARCHAR(50) NOT NULL,
        url VARCHAR(500) NOT NULL,
        pdf_url VARCHAR(500),
        tanggal_disahkan TIMESTAMP,
        tanggal_diundangkan TIMESTAMP,
        deskripsi TEXT,
        konten TEXT,
        metadata JSONB,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        parsed_at TIMESTAMP,
        reparse_count INTEGER DEFAULT 0,
        last_reparse_at TIMESTAMP
    );

    CREATE INDEX IF NOT EXISTS idx_peraturan_kategori ON peraturan(kategori);
    CREATE INDEX IF NOT EXISTS idx_peraturan_tahun ON peraturan(tahun);
    CREATE INDEX IF NOT EXISTS idx_peraturan_created_at ON peraturan(created_at);
    CREATE INDEX IF NOT EXISTS idx_peraturan_search ON peraturan USING gin(to_tsvector('indonesian', judul || ' ' || COALESCE(nomor, '') || ' ' || COALESCE(konten, '')));
    """

    try:
        async with get_db_connection() as conn:
            await conn.execute(create_table_query)
            logger.info("Tables created successfully")
    except Exception as e:
        logger.error(f"Failed to create tables: {e}")
        raise


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
        tanggal_disahkan, tanggal_diundangkan, deskripsi, konten,
        metadata, parsed_at
    )
    VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13)
    ON CONFLICT (id) DO UPDATE SET
        judul = EXCLUDED.judul,
        nomor = EXCLUDED.nomor,
        tahun = EXCLUDED.tahun,
        kategori = EXCLUDED.kategori,
        url = EXCLUDED.url,
        pdf_url = EXCLUDED.pdf_url,
        tanggal_disahkan = EXCLUDED.tanggal_disahkan,
        tanggal_diundangkan = EXCLUDED.tanggal_diundangkan,
        deskripsi = EXCLUDED.deskripsi,
        konten = EXCLUDED.konten,
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
                peraturan_data.get('tanggal_disahkan'),
                peraturan_data.get('tanggal_diundangkan'),
                peraturan_data.get('deskripsi'),
                peraturan_data.get('konten'),
                peraturan_data.get('metadata'),
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
           tanggal_disahkan, tanggal_diundangkan, deskripsi, konten,
           metadata, created_at, updated_at, parsed_at, reparse_count, last_reparse_at
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

    if search:
        param_count += 1
        conditions.append(f"to_tsvector('indonesian', judul || ' ' || COALESCE(nomor, '') || ' ' || COALESCE(konten, '')) @@ plainto_tsquery('indonesian', ${param_count})")
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
           tanggal_disahkan, tanggal_diundangkan, deskripsi,
           created_at, updated_at, parsed_at
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


async def search_peraturan(
    query: str,
    skip: int = 0,
    limit: int = 20
) -> Dict[str, Any]:
    """
    Full-text search peraturan menggunakan PostgreSQL full-text search

    Args:
        query: Search query
        skip: Offset untuk pagination
        limit: Limit hasil per page

    Returns:
        Dictionary dengan total, skip, limit, dan items
    """
    search_query = """
    SELECT id, judul, nomor, tahun, kategori, url, pdf_url,
           tanggal_disahkan, tanggal_diundangkan, deskripsi,
           created_at, updated_at, parsed_at,
           ts_rank(to_tsvector('indonesian', judul || ' ' || COALESCE(nomor, '') || ' ' || COALESCE(konten, '')),
                   plainto_tsquery('indonesian', $1)) as rank
    FROM peraturan
    WHERE to_tsvector('indonesian', judul || ' ' || COALESCE(nomor, '') || ' ' || COALESCE(konten, ''))
          @@ plainto_tsquery('indonesian', $1)
    ORDER BY rank DESC, created_at DESC
    LIMIT $2 OFFSET $3
    """

    count_query = """
    SELECT COUNT(*)
    FROM peraturan
    WHERE to_tsvector('indonesian', judul || ' ' || COALESCE(nomor, '') || ' ' || COALESCE(konten, ''))
          @@ plainto_tsquery('indonesian', $1)
    """

    try:
        async with get_db_connection() as conn:
            # Get total count
            total = await conn.fetchval(count_query, query)

            # Get data
            items = await conn.fetch(search_query, query, limit, skip)

            return {
                "total": total,
                "skip": skip,
                "limit": limit,
                "items": [dict(item) for item in items]
            }
    except Exception as e:
        logger.error(f"Failed to search peraturan: {e}")
        return {
            "total": 0,
            "skip": skip,
            "limit": limit,
            "items": []
        }


async def get_peraturan_stats() -> Dict[str, Any]:
    """
    Get statistics peraturan

    Returns:
        Dictionary dengan statistik peraturan
    """
    stats_query = """
    SELECT
        COUNT(*) as total,
        COUNT(DISTINCT kategori) as unique_categories,
        COUNT(DISTINCT tahun) as unique_years,
        MIN(tahun) as min_year,
        MAX(tahun) as max_year,
        AVG(reparse_count) as avg_reparse_count
    FROM peraturan
    """

    category_stats_query = """
    SELECT kategori, COUNT(*) as count
    FROM peraturan
    GROUP BY kategori
    ORDER BY count DESC
    """

    year_stats_query = """
    SELECT tahun, COUNT(*) as count
    FROM peraturan
    GROUP BY tahun
    ORDER BY tahun DESC
    LIMIT 10
    """

    try:
        async with get_db_connection() as conn:
            # General stats
            general_stats = dict(await conn.fetchrow(stats_query))

            # Category stats
            category_stats = [dict(row) for row in await conn.fetch(category_stats_query)]

            # Year stats
            year_stats = [dict(row) for row in await conn.fetch(year_stats_query)]

            return {
                "general": general_stats,
                "by_category": category_stats,
                "by_year": year_stats
            }
    except Exception as e:
        logger.error(f"Failed to get peraturan stats: {e}")
        return {
            "general": {},
            "by_category": [],
            "by_year": []
        }


async def save_peraturan(peraturan_data: Dict[str, Any]) -> str:
    """
    Helper function untuk save peraturan (create atau update)

    Args:
        peraturan_data: Dictionary data peraturan

    Returns:
        ID peraturan yang disimpan
    """
    return await create_peraturan(peraturan_data)


async def close_db_pool() -> None:
    """Close database connection pool"""
    global _db_pool
    if _db_pool:
        await _db_pool.close()
        _db_pool = None
        logger.info("Database connection pool closed")
