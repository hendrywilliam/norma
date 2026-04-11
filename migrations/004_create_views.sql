-- Migration 004: Create Views
-- File ini untuk membuat views untuk monitoring dan reporting semua tabel

-- ========================================
-- 1. VIEWS untuk tabel peraturan
-- ========================================

-- View untuk statistik umum peraturan
CREATE OR REPLACE VIEW peraturan_stats AS
SELECT
    COUNT(*) as total_peraturan,
    COUNT(DISTINCT kategori) as total_kategori,
    COUNT(DISTINCT tahun) as total_tahun,
    COUNT(DISTINCT jenis_peraturan) as total_jenis,
    MIN(tahun) as tahun_pertama,
    MAX(tahun) as tahun_terakhir,
    MIN(created_at) as pertama_dibuat,
    MAX(created_at) as terakhir_dibuat,
    MIN(parsed_at) as pertama_diparse,
    MAX(parsed_at) as terakhir_diparse,
    AVG(reparse_count) as rata_reparse,
    SUM(CASE WHEN pdf_url IS NOT NULL THEN 1 ELSE 0 END) as total_dengan_pdf,
    (SELECT COUNT(*) FROM bab) as total_bab,
    (SELECT COUNT(*) FROM pasals) as total_pasal,
    (SELECT COUNT(*) FROM ayats) as total_ayat,
    (SELECT COUNT(*) FROM pasals WHERE peraturan_id = peraturan.id) as pasal_count,
    AVG((SELECT COUNT(*) FROM pasals WHERE peraturan_id = peraturan.id)) as rata_pasal_per_peraturan,
    COUNT(CASE WHEN (SELECT COUNT(*) FROM pasals WHERE peraturan_id = peraturan.id) > 0 THEN 1 ELSE 0 END) as total_dengan_pasal,
    COUNT(CASE WHEN (SELECT COUNT(*) FROM pasals WHERE peraturan_id = peraturan.id) = 0 THEN 1 ELSE 0 END) as total_tanpa_pasal
FROM peraturan;

-- View untuk peraturan dikelompokkan by kategori
CREATE OR REPLACE VIEW peraturan_by_kategori AS
SELECT
    kategori,
    COUNT(*) as jumlah,
    COUNT(DISTINCT tahun) as jumlah_tahun,
    MIN(tahun) as tahun_pertama,
    MAX(tahun) as tahun_terakhir,
    AVG(reparse_count) as rata_reparse,
    AVG((SELECT COUNT(*) FROM pasals WHERE peraturan_id = peraturan.id)) as rata_pasal,
    COUNT(CASE WHEN (SELECT COUNT(*) FROM pasals WHERE peraturan_id = peraturan.id) > 0 THEN 1 ELSE 0 END) as jumlah_dengan_pasal,
    COUNT(CASE WHEN (SELECT COUNT(*) FROM pasals WHERE peraturan_id = peraturan.id) = 0 THEN 1 ELSE 0 END) as jumlah_tanpa_pasal,
    SUM(CASE WHEN pdf_url IS NOT NULL THEN 1 ELSE 0 END) as jumlah_dengan_pdf,
    AVG(jumlah_dilihat) as rata_dilihat,
    AVG(jumlah_download) as rata_download,
    MIN(created_at) as pertama_dibuat,
    MAX(created_at) as terakhir_dibuat,
    array_agg(DISTINCT jenis_peraturan ORDER BY jenis_peraturan) as jenis_peraturan
FROM peraturan
GROUP BY kategori
ORDER BY jumlah DESC;

-- View untuk peraturan dikelompokkan by tahun (10 tahun terakhir)
CREATE OR REPLACE VIEW peraturan_by_tahun AS
SELECT
    tahun,
    COUNT(*) as jumlah,
    COUNT(DISTINCT kategori) as jumlah_kategori,
    COUNT(DISTINCT jenis_peraturan) as jumlah_jenis,
    array_agg(DISTINCT kategori ORDER BY kategori) as kategori,
    array_agg(DISTINCT jenis_peraturan ORDER BY jenis_peraturan) as jenis_peraturan,
    AVG(reparse_count) as rata_reparse,
    AVG((SELECT COUNT(*) FROM pasals WHERE peraturan_id = peraturan.id)) as rata_pasal,
    COUNT(CASE WHEN (SELECT COUNT(*) FROM pasals WHERE peraturan_id = peraturan.id) > 0 THEN 1 ELSE 0 END) as jumlah_dengan_pasal,
    AVG(jumlah_dilihat) as rata_dilihat,
    AVG(jumlah_download) as rata_download
