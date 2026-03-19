"""
Repository untuk Tabel Peraturan
CRUD operations untuk tabel peraturan
"""

import asyncpg
from typing import List, Dict, Optional, Any
from datetime import datetime
import logging

# Import db connection management
from ..db.db import get_db_connection

logger = logging.getLogger(__name__)


# ========================================
# Repository Class untuk Peraturan
# ========================================

class PeraturanRepository:
    """Repository class untuk tabel peraturan"""

    async def create(self, peraturan_data: Dict[str, Any]) -> str:
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
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11,
                $12, $13, $14, $15, $16, $17, $18, $19, $20, $21)
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

    async def get_by_id(self, peraturan_id: str) -> Optional[Dict[str, Any]]:
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

    async def get_list(
        self,
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

    async def update(self, peraturan_id: str, update_data: Dict[str, Any]) -> bool:
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

    async def delete(self, peraturan_id: str) -> bool:
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

    async def search(
        self,
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
               jenis_peraturan, pemrakarsa, tentang, status_peraturan,
               created_at, updated_at, parsed_at, reparse_count,
               ts_rank(to_tsvector('indonesian', judul || ' ' || COALESCE(nomor, '') || ' ' || COALESCE(tentang, '')),
                       plainto_tsquery('indonesian', $1)) as rank
        FROM peraturan
        WHERE to_tsvector('indonesian', judul || ' ' || COALESCE(nomor, '') || ' ' || COALESCE(tentang, ''))
              @@ plainto_tsquery('indonesian', $1)
        ORDER BY rank DESC, created_at DESC
        LIMIT $2 OFFSET $3
        """

        count_query = """
        SELECT COUNT(*)
        FROM peraturan
        WHERE to_tsvector('indonesian', judul || ' ' || COALESCE(nomor, '') || ' ' || COALESCE(tentang, ''))
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

    async def get_stats(self) -> Dict[str, Any]:
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


# Singleton repository instance
peraturan_repository = PeraturanRepository()
