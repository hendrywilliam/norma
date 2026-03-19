-- Migration 002: Create Indexes
-- File ini untuk membuat indexes untuk performa query di semua tabel

-- ========================================
-- 1. INDEXES untuk tabel peraturan
-- ========================================

-- Basic indexes untuk filter dan sorting
CREATE INDEX IF NOT EXISTS idx_peraturan_kategori ON peraturan(kategori);
CREATE INDEX IF NOT EXISTS idx_peraturan_tahun ON peraturan(tahun);
CREATE INDEX IF NOT EXISTS idx_peraturan_nomor ON peraturan(nomor);
CREATE INDEX IF NOT EXISTS idx_peraturan_created_at ON peraturan(created_at);
CREATE INDEX IF NOT EXISTS idx_peraturan_updated_at ON peraturan(updated_at);
CREATE INDEX IF NOT EXISTS idx_peraturan_parsed_at ON peraturan(parsed_at);
CREATE INDEX IF NOT EXISTS idx_peraturan_tanggal_disahkan ON peraturan(tanggal_disahkan);
CREATE INDEX IF NOT EXISTS idx_peraturan_tanggal_diundangkan ON peraturan(tanggal_diundangkan);
CREATE INDEX IF NOT EXISTS idx_peraturan_tanggal_ditetapkan ON peraturan(tanggal_ditetapkan);
CREATE INDEX IF NOT EXISTS idx_peraturan_jenis_peraturan ON peraturan(jenis_peraturan);
CREATE INDEX IF NOT EXISTS idx_peraturan_pemrakarsa ON peraturan(pemrakarsa);
CREATE INDEX IF NOT EXISTS idx_peraturan_tentang ON peraturan(tentang);
CREATE INDEX IF NOT EXISTS idx_peraturan_status_peraturan ON peraturan(status_peraturan);

-- Full-text search index untuk Indonesian language
-- Index ini memungkinkan pencarian cepat dengan to_tsvector
CREATE INDEX IF NOT EXISTS idx_peraturan_search
ON peraturan USING gin(to_tsvector('indonesian', judul || ' ' || COALESCE(nomor, '') || ' ' || COALESCE(tentang, '')));

-- Trigram index untuk fuzzy search dan partial matching
-- Berguna untuk pencarian dengan typo atau partial string
CREATE INDEX IF NOT EXISTS idx_peraturan_judul_trgm
ON peraturan USING gin(judul gin_trgm_ops);

CREATE INDEX IF NOT EXISTS idx_peraturan_tentang_trgm
ON peraturan USING gin(tentang gin_trgm_ops);

-- Composite indexes untuk common queries
CREATE INDEX IF NOT EXISTS idx_peraturan_kategori_tahun ON peraturan(kategori, tahun);
CREATE INDEX IF NOT EXISTS idx_peraturan_tahun_kategori ON peraturan(tahun, kategori);
CREATE INDEX IF NOT EXISTS idx_peraturan_kategori_status ON peraturan(kategori, status_peraturan);
CREATE INDEX IF NOT EXISTS idx_peraturan_tahun_status ON peraturan(tahun, status_peraturan);
CREATE INDEX IF NOT EXISTS idx_peraturan_kategori_tahun_status ON peraturan(kategori, tahun, status_peraturan);

-- Index untuk JSONB fields (metadata)
CREATE INDEX IF NOT EXISTS idx_peraturan_metadata ON peraturan USING gin(metadata);

-- Index untuk reparse tracking
CREATE INDEX IF NOT EXISTS idx_peraturan_reparse_count ON peraturan(reparse_count);
CREATE INDEX IF NOT EXISTS idx_peraturan_last_reparse_at ON peraturan(last_reparse_at);

-- Index untuk popularity (jumlah_dilihat dan jumlah_download)
CREATE INDEX IF NOT EXISTS idx_peraturan_jumlah_dilihat ON peraturan(jumlah_dilihat DESC);
CREATE INDEX IF NOT EXISTS idx_peraturan_jumlah_download ON peraturan(jumlah_download DESC);

-- ========================================
-- 2. INDEXES untuk tabel bab
-- ========================================

-- Foreign key indexes untuk quick lookup
CREATE INDEX IF NOT EXISTS idx_bab_peraturan_id ON bab(peraturan_id);

-- Index untuk sorting dan filtering
CREATE INDEX IF NOT EXISTS idx_bab_urutan ON bab(urutan);
CREATE INDEX IF NOT EXISTS idx_bab_nomor_bab ON bab(nomor_bab);

-- Composite index untuk get bab by peraturan with ordering
CREATE INDEX IF NOT EXISTS idx_bab_peraturan_id_urutan ON bab(peraturan_id, urutan);

