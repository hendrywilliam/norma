# Database Schema Documentation

## Overview

Database ini digunakan untuk menyimpan data peraturan perundangan dari peraturan.go.id dengan struktur yang ter-normalisasi. Peraturan dipecah menjadi bab, pasal, dan ayat untuk memudahkan pencarian dan referensi.

## Entity Relationship Diagram (ERD)

```
┌─────────────────┐       ┌─────────────┐       ┌─────────────┐       ┌─────────────┐
│   peraturan     │──────►│     bab     │──────►│   pasals    │──────►│    ayats    │
│                 │       │             │       │             │       │             │
│ - id           │       │ - id        │       │ - id        │       │ - id        │
│ - judul        │       │ - peraturan │       │ - peraturan │       │ - pasal_id  │
│ - nomor        │       │   _id       │       │ - bab_id    │       │ - nomor_ayat │
│ - tahun        │       │ - nomor_bab  │       │ - nomor_pasal│       │ - konten_ayat│
│ - kategori     │       │ - judul_bab  │       │ - judul_pasal│       │ - urutan      │
│ - jenis        │       │ - urutan     │       │ - konten_pas │       │ - metadata    │
│   _peraturan   │       │ - metadata    │       │ - urutan     │       │             │
│ - pemrakarsa   │       │             │       │ - metadata    │       │             │
│ - tentang      │       │             │       │             │       │             │
│ - status       │       │             │       │             │       │             │
└─────────────────┘       └─────────────┘       └─────────────┘       └─────────────┘

┌─────────────────────┐
│   parsing_logs      │
│                     │
│ - id                │
│ - peraturan_id      │
│ - action            │
│ - status            │
│ - error_message     │
│ - parsed_at         │
│ - metadata          │
└─────────────────────┘
```

## Tables

### 1. peraturan

Tabel utama untuk menyimpan informasi peraturan perundangan.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | VARCHAR(255) | PRIMARY KEY | Unique ID peraturan |
| judul | VARCHAR(1000) | | Judul lengkap peraturan |
| nomor | VARCHAR(100) | NOT NULL | Nomor peraturan |
| tahun | INTEGER | NOT NULL | Tahun peraturan |
| kategori | VARCHAR(50) | NOT NULL | Kategori (UU, PP, Perpres, dll) |
| url | VARCHAR(500) | UNIQUE, NOT NULL | URL sumber dari peraturan.go.id |
| pdf_url | VARCHAR(500) | | URL PDF peraturan |
| jenis_peraturan | VARCHAR(100) | | Jenis peraturan lengkap |
| pemrakarsa | VARCHAR(200) | | Pemrakarsa peraturan |
| tentang | VARCHAR(500) | | Topik/judul peraturan |
| tempat_penetapan | VARCHAR(200) | | Tempat peraturan ditetapkan |
| tanggal_ditetapkan | TIMESTAMP | | Tanggal peraturan ditetapkan |
| tanggal_diundangkan | TIMESTAMP | | Tanggal peraturan diundangkan |
| tanggal_disahkan | TIMESTAMP | | Tanggal peraturan disahkan |
| pejabat_menetapkan | VARCHAR(200) | | Pejabat yang menetapkan peraturan |
| status_peraturan | VARCHAR(50) | DEFAULT 'Berlaku' | Status peraturan (Berlaku, Dicabut, dll) |
| jumlah_dilihat | INTEGER | DEFAULT 0 | Jumlah peraturan dilihat di peraturan.go.id |
| jumlah_download | INTEGER | DEFAULT 0 | Jumlah peraturan didownload di peraturan.go.id |
| deskripsi | TEXT | | Deskripsi singkat peraturan |
| metadata | JSONB | DEFAULT '{}' | Metadata tambahan |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Waktu record dibuat |
| updated_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Waktu record diupdate |
| parsed_at | TIMESTAMP | | Waktu parsing terakhir |
| reparse_count | INTEGER | DEFAULT 0 | Berapa kali peraturan di-reparse |
| last_reparse_at | TIMESTAMP | | Waktu terakhir reparse |

**Indexes:**
- `idx_peraturan_kategori` - Untuk filter by kategori
- `idx_peraturan_tahun` - Untuk filter by tahun
- `idx_peraturan_nomor` - Untuk filter by nomor
- `idx_peraturan_created_at` - Untuk sorting by created_at
- `idx_peraturan_updated_at` - Untuk sorting by updated_at
- `idx_peraturan_parsed_at` - Untuk sorting by parsed_at
- `idx_peraturan_tanggal_disahkan` - Untuk filter by tanggal disahkan
- `idx_peraturan_tanggal_diundangkan` - Untuk filter by tanggal diundangkan
- `idx_peraturan_tanggal_ditetapkan` - Untuk filter by tanggal ditetapkan
- `idx_peraturan_jenis_peraturan` - Untuk filter by jenis peraturan
- `idx_peraturan_pemrakarsa` - Untuk filter by pemrakarsa
- `idx_peraturan_tentang` - Untuk filter by tentang
- `idx_peraturan_status_peraturan` - Untuk filter by status
- `idx_peraturan_search` - Full-text search (judul + nomor + tentang)
- `idx_peraturan_judul_trgm` - Fuzzy search untuk judul
- `idx_peraturan_tentang_trgm` - Fuzzy search untuk tentang
- `idx_peraturan_kategori_tahun` - Composite index
- `idx_peraturan_kategori_status` - Composite index
- `idx_peraturan_tahun_status` - Composite index
- `idx_peraturan_kategori_tahun_status` - Composite index
- `idx_peraturan_metadata` - JSONB metadata search
- `idx_peraturan_reparse_count` - Untuk reparse tracking
- `idx_peraturan_last_reparse_at` - Untuk reparse tracking
- `idx_peraturan_jumlah_dilihat` - Untuk popularity (jumlah dilihat)
- `idx_peraturan_jumlah_download` - Untuk popularity (jumlah download)

