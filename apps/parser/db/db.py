"""
Database Connection Management dengan Connection Pooling
Module ini menghandle koneksi ke PostgreSQL dengan asyncpg dan connection pooling
"""

import asyncpg
from typing import Optional, Any
from contextlib import asynccontextmanager
import logging

logger = logging.getLogger(__name__)

# Global connection pool
_db_pool: Optional[asyncpg.Pool] = None


async def init_db_pool(
    host: str = "localhost",
    port: int = 5432,
    database: str = "peraturan_db",
    user: str = "postgres",
    password: str = "postgres",
    min_connections: int = 1,
    max_connections: int = 10,
) -> None:
    """
    Inisialisasi database connection pool

    Args:
        host: Database host
        port: Database port
        database: Database name
        user: Database user
        password: Database password
        min_connections: Minimum connections di pool
        max_connections: Maximum connections di pool
    """
    global _db_pool

    try:
        _db_pool = await asyncpg.create_pool(
            host=host,
            port=port,
            database=database,
            user=user,
            password=password,
            min_size=min_connections,
            max_size=max_connections,
            command_timeout=60,
            server_settings={"timezone": "UTC"},
        )
        logger.info(
            f"Database pool initialized: {host}:{port}/{database} "
            f"(min={min_connections}, max={max_connections})"
        )
    except Exception as e:
        logger.error(f"Failed to initialize database pool: {e}")
        raise


async def close_db_pool() -> None:
    """Tutup semua koneksi di pool"""
    global _db_pool

    if _db_pool:
        await _db_pool.close()
        _db_pool = None
        logger.info("Database pool closed")


@asynccontextmanager
async def get_db_connection():
    """
    Context manager untuk mendapatkan koneksi database dari pool

    Usage:
        async with get_db_connection() as conn:
            result = await conn.fetchval("SELECT 1")
    """
    global _db_pool

    if _db_pool is None:
        raise RuntimeError("Database pool not initialized. Call init_db_pool() first.")

    async with _db_pool.acquire() as conn:
        try:
            yield conn
        except Exception as e:
            logger.error(f"Database connection error: {e}")
            raise


@asynccontextmanager
async def get_db_transaction():
    """
    Context manager untuk transaksi database otomatis

    Usage:
        async with get_db_transaction() as conn:
            # Semua perintah di sini adalah bagian dari satu transaksi
            await conn.execute("INSERT INTO ...")

    Rollback otomatis jika exception, commit jika sukses.
    """
    async with get_db_connection() as conn:
        async with conn.transaction():
            try:
                yield conn
            except Exception as e:
                logger.error(f"Transaction failed, rolling back: {e}")
                raise


def get_pool_status() -> dict:
    """
    Get status dari connection pool

    Returns:
        Dictionary dengan informasi pool
    """
    global _db_pool

    if _db_pool is None:
        return {"status": "not_initialized"}

    return {
        "status": "initialized",
        "min_size": _db_pool.get_min_size(),
        "max_size": _db_pool.get_max_size(),
        "size": _db_pool.get_size(),
    }


async def execute_query(query: str, args: tuple = (), fetch: str = "one") -> Optional[Any]:
    """
    Execute query dengan parameterized statement (prepared statement)

    Args:
        query: SQL query dengan positional parameters ($1, $2, etc.)
        args: Tuple of parameter values
        fetch: Type of fetch ('one', 'all', 'val', 'exec')

    Returns:
        Result berdasarkan type fetch

    Note:
        Menggunakan positional parameters ($1, $2, etc.) mencegah SQL injection
        karena asyncpg akan memvalidasi dan escape parameter dengan benar.
    """
    async with get_db_connection() as conn:
        try:
            if fetch == "one":
                result = await conn.fetchrow(query, *args)
                return dict(result) if result else None
            elif fetch == "all":
                result = await conn.fetch(query, *args)
                return [dict(row) for row in result]
            elif fetch == "val":
                result = await conn.fetchval(query, *args)
                return result
            elif fetch == "exec":
                result = await conn.execute(query, *args)
                affected = result.split(" ")[-1]
                return int(affected) if affected else 0
            else:
                raise ValueError(f"Invalid fetch type: {fetch}")
        except Exception as e:
            logger.error(f"Query failed: {e}\nQuery: {query}")
            raise


async def execute_transaction(queries: list[tuple[str, tuple]]) -> list[Any]:
    """
    Execute multiple queries dalam satu transaksi

    Args:
        queries: List of (query, args) tuples

    Returns:
        List of results

    Example:
        results = await execute_transaction([
            ("INSERT INTO table (...) VALUES ($1, $2)", (value1, value2)),
            ("UPDATE table SET field = $1 WHERE id = $2", (new_value, id)),
        ])
    """
    async with get_db_transaction() as conn:
        results = []
        for query, args in queries:
            try:
                result = await conn.fetchrow(query, *args)
                results.append(dict(result) if result else None)
            except Exception as e:
                logger.error(f"Transaction query failed: {e}")
                raise
        return results


# Helper functions untuk escaping parameter jika diperlukan
# Namun, asyncpg sudah melakukan escaping otomatis untuk positional parameters


def validate_identifier(identifier: str) -> bool:
    """
    Validasi bahwa identifier hanya berisi karakter aman untuk SQL identifier

    Args:
        identifier: SQL identifier (table name, column name, dll.)

    Returns:
        True jika aman, False jika tidak

    Note:
        Gunakan ini HANYA untuk identifier, bukan untuk values.
        Untuk values, gunakan positional parameters ($1, $2, dll.)
    """
    import re

    # Hanya izinkan alphanumeric, underscore, dan dot
    pattern = r"^[a-zA-Z0-9_\.]+$"
    return bool(re.match(pattern, identifier))


def sanitize_search_query(query: str) -> str:
    """
    Sanitize search query untuk full-text search

    Args:
        query: Search query dari user

    Returns:
        Sanitized query yang aman untuk plainto_tsquery

    Note:
        Fungsi ini melakukan sanitasi dasar untuk tsquery.
        Gunakan parameterized query untuk keamanan maksimal.
    """
    if not query:
        return ""

    # Hapus karakter spesial berbahaya
    dangerous_chars = ["'", '"', ";", "--", "/*", "*/"]
    sanitized = query
    for char in dangerous_chars:
        sanitized = sanitized.replace(char, "")

    return sanitized.strip()
