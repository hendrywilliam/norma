"""
Repository for Bab Table
CRUD operations for bab table
"""

from typing import List, Dict, Optional, Any
from datetime import datetime
import logging

# Import db connection management
from db import get_db_connection, execute_query, validate_identifier

# Import Bab model
from models.bab import (
    BabBase,
    BabCreate,
    BabUpdate,
    BabInDB,
    BabResponse,
    BabWithPasalCount,
    BabWithPeraturanInfo,
    BabListResponse,
)

logger = logging.getLogger(__name__)


# ========================================
# Repository Class for Bab
# ========================================


class BabRepository:
    """Repository class for bab table"""

    async def create(self, bab_data: Dict[str, Any]) -> int:
        """
        Create new bab in database

        Args:
            bab_data: Dictionary of bab data

        Returns:
            ID of created bab

        Raises:
            Exception: If failed to create bab
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
            result = await execute_query(
                insert_query,
                args=(
                    bab_data.get("peraturan_id"),
                    bab_data.get("nomor_bab"),
                    bab_data.get("judul_bab"),
                    bab_data.get("urutan"),
                ),
                fetch="val",
            )
            if result is None:
                raise RuntimeError("Failed to create bab: no ID returned")
            bab_id: int = result
            logger.info(f"Bab created/updated: {bab_id}")
            return bab_id
        except Exception as e:
            logger.error(f"Failed to create bab: {e}")
            raise

    async def get_by_id(self, bab_id: int) -> Optional[Dict[str, Any]]:
        """
        Get bab by ID

        Args:
            bab_id: ID of bab

        Returns:
            Dictionary of bab data or None if not found
        """
        select_query = """
        SELECT id, peraturan_id, nomor_bab, judul_bab, urutan,
               created_at, updated_at,
               (SELECT COUNT(*) FROM pasals WHERE bab_id = bab.id) as total_pasal
        FROM bab
        WHERE id = $1
        """

        return await execute_query(select_query, args=(bab_id,), fetch="one")

    async def get_list(self, peraturan_id: str, skip: int = 0, limit: int = 50) -> Dict[str, Any]:
        """
        Get list of babs by peraturan_id with pagination

        Args:
            peraturan_id: ID of peraturan
            skip: Offset for pagination
            limit: Limit results per page

        Returns:
            Dictionary with total, skip, limit, and items
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
                    "items": [dict(item) for item in items],
                }
        except Exception as e:
            logger.error(f"Failed to get bab list for {peraturan_id}: {e}")
            return {"total": 0, "skip": skip, "limit": limit, "items": []}

    async def update(self, bab_id: int, update_data: Dict[str, Any]) -> bool:
        """
        Update bab

        Args:
            bab_id: ID of bab
            update_data: Dictionary of data for update

        Returns:
            True if successful, False otherwise
        """
        # Build SET clause with prepared statement
        allowed_fields = ["nomor_bab", "judul_bab", "urutan"]
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
        params.append(bab_id)

        update_query = f"""
        UPDATE bab
        SET {", ".join(set_clauses)}
        WHERE id = ${param_count + 1}
        """

        try:
            result = await execute_query(update_query, args=(*params, bab_id), fetch="exec")
            affected_rows = result if isinstance(result, int) else 0
            logger.info(f"Updated bab {bab_id}: {affected_rows} rows")
            return affected_rows > 0
        except Exception as e:
            logger.error(f"Failed to update bab {bab_id}: {e}")
            return False

    async def delete(self, bab_id: int) -> bool:
        """
        Delete bab

        Args:
            bab_id: ID of bab

        Returns:
            True if successful, False otherwise
        """
        delete_query = "DELETE FROM bab WHERE id = $1"

        try:
            result = await execute_query(delete_query, args=(bab_id,), fetch="exec")
            affected_rows: int = result if isinstance(result, int) else 0
            logger.info(f"Deleted bab {bab_id}: {affected_rows} rows")
            return affected_rows > 0
        except Exception as e:
            logger.error(f"Failed to delete bab {bab_id}: {e}")
            return False

    async def delete_by_peraturan(self, peraturan_id: str) -> int:
        """
        Delete all babs belonging to specific peraturan

        Args:
            peraturan_id: ID of peraturan

        Returns:
            Number of deleted babs
        """
        delete_query = "DELETE FROM bab WHERE peraturan_id = $1"

        try:
            result = await execute_query(delete_query, args=(peraturan_id,), fetch="exec")
            affected_rows: int = result if isinstance(result, int) else 0
            logger.info(f"Deleted {affected_rows} bab for peraturan {peraturan_id}")
            return affected_rows
        except Exception as e:
            logger.error(f"Failed to delete bab for peraturan {peraturan_id}: {e}")
            return 0


# Singleton repository instance
bab_repository = BabRepository()
