CREATE EXTENSION IF NOT EXISTS pg_trgm;

CREATE TABLE IF NOT EXISTS peraturan (
    -- Primary Key
    id VARCHAR(255) PRIMARY KEY,

    -- Informasi Dasar Peraturan
    judul VARCHAR(1000),
    nomor VARCHAR(100) NOT NULL,
    tahun INTEGER NOT NULL,
    kategori VARCHAR(50) NOT NULL,

    -- URLs
    url VARCHAR(500) NOT NULL UNIQUE,
    pdf_url VARCHAR(500),

    -- Tanggal Penting
    tanggal_disahkan TIMESTAMP,
    tanggal_diundangkan TIMESTAMP,
    tanggal_ditetapkan TIMESTAMP,

    -- Informasi Tambahan
    deskripsi TEXT,

    -- Metadata JSON
    metadata JSONB DEFAULT '{}',

    -- Field dari Peraturan.go.id
    jenis_peraturan VARCHAR(100),
    pemrakarsa VARCHAR(200),
    tentang VARCHAR(500),
    tempat_penetapan VARCHAR(200),
    pejabat_menetapkan VARCHAR(200),
    status_peraturan VARCHAR(50) DEFAULT 'Berlaku',
    jumlah_dilihat INTEGER DEFAULT 0,
    jumlah_download INTEGER DEFAULT 0,

    -- Tracking
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    parsed_at TIMESTAMP,
    reparse_count INTEGER DEFAULT 0,
    last_reparse_at TIMESTAMP
);

-- Comments untuk kolom peraturan
COMMENT ON TABLE peraturan IS 'Tabel utama untuk menyimpan informasi peraturan perundangan';
COMMENT ON COLUMN peraturan.id IS 'Unique ID peraturan';
COMMENT ON COLUMN peraturan.judul IS 'Judul lengkap peraturan';
COMMENT ON COLUMN peraturan.nomor IS 'Nomor peraturan';
COMMENT ON COLUMN peraturan.tahun IS 'Tahun peraturan';
COMMENT ON COLUMN peraturan.kategori IS 'Kategori peraturan (UU, PP, Perpres, dll)';
COMMENT ON COLUMN peraturan.url IS 'URL sumber dari peraturan.go.id';
COMMENT ON COLUMN peraturan.pdf_url IS 'URL PDF peraturan';
COMMENT ON COLUMN peraturan.tanggal_disahkan IS 'Tanggal peraturan disahkan';
COMMENT ON COLUMN peraturan.tanggal_diundangkan IS 'Tanggal peraturan diundangkan';
COMMENT ON COLUMN peraturan.tanggal_ditetapkan IS 'Tanggal peraturan ditetapkan';
COMMENT ON COLUMN peraturan.deskripsi IS 'Deskripsi singkat peraturan';
COMMENT ON COLUMN peraturan.metadata IS 'Metadata tambahan (keywords, tags, dll)';
COMMENT ON COLUMN peraturan.jenis_peraturan IS 'Jenis peraturan lengkap';
COMMENT ON COLUMN peraturan.pemrakarsa IS 'Pemrakarsa peraturan';
COMMENT ON COLUMN peraturan.tentang IS 'Topik/judul peraturan';
COMMENT ON COLUMN peraturan.tempat_penetapan IS 'Tempat peraturan ditetapkan';
COMMENT ON COLUMN peraturan.pejabat_menetapkan IS 'Pejabat yang menetapkan peraturan';
COMMENT ON COLUMN peraturan.status_peraturan IS 'Status peraturan (Berlaku, Dicabut, dll)';
COMMENT ON COLUMN peraturan.jumlah_dilihat IS 'Jumlah peraturan dilihat di peraturan.go.id';
COMMENT ON COLUMN peraturan.jumlah_download IS 'Jumlah peraturan didownload di peraturan.go.id';
COMMENT ON COLUMN peraturan.created_at IS 'Waktu record dibuat';
COMMENT ON COLUMN peraturan.updated_at IS 'Waktu record diupdate';
COMMENT ON COLUMN peraturan.parsed_at IS 'Waktu parsing terakhir';
COMMENT ON COLUMN peraturan.reparse_count IS 'Berapa kali peraturan di-reparse';
COMMENT ON COLUMN peraturan.last_reparse_at IS 'Waktu terakhir reparse';

CREATE TABLE IF NOT EXISTS bab (
    -- Primary Key
    id SERIAL PRIMARY KEY,

    -- Foreign Key ke peraturan
    peraturan_id VARCHAR(255) NOT NULL,

    -- Informasi Bab
    nomor_bab VARCHAR(20) NOT NULL,
    judul_bab TEXT,
    urutan INTEGER NOT NULL,

    -- Tracking
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- Constraints
    CONSTRAINT fk_bab_peraturan FOREIGN KEY (peraturan_id)
        REFERENCES peraturan(id) ON DELETE CASCADE,
    CONSTRAINT uq_bab_peraturan_nomor UNIQUE (peraturan_id, nomor_bab)
);

-- Comments untuk tabel bab
COMMENT ON TABLE bab IS 'Tabel untuk menyimpan bab-bab peraturan';
COMMENT ON COLUMN bab.id IS 'Auto-increment ID';
COMMENT ON COLUMN bab.peraturan_id IS 'Foreign key ke tabel peraturan';
COMMENT ON COLUMN bab.nomor_bab IS 'Nomor bab (I, II, III atau 1, 2, 3)';
COMMENT ON COLUMN bab.judul_bab IS 'Judul bab';
COMMENT ON COLUMN bab.urutan IS 'Urutan bab dalam peraturan';
COMMENT ON COLUMN bab.created_at IS 'Waktu bab dibuat';
COMMENT ON COLUMN bab.updated_at IS 'Waktu bab diupdate';

