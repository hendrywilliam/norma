-- Migration 005: Sample Data
-- File ini untuk mengisi sample data untuk semua tabel
-- Termasuk: peraturan, bab, pasals, ayats, parsing_logs

-- ========================================
-- 1. SAMPLE DATA untuk peraturan
-- ========================================

INSERT INTO peraturan (
    id, judul, nomor, tahun, kategori, url, pdf_url,
    jenis_peraturan, pemrakarsa, tentang, tempat_penetapan,
    tanggal_ditetapkan, pejabat_menetapkan, status_peraturan,
    jumlah_dilihat, jumlah_download, tanggal_diundangkan,
    tanggal_disahkan, deskripsi, metadata, created_at, parsed_at, reparse_count
) VALUES
-- Peraturan 1: UU No. 1 Tahun 2026
(
    'uu-1-2026',
    'Undang-Undang Nomor 1 Tahun 2026 tentang Penyesuaian Pidana',
    '1',
    2026,
    'UU',
    'https://peraturan.go.id/uu/1/2026',
    'https://peraturan.go.id/files/uu-1-2026.pdf',
    'UNDANG-UNDANG',
    'PEMERINTAH PUSAT',
    'PENYESUAIAN PIDANA',
    'Jakarta',
    '2026-01-02',
    'PRABOWO SUBIANTO',
    'Berlaku',
    67200,
    71045,
    '2026-01-10',
    '2026-01-02',
    'Undang-Undang tentang penyesuaian pidana dalam undang-undang di luar KUHP',
    '{"keywords": ["penyesuaian pidana", "kuhp", "keadilan"], "page_count": 45, "author": "DPR RI"}',
    '2026-01-01 00:00:00',
    '2026-01-25 10:30:00',
    1
),

-- Peraturan 2: PP No. 10 Tahun 2023
(
    'pp-10-2023',
    'Peraturan Pemerintah Nomor 10 Tahun 2023 tentang Perlindungan Data Pribadi',
    '10',
    2023,
    'PP',
    'https://peraturan.go.id/pp/10/2023',
    'https://peraturan.go.id/files/pp-10-2023.pdf',
    'PERATURAN PEMERINTAH',
    'PEMERINTAH PUSAT',
    'PERLINDUNGAN DATA PRIBADI',
    'Jakarta',
    '2023-06-10',
    'PRESIDEN REPUBLIK INDONESIA',
    'Berlaku',
    25000,
    18000,
    '2023-06-15',
    '2023-06-10',
    'Peraturan Pemerintah tentang perlindungan data pribadi',
    '{"keywords": ["data pribadi", "perlindungan", "privasi"], "page_count": 38, "author": "Presiden RI"}',
    '2023-06-01 00:00:00',
    '2023-06-20 14:15:00',
    2
),

-- Peraturan 3: Perpres No. 15 Tahun 2023
(
    'perpres-15-2023',
    'Peraturan Presiden Nomor 15 Tahun 2023 tentang Transformasi Digital',
    '15',
    2023,
    'Perpres',
    'https://peraturan.go.id/perpres/15/2023',
    'https://peraturan.go.id/files/perpres-15-2023.pdf',
    'PERATURAN PRESIDEN',
    'PEMERINTAH PUSAT',
    'TRANSFORMASI DIGITAL',
    'Jakarta',
    '2023-03-20',
    'PRESIDEN REPUBLIK INDONESIA',
    'Berlaku',
    18000,
    12000,
    '2023-03-25',
    '2023-03-20',
    'Peraturan Presiden tentang transformasi digital',
    '{"keywords": ["transformasi digital", "teknologi", "inovasi"], "page_count": 22, "author": "Presiden RI"}',
    '2023-03-15 00:00:00',
    '2023-04-01 09:00:00',
    1
),

-- Peraturan 4: UU Cipta Kerja (tanpa pasal, perlu parsing)
(
    'uu-11-2022',
    'Undang-Undang Nomor 11 Tahun 2022 tentang Cipta Kerja',
    '11',
    2022,
    'UU',
    'https://peraturan.go.id/uu/11/2022',
    'https://peraturan.go.id/files/uu-11-2022.pdf',
    'UNDANG-UNDANG',
    'PEMERINTAH PUSAT',
    'CITA KERJA',
    'Jakarta',
    '2020-10-05',
    'PRESIDEN REPUBLIK INDONESIA',
    'Berlaku',
    35000,
    28000,
    '2020-11-02',
    '2020-10-05',
    'Undang-Undang Cipta Kerja',
    '{"keywords": ["cinta kerja", "investasi", "ekonomi"], "page_count": 0}',
    '2022-01-10 00:00:00',
    NULL,
    0
),