**Foreign Keys:**
- Tidak ada foreign key di tabel peraturan (tabel parent)

### 2. bab

Tabel untuk menyimpan bab-bab peraturan.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | SERIAL | PRIMARY KEY | Auto-increment ID |
| peraturan_id | VARCHAR(255) | NOT NULL, FK → peraturan(id) | Foreign key ke peraturan |
| nomor_bab | VARCHAR(20) | NOT NULL | Nomor bab (I, II, III, dll) |
| judul_bab | TEXT | | Judul bab |
| urutan | INTEGER | NOT NULL | Urutan bab dalam peraturan |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Waktu bab dibuat |
| updated_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Waktu bab diupdate |

**Unique Constraint:**
- `(peraturan_id, nomor_bab)` - Satu nomor bab unik per peraturan

**Foreign Keys:**
- `fk_bab_peraturan` → `peraturan(id)` ON DELETE CASCADE

**Indexes:**
- `idx_bab_peraturan_id` - Quick lookup by peraturan
- `idx_bab_urutan` - Sorting urutan bab
- `idx_bab_nomor_bab` - Search by nomor bab
- `idx_bab_judul_bab_search` - Full-text search judul bab
- `idx_bab_peraturan_id_urutan` - Composite index untuk get bab by peraturan with ordering

**Comments:**
- Tabel ini menyimpan bab-bab dari peraturan (BAB I, BAB II, dst.)
- Setiap bab memiliki urutan yang unik dalam peraturan
- Bab bersifat opsional, beberapa peraturan mungkin tidak memiliki bab

### 3. pasals

Tabel untuk menyimpan setiap pasal dari peraturan.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | SERIAL | PRIMARY KEY | Auto-increment ID |
| peraturan_id | VARCHAR(255) | NOT NULL, FK → peraturan(id) | Foreign key ke peraturan |
| bab_id | INTEGER | FK → bab(id), NULLABLE | Foreign key ke bab |
| nomor_pasal | VARCHAR(50) | NOT NULL | Nomor pasal (Pasal 1, Pasal 2, dll) |
| judul_pasal | TEXT | | Judul pasal jika ada |
| konten_pasal | TEXT | NOT NULL | Konten lengkap pasal |
| urutan | INTEGER | NOT NULL | Urutan pasal dalam peraturan |
| metadata | JSONB | DEFAULT '{}' | Metadata tambahan |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Waktu pasal dibuat |
| updated_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Waktu pasal diupdate |

**Unique Constraint:**
- `(peraturan_id, nomor_pasal)` - Satu nomor pasal unik per peraturan

**Foreign Keys:**
- `fk_pasal_peraturan` → `peraturan(id)` ON DELETE CASCADE
- `fk_pasal_bab` → `bab(id)` ON DELETE SET NULL

**Indexes:**
- `idx_pasals_peraturan_id` - Quick lookup by peraturan
- `idx_pasals_bab_id` - Quick lookup by bab
- `idx_pasals_urutan` - Sorting urutan pasal
- `idx_pasals_nomor` - Search by nomor pasal
- `idx_pasals_search` - Full-text search pasal (nomor + judul + konten)
- `idx_pasals_judul_trgm` - Fuzzy search judul pasal
- `idx_pasals_peraturan_id_urutan` - Composite index untuk get pasal by peraturan with ordering
- `idx_pasals_bab_id_urutan` - Composite index untuk get pasal by bab with ordering
- `idx_pasals_peraturan_bab_urutan` - Composite index untuk get pasal by peraturan and bab
- `idx_pasals_metadata` - JSONB metadata search

**Comments:**
- Tabel ini menyimpan setiap pasal dari peraturan (Pasal 1, Pasal 2, dst.)
- Setiap pasal terhubung ke peraturan dan opsional ke bab
- Pasal memiliki konten lengkap yang akan digunakan untuk pencarian

### 4. ayats

Tabel untuk menyimpan setiap ayat dari pasal.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | SERIAL | PRIMARY KEY | Auto-increment ID |
| pasal_id | INTEGER | NOT NULL, FK → pasals(id) | Foreign key ke pasals |
| nomor_ayat | VARCHAR(10) | NOT NULL | Nomor ayat ((1), (2), (3), dll) |
| konten_ayat | TEXT | NOT NULL | Konten ayat |
| urutan | INTEGER | NOT NULL | Urutan ayat dalam pasal |
| metadata | JSONB | DEFAULT '{}' | Metadata tambahan |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Waktu ayat dibuat |
| updated_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Waktu ayat diupdate |