-- Full-text search untuk judul bab
CREATE INDEX IF NOT EXISTS idx_bab_judul_bab_search
ON bab USING gin(to_tsvector('indonesian', COALESCE(judul_bab, '') || ' ' || nomor_bab));

-- ========================================
-- 3. INDEXES untuk tabel pasals
-- ========================================

-- Foreign key indexes untuk quick lookup
CREATE INDEX IF NOT EXISTS idx_pasals_peraturan_id ON pasals(peraturan_id);
CREATE INDEX IF NOT EXISTS idx_pasals_bab_id ON pasals(bab_id);

-- Index untuk sorting dan filtering
CREATE INDEX IF NOT EXISTS idx_pasals_urutan ON pasals(urutan);
CREATE INDEX IF NOT EXISTS idx_pasals_nomor ON pasals(nomor_pasal);

-- Full-text search index untuk Indonesian language
-- Index ini memungkinkan pencarian cepat di konten pasal
CREATE INDEX IF NOT EXISTS idx_pasals_search
ON pasals USING gin(to_tsvector('indonesian', nomor_pasal || ' ' || COALESCE(judul_pasal, '') || ' ' || konten_pasal));

-- Trigram index untuk fuzzy search di judul pasal
CREATE INDEX IF NOT EXISTS idx_pasals_judul_trgm
ON pasals USING gin(judul_pasal gin_trgm_ops);

-- Composite indexes untuk common queries
CREATE INDEX IF NOT EXISTS idx_pasals_peraturan_id_urutan ON pasals(peraturan_id, urutan);
CREATE INDEX IF NOT EXISTS idx_pasals_bab_id_urutan ON pasals(bab_id, urutan);
CREATE INDEX IF NOT EXISTS idx_pasals_peraturan_bab_urutan ON pasals(peraturan_id, bab_id, urutan);

-- Index untuk JSONB fields (metadata)
CREATE INDEX IF NOT EXISTS idx_pasals_metadata ON pasals USING gin(metadata);

-- ========================================
-- 4. INDEXES untuk tabel ayats
-- ========================================

-- Foreign key indexes untuk quick lookup
CREATE INDEX IF NOT EXISTS idx_ayats_pasal_id ON ayats(pasal_id);

-- Index untuk sorting dan filtering
CREATE INDEX IF NOT EXISTS idx_ayats_urutan ON ayats(urutan);
CREATE INDEX IF NOT EXISTS idx_ayats_nomor_ayat ON ayats(nomor_ayat);

-- Full-text search index untuk Indonesian language
-- Index ini memungkinkan pencarian cepat di konten ayat
CREATE INDEX IF NOT EXISTS idx_ayats_search
ON ayats USING gin(to_tsvector('indonesian', nomor_ayat || ' ' || konten_ayat));

-- Composite index untuk get ayats by pasal with ordering
CREATE INDEX IF NOT EXISTS idx_ayats_pasal_id_urutan ON ayats(pasal_id, urutan);

-- Index untuk JSONB fields (metadata)
CREATE INDEX IF NOT EXISTS idx_ayats_metadata ON ayats USING gin(metadata);

-- ========================================
-- 5. INDEXES untuk tabel parsing_logs
-- ========================================

-- Foreign key indexes untuk quick lookup
CREATE INDEX IF NOT EXISTS idx_parsing_logs_peraturan_id ON parsing_logs(peraturan_id);

-- Index untuk filtering dan sorting
CREATE INDEX IF NOT EXISTS idx_parsing_logs_status ON parsing_logs(status);
CREATE INDEX IF NOT EXISTS idx_parsing_logs_action ON parsing_logs(action);
CREATE INDEX IF NOT EXISTS idx_parsing_logs_parsed_at ON parsing_logs(parsed_at DESC);
CREATE INDEX IF NOT EXISTS idx_parsing_logs_error_message ON parsing_logs(error_message) WHERE error_message IS NOT NULL;

-- Composite indexes untuk common queries
CREATE INDEX IF NOT EXISTS idx_parsing_logs_peraturan_status ON parsing_logs(peraturan_id, status);
CREATE INDEX IF NOT EXISTS idx_parsing_logs_peraturan_parsed_at ON parsing_logs(peraturan_id, parsed_at DESC);
CREATE INDEX IF NOT EXISTS idx_parsing_logs_status_parsed_at ON parsing_logs(status, parsed_at DESC);

-- Index untuk JSONB fields (metadata)
CREATE INDEX IF NOT EXISTS idx_parsing_logs_metadata ON parsing_logs USING gin(metadata);
