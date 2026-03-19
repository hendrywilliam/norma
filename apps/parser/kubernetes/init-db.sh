#!/bin/bash
# Script untuk inisialisasi database schema

set -e

NAMESPACE=${1:-norma-parser}
DB_HOST=${2:-postgres-service}
DB_PORT=${3:-5432}
DB_NAME=${4:-peraturan_db}
DB_USER=${5:-postgres}
SCHEMA_FILE="./DATABASE_SCHEMA.md"

echo "Initializing database schema..."
echo "Namespace: $NAMESPACE"
echo "Database: $DB_NAME"

# Cek apakah database sudah terinisialisasi
RESULT=$(kubectl exec postgres-0 -n $NAMESPACE -- psql -U $DB_USER -d $DB_NAME -tAc "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema='public'") 2>/dev/null || echo "0")

if [ "$RESULT" -gt 0 ]; then
    echo "Database already initialized with $RESULT tables."
    exit 0
fi

# Cek apakah file schema ada
if [ ! -f "$SCHEMA_FILE" ]; then
    echo "Error: Schema file not found: $SCHEMA_FILE"
    exit 1
fi

# Copy schema file ke pod
echo "Copying schema file to pod..."
kubectl cp $SCHEMA_FILE postgres-0:/tmp/schema.md -n $NAMESPACE

# Connect ke database dan jalankan perintah SQL
echo "Applying schema..."

# Parse markdown SQL dan jalankan perintahnya
kubectl exec postgres-0 -n $NAMESPACE -- bash -c "
    psql -U $DB_USER -d $DB_NAME <<'EOSQL'
-- Create tables
CREATE TABLE IF NOT EXISTS peraturan (
    id VARCHAR(100) PRIMARY KEY,
    judul TEXT,
    nomor VARCHAR(50),
    tahun INTEGER,
    kategori VARCHAR(50),
    url TEXT,
    pdf_url TEXT,
    jenis_peraturan TEXT,
    pemrakarsa TEXT,
    tentang TEXT,
    tempat_penetapan TEXT,
    tanggal_ditetapkan DATE,
    pejabat_menetapkan TEXT,
    status_peraturan VARCHAR(50) DEFAULT 'Berlaku',
    jumlah_dilihat INTEGER DEFAULT 0,
    jumlah_download INTEGER DEFAULT 0,
    tanggal_disahkan DATE,
    tanggal_diundangkan DATE,
    deskripsi TEXT,
    metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    parsed_at TIMESTAMP,
    reparse_count INTEGER DEFAULT 0,
    last_reparse_at TIMESTAMP
);

CREATE TABLE IF NOT EXISTS bab (
    id SERIAL PRIMARY KEY,
    peraturan_id VARCHAR(100) REFERENCES peraturan(id) ON DELETE CASCADE,
    nomor_bab VARCHAR(10),
    judul_bab TEXT,
    urutan INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(peraturan_id, nomor_bab)
);

CREATE TABLE IF NOT EXISTS pasals (
    id SERIAL PRIMARY KEY,
    peraturan_id VARCHAR(100) REFERENCES peraturan(id) ON DELETE CASCADE,
    bab_id INTEGER REFERENCES bab(id) ON DELETE SET NULL,
    nomor_pasal VARCHAR(50),
    judul_pasal TEXT,
    konten_pasal TEXT,
    urutan INTEGER,
    metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(peraturan_id, nomor_pasal)
);

CREATE TABLE IF NOT EXISTS ayats (
    id SERIAL PRIMARY KEY,
    pasal_id INTEGER REFERENCES pasals(id) ON DELETE CASCADE,
    nomor_ayat VARCHAR(10),
    konten_ayat TEXT,
    urutan INTEGER,
    metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(pasal_id, nomor_ayat)
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_peraturan_kategori ON peraturan(kategori);
CREATE INDEX IF NOT EXISTS idx_peraturan_tahun ON peraturan(tahun);
CREATE INDEX IF NOT EXISTS idx_peraturan_created ON peraturan(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_bab_peraturan ON bab(peraturan_id);
CREATE INDEX IF NOT EXISTS idx_pasal_peraturan ON pasals(peraturan_id);
CREATE INDEX IF NOT EXISTS idx_pasal_bab ON pasals(bab_id);
CREATE INDEX IF NOT EXISTS idx_ayat_pasal ON ayats(pasal_id);

EOSQL
"

echo "Database schema initialized successfully!"
echo ""
echo "Tables created:"
kubectl exec postgres-0 -n $NAMESPACE -- psql -U $DB_USER -d $DB_NAME -c "\dt" | grep -v "Did not find"