**Unique Constraint:**
- `(pasal_id, nomor_ayat)` - Satu nomor ayat unik per pasal

**Foreign Keys:**
- `fk_ayat_pasal` → `pasals(id)` ON DELETE CASCADE

**Indexes:**
- `idx_ayats_pasal_id` - Quick lookup by pasal
- `idx_ayats_urutan` - Sorting urutan ayat
- `idx_ayats_nomor_ayat` - Search by nomor ayat
- `idx_ayats_search` - Full-text search ayat (nomor + konten)
- `idx_ayats_pasal_id_urutan` - Composite index untuk get ayat by pasal with ordering
- `idx_ayats_metadata` - JSONB metadata search

**Comments:**
- Tabel ini menyimpan setiap ayat dari pasal ((1), (2), (3), dst.)
- Setiap ayat terhubung ke pasal dan memiliki urutan yang unik dalam pasal
- Ayat adalah unit terkecil dari peraturan yang dapat direferensikan

### 5. parsing_logs

Tabel untuk logging operasi parsing.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | SERIAL | PRIMARY KEY | Auto-increment ID |
| peraturan_id | VARCHAR(255) | FK → peraturan(id) | Foreign key ke peraturan |
| action | VARCHAR(50) | NOT NULL | Tipe action (create, update, reparse) |
| status | VARCHAR(20) | NOT NULL | Status (success, failed, running) |
| error_message | TEXT | | Error message jika gagal |
| metadata | JSONB | DEFAULT '{}' | Metadata tambahan |
| parsed_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Waktu parsing |

**Foreign Keys:**
- `fk_parsing_logs_peraturan` → `peraturan(id)` ON DELETE SET NULL

**Indexes:**
- `idx_parsing_logs_peraturan_id` - Quick lookup by peraturan
- `idx_parsing_logs_status` - Filter by status
- `idx_parsing_logs_action` - Filter by action
- `idx_parsing_logs_parsed_at` - Sorting by waktu parsing DESC
- `idx_parsing_logs_error_message` - Partial index untuk error message
- `idx_parsing_logs_peraturan_status` - Composite index untuk get logs by peraturan dan status
- `idx_parsing_logs_peraturan_parsed_at` - Composite index untuk get logs by peraturan dan waktu
- `idx_parsing_logs_status_parsed_at` - Composite index untuk get logs by status dan waktu
- `idx_parsing_logs_metadata` - JSONB metadata search

**Comments:**
- Tabel ini menyimpan log dari setiap operasi parsing
- Berguna untuk tracking error dan monitoring performance
- Metadata dapat berisi duration, pages, bab_count, pasal_count, ayat_count

## Views

### peraturan_stats

Statistik umum peraturan.

| Column | Type | Description |
|--------|------|-------------|
| total_peraturan | INTEGER | Total jumlah peraturan |
| total_kategori | INTEGER | Total kategori unik |
| total_tahun | INTEGER | Total tahun unik |
| total_jenis | INTEGER | Total jenis peraturan unik |
| tahun_pertama | INTEGER | Tahun peraturan pertama |
| tahun_terakhir | INTEGER | Tahun peraturan terakhir |
| pertama_dibuat | TIMESTAMP | Waktu record peraturan pertama dibuat |
| terakhir_dibuat | TIMESTAMP | Waktu record peraturan terakhir dibuat |
| pertama_diparse | TIMESTAMP | Waktu pertama kali parsing dilakukan |
| terakhir_diparse | TIMESTAMP | Waktu terakhir kali parsing dilakukan |
| rata_reparse | NUMERIC | Rata-rata reparse count |
| total_dengan_pdf | INTEGER | Total peraturan yang memiliki PDF |
| total_bab | INTEGER | Total semua bab di database |
| total_pasal | INTEGER | Total semua pasal di database |
| total_ayat | INTEGER | Total semua ayat di database |
| rata_pasal_per_peraturan | NUMERIC | Rata-rata pasal per peraturan |

### peraturan_with_pasal_count

Peraturan dengan count pasal.

| Column | Type | Description |
|--------|------|-------------|
| Semua kolom dari tabel peraturan | - | Semua field dari tabel peraturan |
| total_pasal | INTEGER | Total pasal dalam peraturan |
| total_bab | INTEGER | Total bab dalam peraturan |
| total_ayat | INTEGER | Total ayat dalam peraturan |
| total_karakter_pasal | INTEGER | Total karakter konten pasal |
| pasal_pertama | INTEGER | Nomor pasal pertama (urutan) |
| pasal_terakhir | INTEGER | Nomor pasal terakhir (urutan) |
| bab_pertama | INTEGER | Nomor bab pertama (urutan) |
| bab_terakhir | INTEGER | Nomor bab terakhir (urutan) |

### peraturan_with_bab_pasals

Peraturan dengan semua bab dan pasals.