-- Peraturan 5: Permen Kominfo
(
    'permen-5-2023',
    'Peraturan Menteri Komunikasi dan Informatika Nomor 5 Tahun 2023 tentang Penyelenggaraan Sistem Elektronik',
    '5',
    2023,
    'Permen',
    'https://peraturan.go.id/permen/5/2023',
    'https://peraturan.go.id/files/permen-5-2023.pdf',
    'PERATURAN MENTERI',
    'PEMERINTAH PUSAT',
    'PENYELENGGARAAN SISTEM ELEKTRONIK',
    'Jakarta',
    '2023-02-10',
    'MENTERI KOMUNIKASI DAN INFORMATIKA',
    'Berlaku',
    12000,
    8500,
    '2023-02-15',
    '2023-02-10',
    'Peraturan Menteri tentang penyelenggaraan sistem elektronik',
    '{"keywords": ["sistem elektronik", "komunikasi", "informatika"], "page_count": 18, "author": "Menkominfo"}',
    '2023-02-05 00:00:00',
    '2023-02-20 11:45:00',
    1
)
ON CONFLICT (url) DO NOTHING;

-- ========================================
-- 2. SAMPLE DATA untuk bab
-- ========================================

-- Bab untuk UU No. 1 Tahun 2026
INSERT INTO bab (peraturan_id, nomor_bab, judul_bab, urutan) VALUES
('uu-1-2026', 'I', 'PENYESUAIAN PIDANA DALAM UNDANG-UNDANG DI LUAR UNDANG-UNDANG NOMOR 1 TAHUN 2023 TENTANG KITAB UNDANG-UNDANG HUKUM PIDANA', 1),
('uu-1-2026', 'II', 'KETENTUAN PENYIDIKAN', 2),
('uu-1-2026', 'III', 'KETENTUAN PIDANA', 3),
('uu-1-2026', 'IV', 'KETENTUAN PENUTUP', 4)
ON CONFLICT (peraturan_id, nomor_bab) DO NOTHING;

-- Bab untuk PP No. 10 Tahun 2023
INSERT INTO bab (peraturan_id, nomor_bab, judul_bab, urutan) VALUES
('pp-10-2023', 'I', 'KETENTUAN UMUM', 1),
('pp-10-2023', 'II', 'HAK DATA PRIBADI', 2),
('pp-10-2023', 'III', 'PENGENDALIAN PENGOLAHAN DATA PRIBADI', 3),
('pp-10-2023', 'IV', 'HAK SUBYEK DATA PRIBADI', 4),
('pp-10-2023', 'V', 'KETENTUAN PENUTUP', 5)
ON CONFLICT (peraturan_id, nomor_bab) DO NOTHING;

-- Bab untuk Perpres No. 15 Tahun 2023
INSERT INTO bab (peraturan_id, nomor_bab, judul_bab, urutan) VALUES
('perpres-15-2023', 'I', 'KETENTUAN UMUM', 1),
('perpres-15-2023', 'II', 'STRATEGI DAN PROGRAM', 2),
('perpres-15-2023', 'III', 'PENYELENGGARAAN', 3),
('perpres-15-2023', 'IV', 'KETENTUAN PENUTUP', 4)
ON CONFLICT (peraturan_id, nomor_bab) DO NOTHING;

-- Bab untuk Permen Kominfo
INSERT INTO bab (peraturan_id, nomor_bab, judul_bab, urutan) VALUES
('permen-5-2023', 'I', 'KETENTUAN UMUM', 1),
('permen-5-2023', 'II', 'HAK DAN KEWAJIBAN', 2),
('permen-5-2023', 'III', 'PENGAWASAN', 3),
('permen-5-2023', 'IV', 'KETENTUAN SANKSI', 4)
ON CONFLICT (peraturan_id, nomor_bab) DO NOTHING;

-- ========================================
-- 3. SAMPLE DATA untuk pasals
-- ========================================