FROM peraturan
WHERE tahun >= EXTRACT(YEAR FROM CURRENT_DATE) - 10
GROUP BY tahun
ORDER BY tahun DESC;

-- View untuk 50 peraturan terbaru yang diparse
CREATE OR REPLACE VIEW peraturan_terbaru_diparse AS
SELECT
    id,
    judul,
    nomor,
    tahun,
    kategori,
    jenis_peraturan,
    tentang,
    status_peraturan,
    url,
    pdf_url,
    created_at,
    updated_at,
    parsed_at,
    reparse_count,
    (SELECT COUNT(*) FROM bab WHERE peraturan_id = peraturan.id) as total_bab,
    (SELECT COUNT(*) FROM pasals WHERE peraturan_id = peraturan.id) as total_pasal,
    (SELECT COUNT(*) FROM ayats WHERE pasal_id IN (SELECT id FROM pasals WHERE peraturan_id = peraturan.id)) as total_ayat
FROM peraturan
WHERE parsed_at IS NOT NULL
ORDER BY parsed_at DESC
LIMIT 50;

-- View untuk 50 peraturan terbaru yang dibuat di database
CREATE OR REPLACE VIEW peraturan_terbaru_dibuat AS
SELECT
    id,
    judul,
    nomor,
    tahun,
    kategori,
    jenis_peraturan,
    tentang,
    status_peraturan,
    url,
    pdf_url,
    created_at,
    updated_at,
    parsed_at,
    reparse_count,
    (SELECT COUNT(*) FROM bab WHERE peraturan_id = peraturan.id) as total_bab,
    (SELECT COUNT(*) FROM pasals WHERE peraturan_id = peraturan.id) as total_pasal
FROM peraturan
ORDER BY created_at DESC
LIMIT 50;

-- View untuk peraturan yang perlu di-reparse
-- Criteria: lama diparse (> 180 hari) atau reparse_count rendah (< 2)
CREATE OR REPLACE VIEW peraturan_perlu_reparse AS
SELECT
    id,
    judul,
    nomor,
    tahun,
    kategori,
    jenis_peraturan,
    status_peraturan,
    url,
    pdf_url,
    created_at,
    updated_at,
    parsed_at,
    reparse_count,
    EXTRACT(DAY FROM CURRENT_TIMESTAMP - COALESCE(parsed_at, created_at)) as hari_sejak_terakhir,
    (SELECT COUNT(*) FROM pasals WHERE peraturan_id = peraturan.id) as total_pasal,
    CASE
        WHEN parsed_at IS NULL THEN 10
        WHEN (SELECT COUNT(*) FROM pasals WHERE peraturan_id = peraturan.id) = 0 THEN 9
        WHEN EXTRACT(DAY FROM CURRENT_TIMESTAMP - parsed_at) > 180 THEN 8
        WHEN reparse_count < 2 THEN 5
        ELSE 1
    END as prioritas_reparse
FROM peraturan
WHERE
    parsed_at IS NULL
    OR EXTRACT(DAY FROM CURRENT_TIMESTAMP - COALESCE(parsed_at, created_at)) > 180
    OR reparse_count < 2
    OR (SELECT COUNT(*) FROM pasals WHERE peraturan_id = peraturan.id) = 0
ORDER BY prioritas_reparse DESC, COALESCE(parsed_at, created_at) ASC;

-- View untuk peraturan dengan error parsing
CREATE OR REPLACE VIEW peraturan_error_parsing AS
SELECT
    id,
    judul,
    nomor,
    tahun,
    kategori,
    jenis_peraturan,
    status_peraturan,
    url,
    pdf_url,
    created_at,
    updated_at,
    parsed_at,
    reparse_count,
    (SELECT COUNT(*) FROM pasals WHERE peraturan_id = peraturan.id) as total_pasal,
    (SELECT COUNT(*) FROM parsing_logs WHERE peraturan_id = peraturan.id AND status = 'failed') as total_error,
    (SELECT MAX(error_message) FROM parsing_logs WHERE peraturan_id = peraturan.id AND status = 'failed') as error_terakhir
FROM peraturan
WHERE (SELECT COUNT(*) FROM parsing_logs WHERE peraturan_id = peraturan.id AND status = 'failed') > 0
    AND (SELECT COUNT(*) FROM pasals WHERE peraturan_id = peraturan.id) = 0
ORDER BY created_at DESC;

-- ========================================
-- 2. VIEWS untuk peraturan dengan bab dan pasals
-- ========================================