| Column | Type | Description |
|--------|------|-------------|
| Semua kolom dari tabel peraturan | - | Semua field dari tabel peraturan |
| bab_id | INTEGER | ID bab |
| nomor_bab | VARCHAR(20) | Nomor bab |
| judul_bab | TEXT | Judul bab |
| bab_urutan | INTEGER | Urutan bab dalam peraturan |
| pasal_id | INTEGER | ID pasal |
| nomor_pasal | VARCHAR(50) | Nomor pasal |
| judul_pasal | TEXT | Judul pasal |
| konten_pasal | TEXT | Konten pasal |
| pasal_urutan | INTEGER | Urutan pasal dalam peraturan |

### bab_with_pasals

Bab dengan semua pasals.

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | ID bab |
| peraturan_id | VARCHAR(255) | ID peraturan |
| nomor_bab | VARCHAR(20) | Nomor bab |
| judul_bab | TEXT | Judul bab |
| urutan | INTEGER | Urutan bab dalam peraturan |
| judul_peraturan | VARCHAR(1000) | Judul peraturan |
| nomor_peraturan | VARCHAR(100) | Nomor peraturan |
| tahun_peraturan | INTEGER | Tahun peraturan |
| kategori_peraturan | VARCHAR(50) | Kategori peraturan |
| total_pasal | INTEGER | Total pasal dalam bab |
| daftar_pasal | TEXT[] | List nomor pasal |

### pasals_with_bab_peraturan

Pasal dengan informasi bab dan peraturan.

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | ID pasal |
| peraturan_id | VARCHAR(255) | ID peraturan |
| bab_id | INTEGER | ID bab |
| nomor_pasal | VARCHAR(50) | Nomor pasal |
| judul_pasal | TEXT | Judul pasal |
| konten_pasal | TEXT | Konten pasal |
| urutan | INTEGER | Urutan pasal dalam peraturan |
| metadata | JSONB | Metadata tambahan |
| created_at | TIMESTAMP | Waktu pasal dibuat |
| updated_at | TIMESTAMP | Waktu pasal diupdate |
| nomor_bab | VARCHAR(20) | Nomor bab |
| judul_bab | TEXT | Judul bab |
| bab_urutan | INTEGER | Urutan bab dalam peraturan |
| judul_peraturan | VARCHAR(1000) | Judul peraturan |
| nomor_peraturan | VARCHAR(100) | Nomor peraturan |
| tahun_peraturan | INTEGER | Tahun peraturan |
| kategori_peraturan | VARCHAR(50) | Kategori peraturan |
| jenis_peraturan | VARCHAR(100) | Jenis peraturan |
| tentang | VARCHAR(500) | Topik peraturan |
| total_ayat | INTEGER | Total ayat dalam pasal |
| daftar_ayat | TEXT[] | List nomor ayat |

### ayats_with_pasal_bab_peraturan

Ayat dengan informasi pasal, bab, dan peraturan.

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | ID ayat |
| pasal_id | INTEGER | ID pasal |
| nomor_ayat | VARCHAR(10) | Nomor ayat |
| konten_ayat | TEXT | Konten ayat |
| urutan | INTEGER | Urutan ayat dalam pasal |
| metadata | JSONB | Metadata tambahan |
| created_at | TIMESTAMP | Waktu ayat dibuat |
| updated_at | TIMESTAMP | Waktu ayat diupdate |
| nomor_pasal | VARCHAR(50) | Nomor pasal |
| judul_pasal | TEXT | Judul pasal |
| pasal_urutan | INTEGER | Urutan pasal dalam peraturan |
| nomor_bab | VARCHAR(20) | Nomor bab |
| judul_bab | TEXT | Judul bab |
| bab_urutan | INTEGER | Urutan bab dalam peraturan |
| peraturan_id | VARCHAR(255) | ID peraturan |
| judul_peraturan | VARCHAR(1000) | Judul peraturan |
| nomor_peraturan | VARCHAR(100) | Nomor peraturan |
| tahun_peraturan | INTEGER | Tahun peraturan |
| kategori_peraturan | VARCHAR(50) | Kategori peraturan |
| jenis_peraturan | VARCHAR(100) | Jenis peraturan |
| tentang | VARCHAR(500) | Topik peraturan |

### peraturan_detail_lengkap

Peraturan detail lengkap (semua bab, pasals, dan ayats).

| Column | Type | Description |
|--------|------|-------------|
| peraturan_id | VARCHAR(255) | ID peraturan |
| judul_peraturan | VARCHAR(1000) | Judul peraturan |
| nomor_peraturan | VARCHAR(100) | Nomor peraturan |
| tahun_peraturan | INTEGER | Tahun peraturan |
| kategori_peraturan | VARCHAR(50) | Kategori peraturan |
| jenis_peraturan | VARCHAR(100) | Jenis peraturan |
| tentang | VARCHAR(500) | Topik peraturan |
| bab_id | INTEGER | ID bab |
| nomor_bab | VARCHAR(20) | Nomor bab |
| judul_bab | TEXT | Judul bab |
| bab_urutan | INTEGER | Urutan bab dalam peraturan |
| pasal_id | INTEGER | ID pasal |
| nomor_pasal | VARCHAR(50) | Nomor pasal |
| judul_pasal | TEXT | Judul pasal |
| pasal_urutan | INTEGER | Urutan pasal dalam peraturan |
| ayat_id | INTEGER | ID ayat |
| nomor_ayat | VARCHAR(10) | Nomor ayat |
| konten_ayat | TEXT | Konten ayat |
| ayat_urutan | INTEGER | Urutan ayat dalam pasal |

