"""
Repository untuk Tabel Ayat
CRUD operations untuk tabel ayat
"""

from typing import List, Dict, Optional, Any
import logging
import json

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
            ayat_data: Dictionary data ayat dengan:
                - nomor_ayat: str
                - konten_ayat: str
                - urutan: int
                - pasal_id: int
                - bab_id: Optional[int]
                - peraturan_id: Optional[str]
                - metadata: Optional[dict]

        Returns:
            ID ayat yang dibuat

        Raises:
            Exception: Jika gagal membuat ayat
        """
        insert_query = """
        INSERT INTO ayats (
            nomor_ayat, konten_ayat, urutan, metadata, pasal_id, bab_id, peraturan_id
        )
        VALUES ($1, $2, $3, $4, $5, $6, $7)
        ON CONFLICT (pasal_id, nomor_ayat) DO UPDATE SET
            konten_ayat = EXCLUDED.konten_ayat,
            urutan = EXCLUDED.urutan,
            metadata = EXCLUDED.metadata,
            bab_id = EXCLUDED.bab_id,
            peraturan_id = EXCLUDED.peraturan_id,
            updated_at = CURRENT_TIMESTAMP
        RETURNING id
        """

        try:
            result = await execute_query(
                insert_query,
                args=(
                    ayat_data.get("nomor_ayat"),
                    ayat_data.get("konten_ayat"),
                    ayat_data.get("urutan"),
                    ayat_data.get("metadata", json.dumps({})),
                    ayat_data.get("pasal_id"),
                    ayat_data.get("bab_id"),
                    ayat_data.get("peraturan_id"),
                ),
                fetch="val",
            )
            if result is None:
                raise RuntimeError("Failed to create ayat: no ID returned")
            ayat_id: int = result
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
        SELECT id, nomor_ayat, konten_ayat, urutan, metadata, pasal_id, bab_id, peraturan_id,
               created_at, updated_at
        FROM ayats
        WHERE id = $1
        """

        return await execute_query(select_query, args=(ayat_id,), fetch="one")

    async def get_list_by_pasal(
        self, pasal_id: int, skip: int = 0, limit: int = 50
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
        SELECT id, nomor_ayat, konten_ayat, urutan, metadata, pasal_id, bab_id, peraturan_id,
               created_at, updated_at
        FROM ayats
        WHERE pasal_id = $1
        ORDER BY urutan ASC
        LIMIT $2 OFFSET $3
        """

        result = await execute_query(select_query, args=(pasal_id, limit, skip), fetch="all")
        return result if result else []

    async def get_list_by_peraturan(
        self, peraturan_id: str, skip: int = 0, limit: int = 10000
    ) -> List[Dict[str, Any]]:
        """
        Get list ayat untuk peraturan spesifik (menggunakan peraturan_id yang sudah di-denormalize)

        Args:
            peraturan_id: ID peraturan
            skip: Offset untuk pagination
            limit: Limit hasil per page

        Returns:
            List dari ayat dictionaries
        """
        select_query = """
        SELECT id, nomor_ayat, konten_ayat, urutan, metadata, pasal_id, bab_id, peraturan_id,
               created_at, updated_at
        FROM ayats
        WHERE peraturan_id = $1
        ORDER BY urutan ASC
        LIMIT $2 OFFSET $3
        """

        result = await execute_query(select_query, args=(peraturan_id, limit, skip), fetch="all")
        return result if result else []

    async def get_list_by_bab(
        self, bab_id: int, skip: int = 0, limit: int = 1000
    ) -> List[Dict[str, Any]]:
        """
        Get list ayat untuk bab spesifik

        Args:
            bab_id: ID bab
            skip: Offset untuk pagination
            limit: Limit hasil per page

        Returns:
            List dari ayat dictionaries
        """
        select_query = """
        SELECT id, nomor_ayat, konten_ayat, urutan, metadata, pasal_id, bab_id, peraturan_id,
               created_at, updated_at
        FROM ayats
        WHERE bab_id = $1
        ORDER BY urutan ASC
        LIMIT $2 OFFSET $3
        """

        result = await execute_query(select_query, args=(bab_id, limit, skip), fetch="all")
        return result if result else []


# Singleton repository instance
ayat_repository = AyatRepository()
