"""
Repository untuk Tabel Ayat
CRUD operations untuk tabel ayat
"""

from typing import List, Dict, Optional, Any
import logging

# Import db connection management
from db import get_db_connection, execute_query

logger = logging.getLogger(__name__)


# ========================================
# Repository Class untuk Ayat
# ========================================

class AyatRepository:
    """Repository class untuk tabel ayat"""

    async def create(self, ayat_data: Dict[str, Any]) -> int:
        """
        Create ayat baru di database

        Args:
            ayat_data: Dictionary data ayat

        Returns:
            ID ayat yang dibuat
        """
        insert_query = """
        INSERT INTO ayat (
            ayat_number, isi, pasal_id, peraturan_id
        )
        VALUES ($1, $2, $3, $4)
        ON CONFLICT (id) DO UPDATE SET
            ayat_number = EXCLUDED.ayat_number,
            isi = EXCLUDED.isi,
            pasal_id = EXCLUDED.pasal_id,
            peraturan_id = EXCLUDED.peraturan_id
        RETURNING id
        """

        try:
            ayat_id = await execute_query(
                insert_query,
                args=(
                    ayat_data.get('ayat_number'),
                    ayat_data.get('isi'),
                    ayat_data.get('pasal_id'),
                    ayat_data.get('peraturan_id')
                ),
                fetch="val"
            )
            logger.info(f"Ayat created/updated: {ayat_id}")
            return ayat_id
        except Exception as e:
            logger.error(f"Failed to create ayat: {e}")
            raise

    async def get_by_id(self, ayat_id: int) -> Optional[Dict[str, Any]]:
        """
        Get ayat by ID

        Args:
            ayat_id: ID ayat

        Returns:
            Dictionary data ayat atau None jika tidak ditemukan
        """
        select_query = """
        SELECT id, ayat_number, isi, pasal_id, peraturan_id,
               created_at, updated_at
        FROM ayat
        WHERE id = $1
        """

        return await execute_query(select_query, args=(ayat_id,), fetch="one")

    async def get_list_by_pasal(
        self,
        pasal_id: int,
        skip: int = 0,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Get list ayat untuk pasal spesifik

        Args:
            pasal_id: ID pasal
            skip: Offset untuk pagination
            limit: Limit hasil per page

        Returns:
            List dari ayat dictionaries
        """
        select_query = """
        SELECT id, ayat_number, isi, pasal_id, peraturan_id,
               created_at, updated_at
        FROM ayat
        WHERE pasal_id = $1
        ORDER BY ayat_number ASC
        LIMIT $2 OFFSET $3
        """

        result = await execute_query(select_query, args=(pasal_id, limit, skip), fetch="all")
        return result if result else []

    async def get_list_by_peraturan(
        self,
        peraturan_id: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Get list ayat untuk peraturan spesifik

        Args:
            peraturan_id: ID peraturan
            skip: Offset untuk pagination
            limit: Limit hasil per page

        Returns:
            List dari ayat dictionaries
        """
        select_query = """
        SELECT id, ayat_number, isi, pasal_id, peraturan_id,
               created_at, updated_at
        FROM ayat
        WHERE peraturan_id = $1
        ORDER BY pasal_id, ayat_number ASC
        LIMIT $2 OFFSET $3
        """

        result = await execute_query(select_query, args=(peraturan_id, limit, skip), fetch="all")
        return result if result else []

    async def delete(self, ayat_id: int) -> bool:
        """
        Delete ayat

        Args:
            ayat_id: ID ayat

        Returns:
            True jika berhasil, False jika tidak
        """
        delete_query = "DELETE FROM ayat WHERE id = $1"

        try:
            affected_rows = await execute_query(delete_query, args=(ayat_id,), fetch="exec")
            logger.info(f"Deleted ayat {ayat_id}: {affected_rows} rows")
            return affected_rows > 0
        except Exception as e:
            logger.error(f"Failed to delete ayat {ayat_id}: {e}")
            return False


# Singleton repository instance
ayat_repository = AyatRepository()