### peraturan_by_kategori

Peraturan dikelompokkan by kategori.

| Column | Type | Description |
|--------|------|-------------|
| kategori | VARCHAR(50) | Nama kategori |
| jumlah | INTEGER | Jumlah peraturan |
| jumlah_tahun | INTEGER | Jumlah tahun unik |
| tahun_pertama | INTEGER | Tahun peraturan pertama |
| tahun_terakhir | INTEGER | Tahun peraturan terakhir |
| rata_reparse | NUMERIC | Rata-rata reparse count |
| rata_pasal | NUMERIC | Rata-rata pasal per peraturan |
| jumlah_dengan_pasal | INTEGER | Jumlah peraturan dengan pasal |
| jumlah_tanpa_pasal | INTEGER | Jumlah peraturan tanpa pasal |
| jumlah_dengan_pdf | INTEGER | Jumlah peraturan dengan PDF |
| rata_dilihat | INTEGER | Rata-rata jumlah dilihat |
| rata_download | INTEGER | Rata-rata jumlah download |
| pertama_dibuat | TIMESTAMP | Waktu peraturan pertama dibuat |
| terakhir_dibuat | TIMESTAMP | Waktu peraturan terakhir dibuat |
| jenis_peraturan | TEXT[] | Array jenis peraturan unik |

### peraturan_by_tahun

Peraturan dikelompokkan by tahun (10 tahun terakhir).

| Column | Type | Description |
|--------|------|-------------|
| tahun | INTEGER | Tahun peraturan |
| jumlah | INTEGER | Jumlah peraturan |
| jumlah_kategori | INTEGER | Jumlah kategori unik |
| jumlah_jenis | INTEGER | Jumlah jenis peraturan unik |
| kategori | TEXT[] | Array kategori unik |
| jenis_peraturan | TEXT[] | Array jenis peraturan unik |
| rata_reparse | NUMERIC | Rata-rata reparse count |
| rata_pasal | NUMERIC | Rata-rata pasal per peraturan |
| jumlah_dengan_pasal | INTEGER | Jumlah peraturan dengan pasal |
| rata_dilihat | INTEGER | Rata-rata jumlah dilihat |
| rata_download | INTEGER | Rata-rata jumlah download |

### peraturan_terbaru_diparse

50 peraturan terbaru yang diparse.

| Column | Type | Description |
|--------|------|-------------|
| Semua kolom penting dari tabel peraturan | - | Informasi peraturan dasar |
| parsed_at | TIMESTAMP | Waktu parsing terakhir |
| reparse_count | INTEGER | Berapa kali peraturan di-reparse |
| total_bab | INTEGER | Total bab dalam peraturan |
| total_pasal | INTEGER | Total pasal dalam peraturan |
| total_ayat | INTEGER | Total ayat dalam peraturan |

Sorted by `parsed_at` DESC

### peraturan_terbaru_dibuat

50 peraturan terbaru yang dibuat di database.

| Column | Type | Description |
|--------|------|-------------|
| Semua kolom penting dari tabel peraturan | - | Informasi peraturan dasar |
| created_at | TIMESTAMP | Waktu record dibuat |
| total_bab | INTEGER | Total bab dalam peraturan |
| total_pasal | INTEGER | Total pasal dalam peraturan |

Sorted by `created_at` DESC

### peraturan_perlu_reparse

Peraturan yang perlu di-reparse.

Criteria:
- Belum pernah di-parse (parsed_at IS NULL)
- Lama diparse (> 180 hari)
- Reparse count rendah (< 2)
- Tidak memiliki pasal (total_pasal = 0)

| Column | Type | Description |
|--------|------|-------------|
| Semua kolom penting dari tabel peraturan | - | Informasi peraturan dasar |
| total_pasal | INTEGER | Total pasal dalam peraturan |
| hari_sejak_terakhir | INTEGER | Hari sejak parsing terakhir |
| prioritas_reparse | INTEGER | Score prioritas (10=high, 8=medium, 5=low, 1=none) |

Sorted by `prioritas_reparse` DESC, `COALESCE(parsed_at, created_at)` ASC

### peraturan_error_parsing

Peraturan dengan error parsing.

| Column | Type | Description |
|--------|------|-------------|
| Semua kolom penting dari tabel peraturan | - | Informasi peraturan dasar |
| total_error | INTEGER | Total error dari parsing_logs |
| error_terakhir | TEXT | Error message terakhir |
| total_pasal | INTEGER | Total pasal dalam peraturan |

Sorted by `created_at` DESC

Filter: `(SELECT COUNT(*) FROM parsing_logs WHERE peraturan_id = peraturan.id AND status = 'failed') > 0` AND `total_pasal = 0`

### peraturan_tanpa_pasal

Peraturan tanpa konten (perlu parsing).