-- View untuk peraturan dengan count pasal
CREATE OR REPLACE VIEW peraturan_with_pasal_count AS
SELECT
    p.*,
    COUNT(DISTINCT ps.id) as total_pasal,
    COUNT(DISTINCT b.id) as total_bab,
    COUNT(DISTINCT a.id) as total_ayat,
    SUM(LENGTH(ps.konten_pasal)) as total_karakter_pasal,
    MIN(ps.urutan) as pasal_pertama,
    MAX(ps.urutan) as pasal_terakhir,
    MIN(b.urutan) as bab_pertama,
    MAX(b.urutan) as bab_terakhir
FROM peraturan p
LEFT JOIN bab b ON p.id = b.peraturan_id
LEFT JOIN pasals ps ON b.id = ps.bab_id OR ps.peraturan_id = p.id
LEFT JOIN ayats a ON ps.id = a.pasal_id
GROUP BY p.id;

-- View untuk peraturan dengan semua bab dan pasals
CREATE OR REPLACE VIEW peraturan_with_bab_pasals AS
SELECT
    p.id,
    p.judul,
    p.nomor,
    p.tahun,
    p.kategori,
    p.jenis_peraturan,
    p.tentang,
    p.status_peraturan,
    p.created_at,
    p.parsed_at,
    b.id as bab_id,
    b.nomor_bab,
    b.judul_bab,
    b.urutan as bab_urutan,
    ps.id as pasal_id,
    ps.nomor_pasal,
    ps.judul_pasal,
    ps.konten_pasal,
    ps.urutan as pasal_urutan
FROM peraturan p
LEFT JOIN bab b ON p.id = b.peraturan_id
LEFT JOIN pasals ps ON b.id = ps.bab_id
ORDER BY p.id, b.urutan, ps.urutan;

-- View untuk bab dengan semua pasals
CREATE OR REPLACE VIEW bab_with_pasals AS
SELECT
    b.*,
    p.judul as judul_peraturan,
    p.nomor as nomor_peraturan,
    p.tahun as tahun_peraturan,
    p.kategori as kategori_peraturan,
    COUNT(ps.id) as total_pasal,
    array_agg(ps.nomor_pasal ORDER BY ps.urutan) as daftar_pasal
FROM bab b
LEFT JOIN peraturan p ON b.peraturan_id = p.id
LEFT JOIN pasals ps ON b.id = ps.bab_id
GROUP BY b.id, p.id
ORDER BY b.peraturan_id, b.urutan;

-- ========================================
-- 3. VIEWS untuk pasals dengan bab dan peraturan
-- ========================================

-- View untuk pasal dengan informasi bab dan peraturan
CREATE OR REPLACE VIEW pasals_with_bab_peraturan AS
SELECT
    ps.id,
    ps.peraturan_id,
    ps.bab_id,
    ps.nomor_pasal,
    ps.judul_pasal,
    ps.konten_pasal,
    ps.urutan,
    ps.metadata,
    ps.created_at,
    ps.updated_at,
    b.nomor_bab,
    b.judul_bab as judul_bab,
    b.urutan as bab_urutan,
    p.judul as judul_peraturan,
    p.nomor as nomor_peraturan,
    p.tahun as tahun_peraturan,
    p.kategori as kategori_peraturan,
    p.jenis_peraturan,
    p.tentang,
    p.status_peraturan,
    COUNT(a.id) as total_ayat,
    array_agg(a.nomor_ayat ORDER BY a.urutan) as daftar_ayat
FROM pasals ps
LEFT JOIN bab b ON ps.bab_id = b.id
LEFT JOIN peraturan p ON ps.peraturan_id = p.id
LEFT JOIN ayats a ON ps.id = a.pasal_id
GROUP BY ps.id, b.id, p.id
ORDER BY ps.peraturan_id, ps.urutan;

-- ========================================
-- 4. VIEWS untuk ayats dengan pasal, bab, dan peraturan
-- ========================================

-- View untuk ayat dengan informasi pasal, bab, dan peraturan
CREATE OR REPLACE VIEW ayats_with_pasal_bab_peraturan AS
SELECT
    a.id,
    a.pasal_id,
    a.nomor_ayat,
    a.konten_ayat,
    a.urutan,
    a.metadata,
    a.created_at,
    a.updated_at,
    ps.nomor_pasal,
    ps.judul_pasal as judul_pasal,
    ps.urutan as pasal_urutan,
    b.nomor_bab,
    b.judul_bab as judul_bab,
    b.urutan as bab_urutan,
    ps.peraturan_id,
    p.judul as judul_peraturan,
    p.nomor as nomor_peraturan,
    p.tahun as tahun_peraturan,
    p.kategori as kategori_peraturan,
    p.jenis_peraturan,
    p.tentang
