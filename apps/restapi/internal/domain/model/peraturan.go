package model

import "time"

type Peraturan struct {
	ID                 string     `json:"id" db:"id"`
	Judul              string     `json:"judul" db:"judul"`
	Nomor              string     `json:"nomor" db:"nomor"`
	Tahun              int        `json:"tahun" db:"tahun"`
	Kategori           string     `json:"kategori" db:"kategori"`
	URL                string     `json:"url" db:"url"`
	PDFURL             *string    `json:"pdf_url" db:"pdf_url"`
	JenisPeraturan     *string    `json:"jenis_peraturan" db:"jenis_peraturan"`
	Pemrakarsa         *string    `json:"pemrakarsa" db:"pemrakarsa"`
	Tentang            *string    `json:"tentang" db:"tentang"`
	TempatPenetapan    *string    `json:"tempat_penetapan" db:"tempat_penetapan"`
	TanggalDitetapkan  *time.Time `json:"tanggal_ditetapkan" db:"tanggal_ditetapkan"`
	PejabatMenetapkan  *string    `json:"pejabat_menetapkan" db:"pejabat_menetapkan"`
	StatusPeraturan    string     `json:"status_peraturan" db:"status_peraturan"`
	JumlahDilihat      int        `json:"jumlah_dilihat" db:"jumlah_dilihat"`
	JumlahDownload     int        `json:"jumlah_download" db:"jumlah_download"`
	TanggalDisahkan    *time.Time `json:"tanggal_disahkan" db:"tanggal_disahkan"`
	TanggalDiundangkan *time.Time `json:"tanggal_diundangkan" db:"tanggal_diundangkan"`
	Deskripsi          *string    `json:"deskripsi" db:"deskripsi"`
	Metadata           *string    `json:"metadata" db:"metadata"`
	CreatedAt          time.Time  `json:"created_at" db:"created_at"`
	UpdatedAt          *time.Time `json:"updated_at" db:"updated_at"`
	ParsedAt           *time.Time `json:"parsed_at" db:"parsed_at"`
	ReparseCount       int        `json:"reparse_count" db:"reparse_count"`
	LastReparseAt      *time.Time `json:"last_reparse_at" db:"last_reparse_at"`
}

type PeraturanFilter struct {
	Skip      int
	Limit     int
	Category  *string
	Year      *int
	Jenis     *string
	Status    *string
	Search    *string
	SortBy    *string
	SortOrder string
}

type PeraturanListResponse struct {
	Total int         `json:"total"`
	Skip  int         `json:"skip"`
	Limit int         `json:"limit"`
	Items []Peraturan `json:"items"`
}

type CreatePeraturanRequest struct {
	ID              string  `json:"id" binding:"required"`
	Judul           string  `json:"judul" binding:"required"`
	Nomor           string  `json:"nomor" binding:"required"`
	Tahun           int     `json:"tahun" binding:"required"`
	Kategori        string  `json:"kategori" binding:"required"`
	URL             string  `json:"url" binding:"required"`
	PDFURL          *string `json:"pdf_url"`
	JenisPeraturan  *string `json:"jenis_peraturan"`
	Pemrakarsa      *string `json:"pemrakarsa"`
	Tentang         *string `json:"tentang"`
	TempatPenetapan *string `json:"tempat_penetapan"`
	StatusPeraturan string  `json:"status_peraturan"`
	JumlahDilihat   int     `json:"jumlah_dilihat"`
	JumlahDownload  int     `json:"jumlah_download"`
}

type UpdatePeraturanRequest struct {
	Judul           *string `json:"judul"`
	Nomor           *string `json:"nomor"`
	Tahun           *int    `json:"tahun"`
	Kategori        *string `json:"kategori"`
	URL             *string `json:"url"`
	PDFURL          *string `json:"pdf_url"`
	JenisPeraturan  *string `json:"jenis_peraturan"`
	Pemrakarsa      *string `json:"pemrakarsa"`
	Tentang         *string `json:"tentang"`
	TempatPenetapan *string `json:"tempat_penetapan"`
	StatusPeraturan *string `json:"status_peraturan"`
}
