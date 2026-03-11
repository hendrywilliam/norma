-- Init SQL untuk Peraturan Database
-- File ini otomatis dijalankan saat PostgreSQL container pertama kali dijalankan

-- Setup database (sudah otomatis dari environment variable POSTGRES_DB)
-- CREATE DATABASE IF NOT EXISTS peraturan_db;

-- Create extension untuk full-text search
CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- Create tabel peraturan
CREATE TABLE IF NOT EXISTS peraturan (
    id VARCHAR(255) PRIMARY KEY,
    judul VARCHAR(1000) NOT NULL,
    nomor VARCHAR(100) NOT NULL,
    tahun INTEGER NOT NULL,
    kategori VARCHAR(50) NOT NULL,
    url VARCHAR(500) NOT NULL UNIQUE,
    pdf_url VARCHAR(500),
    tanggal_disahkan TIMESTAMP,
    tanggal_diundangkan TIMESTAMP,
    deskripsi TEXT,
    konten TEXT,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    parsed_at TIMESTAMP,
    reparse_count INTEGER DEFAULT 0,
    last_reparse_at TIMESTAMP
);

-- Create indexes untuk performa
CREATE INDEX IF NOT EXISTS idx_peraturan_kategori ON peraturan(kategori);
CREATE INDEX IF NOT EXISTS idx_peraturan_tahun ON peraturan(tahun);
CREATE INDEX IF NOT EXISTS idx_peraturan_nomor ON peraturan(nomor);
CREATE INDEX IF NOT EXISTS idx_peraturan_created_at ON peraturan(created_at);
CREATE INDEX IF NOT EXISTS idx_peraturan_updated_at ON peraturan(updated_at);

-- Full-text search index untuk Indonesian
CREATE INDEX IF NOT EXISTS idx_peraturan_search
ON peraturan USING gin(to_tsvector('indonesian', judul || ' ' || COALESCE(nomor, '') || ' ' || COALESCE(konten, '')));

-- Trigram index untuk fuzzy search
CREATE INDEX IF NOT EXISTS idx_peraturan_judul_trgm
ON peraturan USING gin(judul gin_trgm_ops);

-- Create trigger untuk update updated_at otomatis
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_peraturan_updated_at
    BEFORE UPDATE ON peraturan
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Insert sample data (opsional - bisa dihapus)
-- INSERT INTO peraturan (id, judul, nomor, tahun, kategori, url, deskripsi)
-- VALUES
--     ('sample-1', 'Contoh Undang-Undang', '1', 2024, 'UU', 'https://peraturan.go.id/sample-1', 'Ini adalah contoh data peraturan'),
--     ('sample-2', 'Contoh Peraturan Pemerintah', '10', 2023, 'PP', 'https://peraturan.go.id/sample-2', 'Ini adalah contoh data peraturan pemerintah')
-- ON CONFLICT (url) DO NOTHING;

-- Create view untuk statistik peraturan
CREATE OR REPLACE VIEW peraturan_stats AS
SELECT
    COUNT(*) as total_peraturan,
    COUNT(DISTINCT kategori) as total_kategori,
    COUNT(DISTINCT tahun) as total_tahun,
    MIN(tahun) as tahun_pertama,
    MAX(tahun) as tahun_terakhir,
    AVG(reparse_count) as rata_reparse
FROM peraturan;

-- Create view untuk peraturan by kategori
CREATE OR REPLACE VIEW peraturan_by_kategori AS
SELECT
    kategori,
    COUNT(*) as jumlah,
    MIN(tahun) as tahun_pertama,
    MAX(tahun) as tahun_terakhir
FROM peraturan
GROUP BY kategori
ORDER BY jumlah DESC;

-- Create view untuk peraturan by tahun (10 tahun terakhir)
CREATE OR REPLACE VIEW peraturan_by_tahun AS
SELECT
    tahun,
    COUNT(*) as jumlah,
    array_agg(DISTINCT kategori) as kategori
FROM peraturan
WHERE tahun >= EXTRACT(YEAR FROM CURRENT_DATE) - 10
GROUP BY tahun
ORDER BY tahun DESC;

-- Grant permissions (optional - untuk non-superuser)
-- GRANT ALL PRIVILEGES ON TABLE peraturan TO peraturan_user;
-- GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO peraturan_user;
-- GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA public TO peraturan_user;
-- GRANT SELECT ON ALL TABLES IN SCHEMA public TO peraturan_readonly;
-- GRANT USAGE ON ALL SEQUENCES IN SCHEMA public TO peraturan_readonly;

-- Log setup completion
DO $$
BEGIN
    RAISE NOTICE 'Database setup completed successfully!';
END $$;