-- Pasals untuk UU No. 1 Tahun 2026
INSERT INTO pasals (peraturan_id, bab_id, nomor_pasal, judul_pasal, konten_pasal, urutan, metadata) VALUES
-- BAB I
('uu-1-2026', (SELECT id FROM bab WHERE peraturan_id = 'uu-1-2026' AND nomor_bab = 'I'), '1', NULL,
'Dalam hal Undang-Undang di luar Undang-Undang Nomor 1 Tahun 2023 tentang Kitab Undang-Undang Hukum Pidana memuat ancaman pidana minimum khusus, ketentuan ancaman pidana minimum khusus dihapus. Ancaman pidana minimum khusus sebagaimana dimaksud pada ayat (1) adalah ancaman pidana yang ditetapkan dengan batas minimum yang harus dijatuhkan hakim. Penghapusan ancaman pidana minimum khusus sebagaimana dimaksud pada ayat (1) tidak mengurangi sifat khusus dari ancaman pidana tersebut.',
1, '{"keywords": ["pidana minimum khusus", "hapus", "kuhp"]}'),

('uu-1-2026', (SELECT id FROM bab WHERE peraturan_id = 'uu-1-2026' AND nomor_bab = 'I'), '2', NULL,
'Dalam hal Undang-Undang di luar Undang-Undang Nomor 1 Tahun 2023 tentang Kitab Undang-Undang Hukum Pidana memuat ancaman pidana yang bertentangan dengan prinsip keadilan, ketentuan ancaman pidana tersebut disesuaikan. Prinsip keadilan sebagaimana dimaksud pada ayat (1) meliputi: proporsionalitas antara tindak pidana dengan ancaman pidana; kesesuaian dengan maksud undang-undang; dan pertimbangan kepentingan umum.',
2, '{"keywords": ["prinsip keadilan", "penyesuaian", "proporsionalitas"]}'),

-- BAB II
('uu-1-2026', (SELECT id FROM bab WHERE peraturan_id = 'uu-1-2026' AND nomor_bab = 'II'), '3', NULL,
'Penyidikan tindak pidana yang diatur dalam Undang-Undang ini dilakukan oleh penyidik pejabat penyidik pegawai negeri sipil sebagaimana dimaksud dalam Kitab Undang-Undang Hukum Acara Pidana. Dalam hal terdapat penyidik khusus sebagaimana diatur dalam undang-undang lain, penyidikan dapat dilakukan oleh penyidik khusus tersebut.',
3, '{"keywords": ["penyidikan", "penyidik", "kuhap"]}'),

('uu-1-2026', (SELECT id FROM bab WHERE peraturan_id = 'uu-1-2026' AND nomor_bab = 'II'), '4', NULL,
'Penyidikan tindak pidana sebagaimana dimaksud dalam Undang-Undang ini harus dilakukan dengan memperhatikan prinsip keadilan, kepentingan umum, dan perlindungan hak asasi manusia. Penyidik wajib menghormati hak-hak tersangka sebagaimana diatur dalam Kitab Undang-Undang Hukum Acara Pidana.',
4, '{"keywords": ["prinsip keadilan", "hak asasi manusia", "tersangka"]}'),

-- BAB III
('uu-1-2026', (SELECT id FROM bab WHERE peraturan_id = 'uu-1-2026' AND nomor_bab = 'III'), '5', NULL,
'Setiap orang yang dengan sengaja melanggar ketentuan sebagaimana dimaksud dalam Undang-Undang ini dipidana dengan pidana penjara paling lama 5 (lima) tahun atau pidana denda paling banyak Rp5.000.000.000,00 (lima miliar rupiah). Dalam hal pelanggaran sebagaimana dimaksud pada ayat (1) mengakibatkan kerugian finansial, pidana denda dapat ditambah sebesar kerugian tersebut. Tindak pidana sebagaimana dimaksud pada ayat (1) adalah kejahatan.',
5, '{"keywords": ["pidana penjara", "pidana denda", "kejahatan"]}'),

-- BAB IV
('uu-1-2026', (SELECT id FROM bab WHERE peraturan_id = 'uu-1-2026' AND nomor_bab = 'IV'), '6', NULL,
'Undang-Undang ini mulai berlaku pada tanggal diundangkan. Agar setiap orang mengetahuinya, memerintahkan pengundangan Undang-Undang ini dengan penempatannya dalam Lembaran Negara Republik Indonesia.',
6, '{"keywords": ["mulai berlaku", "pengundangan", "lembaran negara"]}')
ON CONFLICT (peraturan_id, nomor_pasal) DO NOTHING;