| Column | Type | Description |
|--------|------|-------------|
| Semua kolom penting dari tabel peraturan | - | Informasi peraturan dasar |
| hari_sejak_dibuat | INTEGER | Hari sejak record dibuat |
| total_bab | INTEGER | Total bab dalam peraturan |

Sorted by `created_at` ASC

Filter: `total_pasal = 0`

### trending_peraturan

50 peraturan yang sering diakses/di-parse (trending).

| Column | Type | Description |
|--------|------|-------------|
| Semua kolom penting dari tabel peraturan | - | Informasi peraturan dasar |
| jumlah_dilihat | INTEGER | Jumlah peraturan dilihat |
| jumlah_download | INTEGER | Jumlah peraturan didownload |
| total_operations | INTEGER | Total operasi parsing |
| operations_last_30_days | INTEGER | Operasi dalam 30 hari terakhir |
| operations_last_7_days | INTEGER | Operasi dalam 7 hari terakhir |
| total_failed | INTEGER | Total error dari parsing_logs |
| trending_level | VARCHAR(10) | Level trending (high/medium/low) |

Sorted by `operations_last_30_days` DESC, `reparse_count` DESC, `jumlah_dilihat` DESC

Filter: `(SELECT COUNT(*) FROM parsing_logs WHERE peraturan_id = peraturan.id) > 0`

### database_health

Health check untuk database.

| Column | Type | Description |
|--------|------|-------------|
| table_name | TEXT | Nama tabel |
| total_rows | INTEGER | Total rows |
| unique_categories | INTEGER | Kategori unik (hanya untuk peraturan) |
| unique_years | INTEGER | Tahun unik (hanya untuk peraturan) |
| oldest_record | TIMESTAMP | Record tertua |
| newest_record | TIMESTAMP | Record terbaru |
| rows_with_pdf | INTEGER | Rows dengan PDF (hanya untuk peraturan) |
| rows_with_pasal | INTEGER | Rows dengan pasal (hanya untuk peraturan) |
| rows_without_pasal | INTEGER | Rows tanpa pasal (hanya untuk peraturan) |
| avg_reparse_count | NUMERIC | Rata-rata reparse count (hanya untuk peraturan) |

Hasil dari UNION ALL semua tabel (peraturan, bab, pasals, ayats, parsing_logs).

### parsing_statistics

Statistik parsing operations.

| Column | Type | Description |
|--------|------|-------------|
| action | VARCHAR(50) | Tipe action |
| status | VARCHAR(20) | Status |
| total | INTEGER | Total operations |
| unique_peraturan | INTEGER | Peraturan unik |
| pertama | TIMESTAMP | Waktu operasi pertama |
| terakhir | TIMESTAMP | Waktu operasi terakhir |
| avg_interval_seconds | NUMERIC | Rata-rata interval antar operations |
| total_duration_seconds | INTEGER | Total durasi (seconds) |
| avg_duration_seconds | NUMERIC | Rata-rata durasi (seconds) |
| avg_bab_count | NUMERIC | Rata-rata bab count |
| avg_pasal_count | NUMERIC | Rata-rata pasal count |
| avg_ayat_count | NUMERIC | Rata-rata ayat count |

Grouped by `action`, `status`, sorted by `action`, `status`.

### peraturan_parsing_history

Parsing history per peraturan.

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | ID log |
| peraturan_id | VARCHAR(255) | ID peraturan |
| judul_peraturan | VARCHAR(1000) | Judul peraturan |
| nomor_peraturan | VARCHAR(100) | Nomor peraturan |
| action | VARCHAR(50) | Tipe action |
| status | VARCHAR(20) | Status |
| error_message | TEXT | Error message |
| parsed_at | TIMESTAMP | Waktu parsing |
| metadata | JSONB | Metadata tambahan |
| duration_from_previous | NUMERIC | Durasi dari operasi sebelumnya |

Sorted by `peraturan_id`, `parsed_at` DESC.

## Functions

### update_updated_at_column()

Trigger function untuk otomatis update kolom `updated_at` saat row di-update.

**Usage:** Attached sebagai trigger pada tabel peraturan, bab, pasals, dan ayats.

### generate_peraturan_id()

Generate ID peraturan dari kategori, nomor, dan tahun.

**Format:** `{kategori}-{nomor}-{tahun}`

**Usage:** Bisa di-attach sebagai trigger pada tabel peraturan (opsional).

### increment_reparse_count()

Increment reparse_count dan update last_reparse_at.

**Usage:** Trigger function untuk update otomatis saat re-parse.

### log_parsing_operation(p_peraturan_id, p_action, p_status, p_error_message, p_metadata)

Log parsing operation ke tabel `parsing_logs`.

**Parameters:**
- `p_peraturan_id` - ID peraturan
- `p_action` - Tipe action (create, update, reparse)
- `p_status` - Status (success, failed, running)
- `p_error_message` - Error message (optional)
- `p_metadata` - JSONB metadata (optional)

### cleanup_old_parsing_logs(days_to_keep)

Hapus parsing logs yang lebih lama dari `days_to_keep` hari.

**Default:** 90 hari

**Returns:** Number of rows deleted