-- ========================================
-- 3. TABLE pasals
-- ========================================

CREATE TABLE IF NOT EXISTS pasals (
    -- Primary Key
    id SERIAL PRIMARY KEY,

    -- Foreign Keys
    peraturan_id VARCHAR(255) NOT NULL,
    bab_id INTEGER,

    -- Informasi Pasal
    nomor_pasal VARCHAR(50) NOT NULL,
    judul_pasal TEXT,
    konten_pasal TEXT NOT NULL,
    urutan INTEGER NOT NULL,

    -- Metadata
    metadata JSONB DEFAULT '{}',

    -- Tracking
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- Constraints
    CONSTRAINT fk_pasal_peraturan FOREIGN KEY (peraturan_id)
        REFERENCES peraturan(id) ON DELETE CASCADE,
    CONSTRAINT fk_pasal_bab FOREIGN KEY (bab_id)
        REFERENCES bab(id) ON DELETE SET NULL,
    CONSTRAINT uq_pasal_peraturan_nomor UNIQUE (peraturan_id, nomor_pasal)
);

-- Comments untuk tabel pasals
COMMENT ON TABLE pasals IS 'Tabel untuk menyimpan pasal-pasal peraturan';
COMMENT ON COLUMN pasals.id IS 'Auto-increment ID';
COMMENT ON COLUMN pasals.peraturan_id IS 'Foreign key ke tabel peraturan';
COMMENT ON COLUMN pasals.bab_id IS 'Foreign key ke tabel bab (optional)';
COMMENT ON COLUMN pasals.nomor_pasal IS 'Nomor pasal (Pasal 1, Pasal 2, dll)';
COMMENT ON COLUMN pasals.judul_pasal IS 'Judul pasal jika ada';
COMMENT ON COLUMN pasals.konten_pasal IS 'Konten lengkap pasal';
COMMENT ON COLUMN pasals.urutan IS 'Urutan pasal dalam peraturan';
COMMENT ON COLUMN pasals.metadata IS 'Metadata tambahan (keywords, tags, dll)';
COMMENT ON COLUMN pasals.created_at IS 'Waktu pasal dibuat';
COMMENT ON COLUMN pasals.updated_at IS 'Waktu pasal diupdate';

-- ========================================
-- 4. TABLE ayats
-- ========================================

CREATE TABLE IF NOT EXISTS ayats (
    -- Primary Key
    id SERIAL PRIMARY KEY,

    -- Foreign Key ke pasal
    pasal_id INTEGER NOT NULL,

    -- Informasi Ayat
    nomor_ayat VARCHAR(10) NOT NULL,
    konten_ayat TEXT NOT NULL,
    urutan INTEGER NOT NULL,

    -- Metadata
    metadata JSONB DEFAULT '{}',

    -- Tracking
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- Constraints
    CONSTRAINT fk_ayat_pasal FOREIGN KEY (pasal_id)
        REFERENCES pasals(id) ON DELETE CASCADE,
    CONSTRAINT uq_ayat_pasal_nomor UNIQUE (pasal_id, nomor_ayat)
);

-- Comments untuk tabel ayats
COMMENT ON TABLE ayats IS 'Tabel untuk menyimpan ayat-ayat dari pasal';
COMMENT ON COLUMN ayats.id IS 'Auto-increment ID';
COMMENT ON COLUMN ayats.pasal_id IS 'Foreign key ke tabel pasals';
COMMENT ON COLUMN ayats.nomor_ayat IS 'Nomor ayat ((1), (2), (3), dll)';
COMMENT ON COLUMN ayats.konten_ayat IS 'Konten ayat';
COMMENT ON COLUMN ayats.urutan IS 'Urutan ayat dalam pasal';
COMMENT ON COLUMN ayats.metadata IS 'Metadata tambahan';
COMMENT ON COLUMN ayats.created_at IS 'Waktu ayat dibuat';
COMMENT ON COLUMN ayats.updated_at IS 'Waktu ayat diupdate';

-- ========================================
-- 5. TABLE parsing_logs
-- ========================================

CREATE TABLE IF NOT EXISTS parsing_logs (
    -- Primary Key
    id SERIAL PRIMARY KEY,

    -- Foreign Key ke peraturan
    peraturan_id VARCHAR(255),

    -- Informasi Parsing
    action VARCHAR(50) NOT NULL,
    status VARCHAR(20) NOT NULL,
    error_message TEXT,

    -- Metadata
    metadata JSONB DEFAULT '{}',

    -- Tracking
    parsed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- Constraints
    CONSTRAINT fk_parsing_logs_peraturan FOREIGN KEY (peraturan_id)
        REFERENCES peraturan(id) ON DELETE SET NULL
);

-- Comments untuk tabel parsing_logs
COMMENT ON TABLE parsing_logs IS 'Tabel untuk logging operasi parsing';
COMMENT ON COLUMN parsing_logs.id IS 'Auto-increment ID';
COMMENT ON COLUMN parsing_logs.peraturan_id IS 'Foreign key ke tabel peraturan';
COMMENT ON COLUMN parsing_logs.action IS 'Tipe action
 (create, update, reparse)';
COMMENT ON COLUMN parsing_logs.status IS 'Status (success, failed, running)';
COMMENT ON COLUMN parsing_logs.error_message IS 'Error message jika gagal';
COMMENT ON COLUMN parsing_logs.metadata IS 'Metadata tambahan (duration, pages, dll)';
COMMENT ON COLUMN parsing_logs.parsed_at IS 'Waktu parsing';