-- Pasals untuk PP No. 10 Tahun 2023
INSERT INTO pasals (peraturan_id, bab_id, nomor_pasal, judul_pasal, konten_pasal, urutan, metadata) VALUES
-- BAB I
('pp-10-2023', (SELECT id FROM bab WHERE peraturan_id = 'pp-10-2023' AND nomor_bab = 'I'), '1', 'Definisi',
'Dalam Peraturan Pemerintah ini yang dimaksud dengan: a. Data pribadi adalah setiap data tentang orang perseorangan yang teridentifikasi atau dapat diidentifikasi secara langsung atau tidak langsung; b. Pengendali data pribadi adalah pihak yang menentukan tujuan dan kendali pengolahan data pribadi.',
1, '{"keywords": ["data pribadi", "definisi", "pengendali"]}'),

('pp-10-2023', (SELECT id FROM bab WHERE peraturan_id = 'pp-10-2023' AND nomor_bab = 'I'), '2', 'Ruang Lingkup',
'Peraturan Pemerintah ini mengatur tentang perlindungan data pribadi yang dikelola di wilayah Negara Kesatuan Republik Indonesia.',
2, '{"keywords": ["ruang lingkup", "wilayah", "nkri"]}'),

-- BAB II
('pp-10-2023', (SELECT id FROM bab WHERE peraturan_id = 'pp-10-2023' AND nomor_bab = 'II'), '4', 'Hak Menghapus Data',
'Subjek data pribadi berhak menghapus data pribadi yang dikelola oleh Pengendali Data Pribadi apabila: a. tujuan pengolahan data pribadi tidak lagi tercapai; b. data pribadi tidak digunakan lagi untuk keperluan pengolahan; atau c. pengolahan data pribadi melawan ketentuan peraturan perundang-undangan.',
3, '{"keywords": ["hapus", "data pribadi", "hak"]}'),

('pp-10-2023', (SELECT id FROM bab WHERE peraturan_id = 'pp-10-2023' AND nomor_bab = 'II'), '5', 'Hak Memperbaiki Data',
'Subjek data pribadi berhak memperbaiki data pribadi yang tidak benar, tidak lengkap, atau tidak diperbarui sebagaimana dimaksud dalam ketentuan peraturan perundang-undangan.',
4, '{"keywords": ["perbaiki", "data pribadi", "update"]}'),

-- BAB III
('pp-10-2023', (SELECT id FROM bab WHERE peraturan_id = 'pp-10-2023' AND nomor_bab = 'III'), '8', 'Prinsip Transparansi',
'Pengendali Data Pribadi wajib menerapkan prinsip transparansi dalam pengolahan data pribadi dengan cara: a. memberikan informasi yang jelas dan mudah dipahami tentang pengolahan data pribadi; b. memperbaharui informasi secara berkala; dan c. menyediakan salinan informasi apabila diminta oleh Subjek Data Pribadi.',
5, '{"keywords": ["transparansi", "informasi", "update"]}'),

-- BAB IV
('pp-10-2023', (SELECT id FROM bab WHERE peraturan_id = 'pp-10-2023' AND nomor_bab = 'IV'), '11', 'Hak Keberatan',
'Subjek Data Pribadi berhak mengajukan keberatan terhadap keputusan yang dihasilkan berdasarkan pengolahan data pribadi secara otomatis yang memberikan dampak hukum atau dampak penting lainnya terhadap Subjek Data Pribadi.',
6, '{"keywords": ["keberatan", "otomatis", "dampak hukum"]}'),

-- BAB V
('pp-10-2023', (SELECT id FROM bab WHERE peraturan_id = 'pp-10-2023' AND nomor_bab = 'V'), '15', 'Mulai Berlaku',
'Peraturan Pemerintah ini mulai berlaku pada tanggal diundangkan.',
7, '{"keywords": ["mulai berlaku", "pengundangan"]}')
ON CONFLICT (peraturan_id, nomor_pasal) DO NOTHING;

-- Pasals untuk Perpres No. 15 Tahun 2023
INSERT INTO pasals (peraturan_id, bab_id, nomor_pasal, judul_pasal, konten_pasal, urutan, metadata) VALUES
-- BAB I
('perpres-15-2023', (SELECT id FROM bab WHERE peraturan_id = 'perpres-15-2023' AND nomor_bab = 'I'), '1', 'Definisi',
'Dalam Peraturan Presiden ini yang dimaksud dengan: a. Transformasi digital adalah proses integrasi teknologi digital ke dalam semua aspek kehidupan; b. Ekonomi digital adalah kegiatan ekonomi yang didukung oleh teknologi digital.',
1, '{"keywords": ["transformasi digital", "definisi", "ekonomi digital"]}'),