### get_parsing_stats(start_date, end_date)

Dapatkan statistik parsing untuk rentang tanggal tertentu.

**Parameters:**
- `start_date` - Tanggal mulai (optional)
- `end_date` - Tanggal akhir (optional)

**Returns:** Table dengan:
- `action` - Tipe action
- `status` - Status
- `count` - Jumlah operations
- `success_rate` - Persentase success
- `avg_time_minutes` - Rata-rata waktu (menit)

### update_peraturan_pasal_count()

Update peraturan metadata saat pasal diinsert/delete.

**Usage:** Trigger function yang akan otomatis mengupdate count pasal di metadata peraturan saat insert atau delete pasal.

### update_pasal_ayat_count()

Update pasal metadata saat ayat diinsert/delete.

**Usage:** Trigger function yang akan otomatis mengupdate count ayat di metadata pasal saat insert atau delete ayat.

## Triggers

### update_peraturan_updated_at

**Table:** peraturan  
**Event:** BEFORE UPDATE  
**Action:** Update `updated_at` ke CURRENT_TIMESTAMP

### update_bab_updated_at

**Table:** bab  
**Event:** BEFORE UPDATE  
**Action:** Update `updated_at` ke CURRENT_TIMESTAMP

### update_pasal_updated_at

**Table:** pasals  
**Event:** BEFORE UPDATE  
**Action:** Update `updated_at` ke CURRENT_TIMESTAMP

### update_ayat_updated_at

**Table:** ayats  
**Event:** BEFORE UPDATE  
**Action:** Update `updated_at` ke CURRENT_TIMESTAMP

## Migrations

Database menggunakan migration system dengan file SQL bernomor di folder `migrations/`:

1. `001_create_tables.sql` - Create semua tables (peraturan, bab, pasals, ayats, parsing_logs)
2. `002_create_indexes.sql` - Create semua indexes untuk performa
3. `003_create_functions_triggers.sql` - Create functions dan triggers
4. `004_create_views.sql` - Create views untuk monitoring
5. `005_sample_data.sql` - Sample data lengkap

### Cara Menjalankan Migrations

```bash
# Connect ke database
docker exec -it peraturan_postgres psql -U postgres -d peraturan_db

# Jalankan semua migrations
\i /docker-entrypoint-initdb.d/001_create_tables.sql
\i /docker-entrypoint-initdb.d/002_create_indexes.sql
\i /docker-entrypoint-initdb.d/003_create_functions_triggers.sql
\i /docker-entrypoint-initdb.d/004_create_views.sql
\i /docker-entrypoint-initdb.d/005_sample_data.sql
```

## Sample Queries

### Query Peraturan dengan Bab dan Pasal

```sql
SELECT
    p.id,
    p.judul,
    p.nomor,
    p.tahun,
    p.kategori,
    b.nomor_bab,
    b.judul_bab,
    ps.nomor_pasal,
    ps.judul_pasal,
    ps.konten_pasal
FROM peraturan p
LEFT JOIN bab b ON p.id = b.peraturan_id
LEFT JOIN pasals ps ON b.id = ps.bab_id
WHERE p.id = 'uu-1-2026'
ORDER BY b.urutan, ps.urutan;
```

### Query Pasal dengan Ayat

```sql
SELECT
    ps.id,
    ps.peraturan_id,
    ps.nomor_pasal,
    ps.judul_pasal,
    ps.konten_pasal,
    ps.urutan,
    a.nomor_ayat,
    a.konten_ayat,
    a.urutan as ayat_urutan
FROM pasals ps
LEFT JOIN ayats a ON ps.id = a.pasal_id
WHERE ps.peraturan_id = 'uu-1-2026'
ORDER BY ps.urutan, a.urutan;
```

### Query Peraturan dengan Count Pasal dan Ayat

```sql
SELECT
    p.*,
    COUNT(DISTINCT b.id) as total_bab,
    COUNT(DISTINCT ps.id) as total_pasal,
    COUNT(DISTINCT a.id) as total_ayat
FROM peraturan p
LEFT JOIN bab b ON p.id = b.peraturan_id
LEFT JOIN pasals ps ON b.id = ps.bab_id OR ps.peraturan_id = p.id
LEFT JOIN ayats a ON ps.id = a.pasal_id
WHERE p.id = 'uu-1-2026'
GROUP BY p.id;
```

### Full-Text Search di Pasal

```sql
SELECT
    ps.*,
    b.nomor_bab,
    p.judul as judul_peraturan,
    p.nomor as nomor_peraturan,
    ts_rank(
        to_tsvector('indonesian', ps.nomor_pasal || ' ' || COALESCE(ps.judul_pasal, '') || ' ' || ps.konten_pasal),
        plainto_tsquery('indonesian', 'pidana minimum')
    ) as rank
FROM pasals ps
LEFT JOIN bab b ON ps.bab_id = b.id
LEFT JOIN peraturan p ON ps.peraturan_id = p.id
WHERE to_tsvector('indonesian', ps.nomor_pasal || ' ' || COALESCE(ps.judul_pasal, '') || ' ' || ps.konten_pasal)
      @@ plainto_tsquery('indonesian', 'pidana minimum')
ORDER BY rank DESC;
```

