"""
Repository untuk Tabel Bab
CRUD operations untuk tabel bab
"""

import asyncpg
from typing import List, Dict, Optional, Any
from datetime import datetime
import logging

# Import db connection management
from ..db.db import get_db_connection

# Import Bab model
from ..models.bab import (
    BabBase, BabCreate, BabUpdate, BabInDB, BabResponse,
    BabWithPasalCount, BabWithPeraturanInfo, BabListResponse
)

logger = logging.getLogger(__name__)


# ========================================
# Repository Class untuk Bab
# ========================================

class BabRepository:
    """Repository class untuk tabel bab"""

    async def create(self, bab_data: Dict[str, Any]) -> int:
        """
        Create bab baru di database

        Args:
            bab_data: Dictionary data bab

        Returns:
            ID bab yang dibuat
        """
        from ...models.bab import BabCreate

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

    async def get_by_id(self, bab_id: int) -> Optional[Dict[str, Any]]:
        """
        Get bab by ID

        Args:
            bab_id: ID bab

        Returns:
            Dictionary data bab atau None jika tidak ditemukan
        """
        select_query = """
        SELECT id, peraturan_id, nomor_bab, judul_bab, urutan,
               created_at, updated_at,
               (SELECT COUNT(*) FROM pasals WHERE bab_id = bab.id) as total_pasal
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

    async def get_list(
        self,
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

    async def update(self, bab_id: int, update_data: Dict[str, Any]) -> bool:
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
                logger.info(f"Updated bab {bab_id}: {affected_rows} rows")
                return int(affected_rows) > 0
        except Exception as e:
            logger.error(f"Failed to update bab {bab_id}: {e}")
            return False

    async def delete(self, bab_id: int) -> bool:
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
                logger.info(f"Deleted bab {bab_id}: {affected_rows} rows")
                return int(affected_rows) > 0
        except Exception as e:
            logger.error(f"Failed to delete bab {bab_id}: {e}")
            return False


# Singleton repository instance
bab_repository = BabRepository()