-- BAB II
('perpres-15-2023', (SELECT id FROM bab WHERE peraturan_id = 'perpres-15-2023' AND nomor_bab = 'II'), '3', 'Strategi Nasional',
'Pemerintah menyusun Strategi Nasional Transformasi Digital sebagai pedoman pelaksanaan transformasi digital di Indonesia.',
2, '{"keywords": ["strategi", "pedoman", "nasional"]}'),

-- BAB IV
('perpres-15-2023', (SELECT id FROM bab WHERE peraturan_id = 'perpres-15-2023' AND nomor_bab = 'IV'), '8', 'Mulai Berlaku',
'Peraturan Presiden ini mulai berlaku pada tanggal diundangkan.',
3, '{"keywords": ["mulai berlaku", "pengundangan"]}')
ON CONFLICT (peraturan_id, nomor_pasal) DO NOTHING;

-- Pasals untuk Permen Kominfo
INSERT INTO pasals (peraturan_id, bab_id, nomor_pasal, judul_pasal, konten_pasal, urutan, metadata) VALUES
-- BAB I
('permen-5-2023', (SELECT id FROM bab WHERE peraturan_id = 'permen-5-2023' AND nomor_bab = 'I'), '1', 'Definisi',
'Dalam Peraturan Menteri ini yang dimaksud dengan: a. Sistem Elektronik adalah rangkaian perangkat dan prosedur yang bekerja secara elektronik.',
1, '{"keywords": ["sistem elektronik", "definisi"]}'),

-- BAB II
('permen-5-2023', (SELECT id FROM bab WHERE peraturan_id = 'permen-5-2023' AND nomor_bab = 'II'), '2', 'Hak Pengguna',
'Pengguna Sistem Elektronik berhak mendapatkan perlindungan terhadap data dan informasi pribadinya.',
2, '{"keywords": ["hak", "pengguna", "perlindungan"]}'),

-- BAB III
('permen-5-2023', (SELECT id FROM bab WHERE peraturan_id = 'permen-5-2023' AND nomor_bab = 'III'), '5', 'Pengawasan',
'Pengawasan terhadap Penyelenggara Sistem Elektronik dilakukan oleh Kementerian.',
3, '{"keywords": ["pengawasan", "penyelenggara", "kementerian"]}'),

-- BAB IV
('permen-5-2023', (SELECT id FROM bab WHERE peraturan_id = 'permen-5-2023' AND nomor_bab = 'IV'), '7', 'Sanksi Administratif',
'Pelanggaran terhadap ketentuan dalam Peraturan Menteri ini dikenakan sanksi administratif berupa peringatan tertulis, pembatasan kegiatan, atau penghentian kegiatan.',
4, '{"keywords": ["sanksi", "administratif", "peringatan"]}')
ON CONFLICT (peraturan_id, nomor_pasal) DO NOTHING;

-- ========================================
-- 4. SAMPLE DATA untuk ayats
-- ========================================

-- Ayats untuk Pasal 1 - UU No. 1 Tahun 2026
INSERT INTO ayats (pasal_id, nomor_ayat, konten_ayat, urutan, metadata) VALUES
((SELECT id FROM pasals WHERE peraturan_id = 'uu-1-2026' AND nomor_pasal = '1'), '(1)', 'Dalam hal Undang-Undang di luar Undang-Undang Nomor 1 Tahun 2023 tentang Kitab Undang-Undang Hukum Pidana memuat ancaman pidana minimum khusus, ketentuan ancaman pidana minimum khusus dihapus.', 1, '{}'),
((SELECT id FROM pasals WHERE peraturan_id = 'uu-1-2026' AND nomor_pasal = '1'), '(2)', 'Ancaman pidana minimum khusus sebagaimana dimaksud pada ayat (1) adalah ancaman pidana yang ditetapkan dengan batas minimum yang harus dijatuhkan hakim.', 2, '{}'),
((SELECT id FROM pasals WHERE peraturan_id = 'uu-1-2026' AND nomor_pasal = '1'), '(3)', 'Penghapusan ancaman pidana minimum khusus sebagaimana dimaksud pada ayat (1) tidak mengurangi sifat khusus dari ancaman pidana tersebut.', 3, '{}'),