FROM ayats a
JOIN pasals ps ON a.pasal_id = ps.id
LEFT JOIN bab b ON ps.bab_id = b.id
JOIN peraturan p ON ps.peraturan_id = p.id
ORDER BY ps.peraturan_id, ps.urutan, a.urutan;

-- View untuk peraturan detail lengkap (semua bab, pasals, dan ayats)
CREATE OR REPLACE VIEW peraturan_detail_lengkap AS
SELECT
    p.id as peraturan_id,
    p.judul as judul_peraturan,
    p.nomor as nomor_peraturan,
    p.tahun as tahun_peraturan,
    p.kategori,
    p.jenis_peraturan,
    p.tentang,
    p.status_peraturan,
    p.pemrakarsa,
    p.tempat_penetapan,
    p.pejabat_menetapkan,
    b.id as bab_id,
    b.nomor_bab,
    b.judul_bab,
    b.urutan as bab_urutan,
    ps.id as pasal_id,
    ps.nomor_pasal,
    ps.judul_pasal,
    ps.konten_pasal,
    ps.urutan as pasal_urutan,
    a.id as ayat_id,
    a.nomor_ayat,
    a.konten_ayat,
    a.urutan as ayat_urutan
FROM peraturan p
LEFT JOIN bab b ON p.id = b.peraturan_id
LEFT JOIN pasals ps ON b.id = ps.bab_id
LEFT JOIN ayats a ON ps.id = a.pasal_id
ORDER BY p.id, b.urutan, ps.urutan, a.urutan;

-- ========================================
-- 5. VIEWS untuk parsing_logs
-- ========================================

-- View untuk statistik parsing operations
CREATE OR REPLACE VIEW parsing_statistics AS
SELECT
    action,
    status,
    COUNT(*) as total,
    COUNT(DISTINCT peraturan_id) as unique_peraturan,
    MIN(parsed_at) as pertama,
    MAX(parsed_at) as terakhir,
    AVG(EXTRACT(EPOCH FROM (
        COALESCE(parsed_at, CURRENT_TIMESTAMP) - LAG(parsed_at) OVER (PARTITION BY action ORDER BY parsed_at)
    ))) as avg_interval_seconds,
    SUM((metadata->>'duration_seconds')::INTEGER) as total_duration_seconds,
    AVG((metadata->>'duration_seconds')::INTEGER) as avg_duration_seconds,
    AVG((metadata->>'bab_count')::INTEGER) as avg_bab_count,
    AVG((metadata->>'pasal_count')::INTEGER) as avg_pasal_count,
    AVG((metadata->>'ayat_count')::INTEGER) as avg_ayat_count
FROM parsing_logs
GROUP BY action, status
ORDER BY action, status;

-- View untuk trending peraturan (sering diakses/di-parse)
CREATE OR REPLACE VIEW trending_peraturan AS
SELECT
    p.id,
    p.judul,
    p.nomor,
    p.tahun,
    p.kategori,
    p.jenis_peraturan,
    p.tentang,
    p.status_peraturan,
    p.url,
    p.created_at,
    p.updated_at,
    p.parsed_at,
    p.reparse_count,
    p.jumlah_dilihat,
    p.jumlah_download,
    (SELECT COUNT(*) FROM parsing_logs WHERE peraturan_id = p.id) as total_operations,
    (SELECT COUNT(*) FROM parsing_logs WHERE peraturan_id = p.id AND parsed_at > CURRENT_TIMESTAMP - INTERVAL '30 days') as operations_last_30_days,
    (SELECT COUNT(*) FROM parsing_logs WHERE peraturan_id = p.id AND parsed_at > CURRENT_TIMESTAMP - INTERVAL '7 days') as operations_last_7_days,
    (SELECT COUNT(*) FROM parsing_logs WHERE peraturan_id = p.id AND status = 'failed') as total_failed,
    CASE
        WHEN (SELECT COUNT(*) FROM parsing_logs WHERE peraturan_id = p.id AND parsed_at > CURRENT_TIMESTAMP - INTERVAL '30 days') > 5 THEN 'high'
        WHEN (SELECT COUNT(*) FROM parsing_logs WHERE peraturan_id = p.id AND parsed_at > CURRENT_TIMESTAMP - INTERVAL '30 days') > 2 THEN 'medium'
        ELSE 'low'
    END as trending_level,
    (SELECT COUNT(*) FROM pasals WHERE peraturan_id = p.id) as total_pasal
