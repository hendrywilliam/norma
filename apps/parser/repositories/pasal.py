"""
Repository untuk Tabel Pasal
CRUD operations untuk tabel pasal
"""

from typing import List, Dict, Optional, Any
from datetime import datetime
import logging

# Import db connection management
from db import get_db_connection, execute_query, validate_identifier, sanitize_search_query

# Import Pasal models
from models.pasal import (
    PasalBase,
    PasalCreate,
    PasalUpdate,
    PasalInDB,
    PasalResponse,
    PasalWithAyatCount,
    PasalWithBabPeraturan,
    PasalListResponse,
    PasalFilter,
)

logger = logging.getLogger(__name__)


# ========================================
# Repository Class untuk Pasal
# ========================================


class PasalRepository:
    """Repository class untuk tabel pasal"""

    async def create(self, pasal_data: Dict[str, Any]) -> int:
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
            pasal_id = await execute_query(
                insert_query,
                args=(
                    pasal_data.get("peraturan_id"),
                    pasal_data.get("bab_id"),
                    pasal_data.get("nomor_pasal"),
                    pasal_data.get("judul_pasal"),
                    pasal_data.get("konten_pasal"),
                    pasal_data.get("urutan"),
                    pasal_data.get("metadata", {}),
                ),
                fetch="val",
            )
            logger.info(f"Pasal created/updated: {pasal_id}")
            return pasal_id
        except Exception as e:
            logger.error(f"Failed to create pasal: {e}")
            raise

    async def get_by_id(self, pasal_id: int) -> Optional[Dict[str, Any]]:
        """
        Get pasal by ID

        Args:
            pasal_id: ID pasal

        Returns:
            Dictionary data pasal atau None jika tidak ditemukan
        """
        select_query = """
        SELECT id, peraturan_id, bab_id, nomor_pasal, judul_pasal,
               konten_pasal, urutan, metadata, created_at, updated_at,
               (SELECT COUNT(*) FROM ayats WHERE pasal_id = pasals.id) as total_ayat
        FROM pasals
        WHERE id = $1
        """

        return await execute_query(select_query, args=(pasal_id,), fetch="one")

    async def get_list(
        self, peraturan_id: str, bab_id: Optional[int] = None, skip: int = 0, limit: int = 50
    ) -> Dict[str, Any]:
        """
        Get list pasal by peraturan_id atau bab_id dengan pagination

        Args:
            peraturan_id: ID peraturan
            bab_id: Filter by bab_id
            skip: Offset untuk pagination
            limit: Limit hasil per page

        Returns:
            Dictionary dengan total, skip, limit, dan items
        """
        # Build query dengan prepared statements
        conditions = ["peraturan_id = $1"]
        params = [peraturan_id]

        if bab_id is not None:
            conditions.append("bab_id = $2")
            params.append(bab_id)

        where_clause = f"WHERE {' AND '.join(conditions)}"

        # Get total count
        count_query = f"SELECT COUNT(*) FROM pasals {where_clause}"

        # Get data
        data_query = f"""
        SELECT id, peraturan_id, bab_id, nomor_pasal, judul_pasal,
               konten_pasal, urutan, metadata, created_at, updated_at,
               (SELECT COUNT(*) FROM ayats WHERE pasal_id = pasals.id) as total_ayat
        FROM pasals
        {where_clause}
        ORDER BY urutan ASC
        LIMIT ${len(params) + 1} OFFSET ${len(params) + 2}
        """

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
                    "items": [dict(item) for item in items],
                }
        except Exception as e:
            logger.error(f"Failed to get pasal list: {e}")
            return {"total": 0, "skip": skip, "limit": limit, "items": []}

    async def update(self, pasal_id: int, update_data: Dict[str, Any]) -> bool:
        """
        Update pasal

        Args:
            pasal_id: ID pasal
            update_data: Dictionary data untuk update

        Returns:
            True jika berhasil, False jika tidak
        """
        # Build SET clause dengan prepared statements
        allowed_fields = [
            "bab_id",
            "nomor_pasal",
            "judul_pasal",
            "konten_pasal",
            "urutan",
            "metadata",
        ]
        set_clauses = []
        params = []
        param_count = 0

        for key, value in update_data.items():
            if key in allowed_fields:
                param_count += 1
                set_clauses.append(f"{key} = ${param_count}")
                params.append(value)

        if not set_clauses:
            return False

        set_clauses.append("updated_at = CURRENT_TIMESTAMP")
        params.append(pasal_id)

        update_query = f"""
        UPDATE pasals
        SET {", ".join(set_clauses)}
        WHERE id = ${param_count + 1}
        """

        try:
            affected_rows = await execute_query(
                update_query, args=(*params, pasal_id), fetch="exec"
            )
            logger.info(f"Updated pasal {pasal_id}: {affected_rows} rows")
            return affected_rows > 0
        except Exception as e:
            logger.error(f"Failed to update pasal {pasal_id}: {e}")
            return False

    async def delete(self, pasal_id: int) -> bool:
        """
        Delete pasal

        Args:
            pasal_id: ID pasal

        Returns:
            True jika berhasil, False jika tidak
        """
        delete_query = "DELETE FROM pasals WHERE id = $1"

        try:
            affected_rows = await execute_query(delete_query, args=(pasal_id,), fetch="exec")
            logger.info(f"Deleted pasal {pasal_id}: {affected_rows} rows")
            return affected_rows > 0
        except Exception as e:
            logger.error(f"Failed to delete pasal {pasal_id}: {e}")
            return False

    async def search(
        self, query: str, peraturan_id: str, skip: int = 0, limit: int = 50
    ) -> Dict[str, Any]:
        """
        Search pasal dalam peraturan spesifik menggunakan full-text search

        Args:
            query: Search query (sudah disanitasi)
            peraturan_id: ID peraturan
            skip: Offset untuk pagination
            limit: Limit hasil per page

        Returns:
            Dictionary dengan total, skip, limit, dan items
        """
        # Sanitize query untuk tsquery
        tsquery = sanitize_search_query(query)

        search_query = """
        SELECT id, peraturan_id, bab_id, nomor_pasal, judul_pasal,
               konten_pasal, urutan, metadata, created_at, updated_at,
               ts_rank(to_tsvector('indonesian',
                       coalesce(nomor_pasal, '') || ' ' ||
                       coalesce(judul_pasal, '') || ' ' ||
                       konten_pasal),
                       plainto_tsquery('indonesian', $1)) as rank
        FROM pasals
        WHERE peraturan_id = $2
          AND to_tsvector('indonesian',
                       coalesce(nomor_pasal, '') || ' ' ||
                       coalesce(judul_pasal, '') || ' ' ||
                       konten_pasal)
              @@ plainto_tsquery('indonesian', $1)
        ORDER BY rank DESC, urutan ASC
        LIMIT $3 OFFSET $4
        """

        count_query = """
        SELECT COUNT(*)
        FROM pasals
        WHERE peraturan_id = $2
          AND to_tsvector('indonesian',
                       coalesce(nomor_pasal, '') || ' ' ||
                       coalesce(judul_pasal, '') || ' ' ||
                       konten_pasal)
              @@ plainto_tsquery('indonesian', $1)
        """

        try:
            async with get_db_connection() as conn:
                # Get total count
                total = await conn.fetchval(count_query, tsquery, peraturan_id)

                # Get data
                items = await conn.fetch(search_query, tsquery, peraturan_id, limit, skip)

                return {
                    "total": total,
                    "skip": skip,
                    "limit": limit,
                    "items": [dict(item) for item in items],
                }
        except Exception as e:
            logger.error(f"Failed to search pasal: {e}")
            return {"total": 0, "skip": skip, "limit": limit, "items": []}


# Singleton repository instance
pasal_repository = PasalRepository()