-- Ayats untuk Pasal 2 - UU No. 1 Tahun 2026
((SELECT id FROM pasals WHERE peraturan_id = 'uu-1-2026' AND nomor_pasal = '2'), '(1)', 'Dalam hal Undang-Undang di luar Undang-Undang Nomor 1 Tahun 2023 tentang Kitab Undang-Undang Hukum Pidana memuat ancaman pidana yang bertentangan dengan prinsip keadilan, ketentuan ancaman pidana tersebut disesuaikan.', 1, '{}'),
((SELECT id FROM pasals WHERE peraturan_id = 'uu-1-2026' AND nomor_pasal = '2'), '(2)', 'Prinsip keadilan sebagaimana dimaksud pada ayat (1) meliputi: a. proporsionalitas antara tindak pidana dengan ancaman pidana; b. kesesuaian dengan maksud undang-undang; dan c. pertimbangan kepentingan umum.', 2, '{}'),

-- Ayats untuk Pasal 3 - UU No. 1 Tahun 2026
((SELECT id FROM pasals WHERE peraturan_id = 'uu-1-2026' AND nomor_pasal = '3'), '(1)', 'Penyidikan tindak pidana yang diatur dalam Undang-Undang ini dilakukan oleh penyidik pejabat penyidik pegawai negeri sipil sebagaimana dimaksud dalam Kitab Undang-Undang Hukum Acara Pidana.', 1, '{}'),
((SELECT id FROM pasals WHERE peraturan_id = 'uu-1-2026' AND nomor_pasal = '3'), '(2)', 'Dalam hal terdapat penyidik khusus sebagaimana diatur dalam undang-undang lain, penyidikan dapat dilakukan oleh penyidik khusus tersebut.', 2, '{}'),

-- Ayats untuk Pasal 4 - UU No. 1 Tahun 2026
((SELECT id FROM pasals WHERE peraturan_id = 'uu-1-2026' AND nomor_pasal = '4'), '(1)', 'Penyidikan tindak pidana sebagaimana dimaksud dalam Undang-Undang ini harus dilakukan dengan memperhatikan prinsip keadilan, kepentingan umum, dan perlindungan hak asasi manusia.', 1, '{}'),
((SELECT id FROM pasals WHERE peraturan_id = 'uu-1-2026' AND nomor_pasal = '4'), '(2)', 'Penyidik wajib menghormati hak-hak tersangka sebagaimana diatur dalam Kitab Undang-Undang Hukum Acara Pidana.', 2, '{}'),

-- Ayats untuk Pasal 5 - UU No. 1 Tahun 2026
((SELECT id FROM pasals WHERE peraturan_id = 'uu-1-2026' AND nomor_pasal = '5'), '(1)', 'Setiap orang yang dengan sengaja melanggar ketentuan sebagaimana dimaksud dalam Undang-Undang ini dipidana dengan pidana penjara paling lama 5 (lima) tahun atau pidana denda paling banyak Rp5.000.000.000,00 (lima miliar rupiah).', 1, '{}'),
((SELECT id FROM pasals WHERE peraturan_id = 'uu-1-2026' AND nomor_pasal = '5'), '(2)', 'Dalam hal pelanggaran sebagaimana dimaksud pada ayat (1) mengakibatkan kerugian finansial, pidana denda dapat ditambah sebesar kerugian tersebut.', 2, '{}'),
((SELECT id FROM pasals WHERE peraturan_id = 'uu-1-2026' AND nomor_pasal = '5'), '(3)', 'Tindak pidana sebagaimana dimaksud pada ayat (1) adalah kejahatan.', 3, '{}'),

-- Ayats untuk Pasal 6 - UU No. 1 Tahun 2026
((SELECT id FROM pasals WHERE peraturan_id = 'uu-1-2026' AND nomor_pasal = '6'), '(1)', 'Undang-Undang ini mulai berlaku pada tanggal diundangkan.', 1, '{}'),
((SELECT id FROM pasals WHERE peraturan_id = 'uu-1-2026' AND nomor_pasal = '6'), '(2)', 'Agar setiap orang mengetahuinya, memerintahkan pengundangan Undang-Undang ini dengan penempatannya dalam Lembaran Negara Republik Indonesia.', 2, '{}'),