FROM peraturan p
WHERE (SELECT COUNT(*) FROM parsing_logs WHERE peraturan_id = p.id) > 0
ORDER BY operations_last_30_days DESC, p.reparse_count DESC, p.jumlah_dilihat DESC
LIMIT 50;

-- View untuk parsing history per peraturan
CREATE OR REPLACE VIEW peraturan_parsing_history AS
SELECT
    pl.id,
    pl.peraturan_id,
    p.judul as judul_peraturan,
    p.nomor as nomor_peraturan,
    p.tahun as tahun_peraturan,
    p.kategori,
    pl.action,
    pl.status,
    pl.error_message,
    pl.parsed_at,
    pl.metadata,
    EXTRACT(SECOND FROM (pl.parsed_at - LAG(pl.parsed_at) OVER (PARTITION BY pl.peraturan_id ORDER BY pl.parsed_at))) as duration_from_previous
FROM parsing_logs pl
LEFT JOIN peraturan p ON pl.peraturan_id = p.id
ORDER BY pl.peraturan_id, pl.parsed_at DESC;

-- ========================================
-- 6. VIEWS untuk monitoring dan health
-- ========================================

-- View untuk health check database
CREATE OR REPLACE VIEW database_health AS
SELECT
    'peraturan' as table_name,
    COUNT(*) as total_rows,
    COUNT(DISTINCT kategori) as unique_categories,
    COUNT(DISTINCT tahun) as unique_years,
    MIN(created_at) as oldest_record,
    MAX(created_at) as newest_record,
    COUNT(CASE WHEN pdf_url IS NOT NULL THEN 1 END) as rows_with_pdf,
    COUNT(CASE WHEN (SELECT COUNT(*) FROM pasals WHERE peraturan_id = peraturan.id) > 0 THEN 1 END) as rows_with_pasal,
    COUNT(CASE WHEN (SELECT COUNT(*) FROM pasals WHERE peraturan_id = peraturan.id) = 0 THEN 1 END) as rows_without_pasal,
    AVG(reparse_count) as avg_reparse_count
FROM peraturan
UNION ALL
SELECT
    'bab' as table_name,
    COUNT(*) as total_rows,
    0 as unique_categories,
    0 as unique_years,
    MIN(created_at) as oldest_record,
    MAX(created_at) as newest_record,
    0 as rows_with_pdf,
    0 as rows_with_pasal,
    0 as rows_without_pasal,
    0 as avg_reparse_count
FROM bab
UNION ALL
SELECT
    'pasals' as table_name,
    COUNT(*) as total_rows,
    COUNT(DISTINCT (SELECT kategori FROM peraturan WHERE id = pasals.peraturan_id)) as unique_categories,
    COUNT(DISTINCT (SELECT tahun FROM peraturan WHERE id = pasals.peraturan_id)) as unique_years,
    MIN(created_at) as oldest_record,
    MAX(created_at) as newest_record,
    0 as rows_with_pdf,
    0 as rows_with_pasal,
    0 as rows_without_pasal,
    0 as avg_reparse_count
FROM pasals
UNION ALL
SELECT
    'ayats' as table_name,
    COUNT(*) as total_rows,
    0 as unique_categories,
    0 as unique_years,
    MIN(created_at) as oldest_record,
    MAX(created_at) as newest_record,
    0 as rows_with_pdf,
    0 as rows_with_pasal,
    0 as rows_without_pasal,
    0 as avg_reparse_count
FROM ayats
UNION ALL
SELECT
    'parsing_logs' as table_name,
    COUNT(*) as total_rows,
    0 as unique_categories,
    0 as unique_years,
    MIN(parsed_at) as oldest_record,
    MAX(parsed_at) as newest_record,
    0 as rows_with_pdf,
    0 as rows_with_pasal,
    0 as rows_without_pasal,
    0 as avg_reparse_count
FROM parsing_logs;

-- ========================================
-- Log completion
-- ========================================

DO $$
BEGIN
    RAISE NOTICE 'Migration 004: Views created successfully!';
    RAISE NOTICE '- Created views for peraturan table';
    RAISE NOTICE '- Created views for bab, pasals, and ayats tables';
    RAISE NOTICE '- Created views for parsing_logs table';
    RAISE NOTICE '- Created views for monitoring and health';
    RAISE NOTICE 'Total views created across all tables';
END $$;