### Query Peraturan yang Perlu Re-parse

```sql
SELECT
    p.*,
    COUNT(DISTINCT ps.id) as total_pasal,
    EXTRACT(DAY FROM CURRENT_TIMESTAMP - COALESCE(p.parsed_at, p.created_at)) as hari_sejak_terakhir,
    CASE
        WHEN p.parsed_at IS NULL THEN 10
        WHEN COUNT(DISTINCT ps.id) = 0 THEN 9
        WHEN EXTRACT(DAY FROM CURRENT_TIMESTAMP - COALESCE(p.parsed_at, p.created_at)) > 180 THEN 8
        WHEN p.reparse_count < 2 THEN 5
        ELSE 1
    END as prioritas_reparse
FROM peraturan p
LEFT JOIN pasals ps ON p.id = ps.peraturan_id
WHERE
    p.parsed_at IS NULL
    OR EXTRACT(DAY FROM CURRENT_TIMESTAMP - COALESCE(p.parsed_at, p.created_at)) > 180
    OR p.reparse_count < 2
    OR COUNT(DISTINCT ps.id) = 0
GROUP BY p.id
ORDER BY prioritas_reparse DESC, COALESCE(p.parsed_at, p.created_at) ASC
LIMIT 10;
```

### Query Parsing Stats per Kategori

```sql
SELECT
    p.kategori,
    COUNT(DISTINCT p.id) as total_peraturan,
    COUNT(DISTINCT ps.id) as total_pasal,
    COUNT(DISTINCT a.id) as total_ayat,
    AVG(p.reparse_count) as rata_reparse,
    SUM(CASE WHEN ps.konten_pasal IS NOT NULL THEN 1 ELSE 0 END) as jumlah_dengan_konten
FROM peraturan p
LEFT JOIN bab b ON p.id = b.peraturan_id
LEFT JOIN pasals ps ON b.id = ps.bab_id
LEFT JOIN ayats a ON ps.id = a.pasal_id
GROUP BY p.kategori
ORDER BY total_peraturan DESC;
```

## Best Practices

### 1. Query Optimization

**Gunakan Views untuk Query Kompleks:**
- Views yang tersedia sudah ter-optimasi dengan indexes
- Hindari subquery yang kompleks di query langsung

**Full-Text Search:**
- Gunakan `to_tsvector` dan `plainto_tsquery` untuk pencarian Indonesian yang optimal
- Kolom yang di-index: pasals.nomor_pasal, pasals.judul_pasal, pasals.konten_pasal

**Pagination:**
- Gunakan `LIMIT` dan `OFFSET` untuk data yang besar
- Untuk pagination cepat di table besar, gunakan cursor-based pagination

**Batch Inserts:**
- Untuk insert banyak data, gunakan batch inserts
- Gunakan transactions untuk memastikan consistency

### 2. Data Integrity

**Foreign Key Constraints:**
- DELETE CASCADE akan otomatis menghapus data child ketika parent dihapus
- Misal: menghapus peraturan akan menghapus semua bab, pasals, dan ayats terkait

**Triggers:**
- Kolom `updated_at` otomatis ter-update, tidak perlu manual
- Triggers untuk count update akan menjaga consistency metadata

**Transaction Management:**
- Gunakan transactions untuk operasi yang melibatkan multiple tables
- Commit setelah semua operasi berhasil, rollback jika ada error

### 3. Performance Tuning

**Indexes:**
- Semua filter/sort penting sudah ada indexes
- Gunakan indexes yang sudah ada untuk performa optimal
- Hindari indexes yang tidak perlu untuk optimasi write performance

**Query Planning:**
- Gunakan `EXPLAIN ANALYZE` untuk memeriksa query plan
- Pastikan query menggunakan indexes yang benar

**Connection Pooling:**
- Gunakan connection pool untuk mengurangi overhead
- Atur min/max connections sesuai kebutuhan aplikasi

### 4. Data Normalization

**Struktur Tabel:**
- Data sudah dinormalisasi ke level 3NF
- Tidak ada data duplicate (kecuali intentionally untuk caching)

**Data Redundancy:**
- Tidak perlu menyimpan konten lengkap di tabel peraturan karena sudah ada di pasals
- Metadata peraturan bisa menyimpan summary (bab_count, pasal_count, ayat_count)

**Hierarki Data:**
- Peraturan → Bab → Pasal → Ayat (4 level hierarchy)
- Setiap level memiliki foreign key ke level di atasnya

## Future Enhancements

- [ ] Implement materialized views untuk reporting
- [ ] Implement partitioning untuk tabel besar (peraturan, pasals, ayats)
- [ ] Implement caching layer (Redis/Memcached) untuk frequent queries
- [ ] Implement audit logging untuk semua CRUD operations
- [ ] Implement data archival strategy untuk old records
- [ ] Implement full-text search dengan phrase search dan fuzzy matching
- [ ] Implement vector embedding untuk semantic search
- [ ] Implement CDC (Change Data Capture) untuk real-time updates
- [ ] Implement read replicas untuk horizontal scaling