-- Ayats untuk Pasal 1 - PP No. 10 Tahun 2023
((SELECT id FROM pasals WHERE peraturan_id = 'pp-10-2023' AND nomor_pasal = '1'), '(1)', 'Dalam Peraturan Pemerintah ini yang dimaksud dengan: a. Data pribadi adalah setiap data tentang orang perseorangan yang teridentifikasi atau dapat diidentifikasi secara langsung atau tidak langsung.', 1, '{}'),
((SELECT id FROM pasals WHERE peraturan_id = 'pp-10-2023' AND nomor_pasal = '1'), '(2)', 'Pengendali data pribadi adalah pihak yang menentukan tujuan dan kendali pengolahan data pribadi.', 2, '{}'),

-- Ayats untuk Pasal 4 - PP No. 10 Tahun 2023
((SELECT id FROM pasals WHERE peraturan_id = 'pp-10-2023' AND nomor_pasal = '4'), '(1)', 'Subjek data pribadi berhak menghapus data pribadi yang dikelola oleh Pengendali Data Pribadi apabila: a. tujuan pengolahan data pribadi tidak lagi tercapai; b. data pribadi tidak digunakan lagi untuk keperluan pengolahan; atau c. pengolahan data pribadi melawan ketentuan peraturan perundang-undangan.', 1, '{}'),

-- Ayats untuk Pasal 5 - PP No. 10 Tahun 2023
((SELECT id FROM pasals WHERE peraturan_id = 'pp-10-2023' AND nomor_pasal = '5'), '(1)', 'Subjek data pribadi berhak memperbaiki data pribadi yang tidak benar, tidak lengkap, atau tidak diperbarui sebagaimana dimaksud dalam ketentuan peraturan perundang-undangan.', 1, '{}'),

-- Ayats untuk Pasal 8 - PP No. 10 Tahun 2023
((SELECT id FROM pasals WHERE peraturan_id = 'pp-10-2023' AND nomor_pasal = '8'), '(1)', 'Pengendali Data Pribadi wajib menerapkan prinsip transparansi dalam pengolahan data pribadi dengan cara: a. memberikan informasi yang jelas dan mudah dipahami tentang pengolahan data pribadi; b. memperbaharui informasi secara berkala; dan c. menyediakan salinan informasi apabila diminta oleh Subjek Data Pribadi.', 1, '{}'),

-- Ayats untuk Pasal 11 - PP No. 10 Tahun 2023
((SELECT id FROM pasals WHERE peraturan_id = 'pp-10-2023' AND nomor_pasal = '11'), '(1)', 'Subjek Data Pribadi berhak mengajukan keberatan terhadap keputusan yang dihasilkan berdasarkan pengolahan data pribadi secara otomatis yang memberikan dampak hukum atau dampak penting lainnya terhadap Subjek Data Pribadi.', 1, '{}'),

-- Ayats untuk Pasal 15 - PP No. 10 Tahun 2023
((SELECT id FROM pasals WHERE peraturan_id = 'pp-10-2023' AND nomor_pasal = '15'), '(1)', 'Peraturan Pemerintah ini mulai berlaku pada tanggal diundangkan.', 1, '{}'),

-- Ayats untuk Pasal 1 - Perpres No. 15 Tahun 2023
((SELECT id FROM pasals WHERE peraturan_id = 'perpres-15-2023' AND nomor_pasal = '1'), '(1)', 'Dalam Peraturan Presiden ini yang dimaksud dengan: a. Transformasi digital adalah proses integrasi teknologi digital ke dalam semua aspek kehidupan; b. Ekonomi digital adalah kegiatan ekonomi yang didukung oleh teknologi digital.', 1, '{}'),

-- Ayats untuk Pasal 3 - Perpres No. 15 Tahun 2023
((SELECT id FROM pasals WHERE peraturan_id = 'perpres-15-2023' AND nomor_pasal = '3'), '(1)', 'Pemerintah menyusun Strategi Nasional Transformasi Digital sebagai pedoman pelaksanaan transformasi digital di Indonesia.', 1, '{}'),

-- Ayats untuk Pasal 8 - Perpres No. 15 Tahun 2023
((SELECT id FROM pasals WHERE peraturan_id = 'perpres-15-2023' AND nomor_pasal = '8'), '(1)', 'Peraturan Presiden ini mulai berlaku pada tanggal diundangkan.', 1, '{}'),

-- Ayats untuk Pasal 1 - Permen Kominfo
((SELECT id FROM pasals WHERE peraturan_id = 'permen-5-2023' AND nomor_pasal = '1'), '(1)', 'Dalam Peraturan Menteri ini yang dimaksud dengan: a. Sistem Elektronik adalah rangkaian perangkat dan prosedur yang bekerja secara elektronik.', 1, '{}'),

-- Ayats untuk Pasal 2 - Permen Kominfo
((SELECT id FROM pasals WHERE peraturan_id = 'permen-5-2023' AND nomor_pasal = '2'), '(1)', 'Pengguna Sistem Elektronik berhak mendapatkan perlindungan terhadap data dan informasi pribadinya.', 1, '{}'),

-- Ayats untuk Pasal 5 - Permen Kominfo
((SELECT id FROM pasals WHERE peraturan_id = 'permen-5-2023' AND nomor_pasal = '5'), '(1)', 'Pengawasan terhadap Penyelenggara Sistem Elektronik dilakukan oleh Kementerian.', 1, '{}'),

-- Ayats untuk Pasal 7 - Permen Kominfo
((SELECT id FROM pasals WHERE peraturan_id = 'permen-5-2023' AND nomor_pasal = '7'), '(1)', 'Pelanggaran terhadap ketentuan dalam Peraturan Menteri ini dikenakan sanksi administratif berupa peringatan tertulis, pembatasan kegiatan, atau penghentian kegiatan.', 1, '{}')
ON CONFLICT (pasal_id, nomor_ayat) DO NOTHING;

-- ========================================
-- 5. SAMPLE DATA untuk parsing_logs
-- ========================================

INSERT INTO parsing_logs (peraturan_id, action, status, error_message, metadata) VALUES
-- UU No. 1 Tahun 2026
('uu-1-2026', 'create', 'success', NULL,
    '{"duration_seconds": 120, "bab_count": 4, "pasal_count": 6, "ayat_count": 12, "pages": 45}'),

-- PP No. 10 Tahun 2023
('pp-10-2023', 'create', 'success', NULL,
    '{"duration_seconds": 90, "bab_count": 5, "pasal_count": 7, "ayat_count": 9, "pages": 38}'),
('pp-10-2023', 'reparse', 'success', NULL,
    '{"duration_seconds": 85, "bab_count": 5, "pasal_count": 7, "ayat_count": 9, "pages": 38, "version": 2}'),

-- Perpres No. 15 Tahun 2023
('perpres-15-2023', 'create', 'success', NULL,
    '{"duration_seconds": 60, "bab_count": 4, "pasal_count": 3, "ayat_count": 3, "pages": 22}'),

-- Permen Kominfo
('permen-5-2023', 'create', 'success', NULL,
    '{"duration_seconds": 45, "bab_count": 4, "pasal_count": 4, "ayat_count": 4, "pages": 18}'),

-- UU Cipta Kerja (failed parsing)
('uu-11-2022', 'create', 'failed', 'PDF file not found or corrupted',
    '{"error_type": "download_error", "attempt": 1}'),
('uu-11-2022', 'create', 'failed', 'PDF parsing error: page extraction failed',
    '{"error_type": "parse_error", "attempt": 2}');

-- ========================================
-- Log completion
-- ========================================

DO $$
DECLARE
    peraturan_count INTEGER;
    bab_count INTEGER;
    pasal_count INTEGER;
    ayat_count INTEGER;
    log_count INTEGER;
BEGIN
    -- Count records
    SELECT COUNT(*) INTO peraturan_count FROM peraturan;
    SELECT COUNT(*) INTO bab_count FROM bab;
    SELECT COUNT(*) INTO pasal_count FROM pasals;
    SELECT COUNT(*) INTO ayat_count FROM ayats;
    SELECT COUNT(*) INTO log_count FROM parsing_logs;

    -- Log summary
    RAISE NOTICE 'Migration 005: Sample data inserted successfully!';
    RAISE NOTICE 'Inserted % peraturan records', peraturan_count;
    RAISE NOTICE 'Inserted % bab records', bab_count;
    RAISE NOTICE 'Inserted % pasal records', pasal_count;
    RAISE NOTICE 'Inserted % ayat records', ayat_count;
    RAISE NOTICE 'Inserted % parsing log records', log_count;
    RAISE NOTICE 'Total records inserted: %', peraturan_count + bab_count + pasal_count + ayat_count + log_count;
END $$;
