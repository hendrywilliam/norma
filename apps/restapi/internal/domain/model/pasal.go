package model

import "time"

type Pasal struct {
	ID          int       `json:"id" db:"id"`
	PeraturanID string    `json:"peraturan_id" db:"peraturan_id"`
	BabID       *int      `json:"bab_id" db:"bab_id"`
	NomorPasal  string    `json:"nomor_pasal" db:"nomor_pasal"`
	JudulPasal  *string   `json:"judul_pasal" db:"judul_pasal"`
	KontenPasal *string   `json:"konten_pasal" db:"konten_pasal"`
	Urutan      int       `json:"urutan" db:"urutan"`
	Metadata    *string   `json:"metadata" db:"metadata"`
	CreatedAt   time.Time `json:"created_at" db:"created_at"`
}

type PasalFilter struct {
	PeraturanID string
	BabID       *int
	Skip        int
	Limit       int
}

type PasalListResponse struct {
	Total int     `json:"total"`
	Skip  int     `json:"skip"`
	Limit int     `json:"limit"`
	Items []Pasal `json:"items"`
}

type CreatePasalRequest struct {
	PeraturanID string  `json:"peraturan_id" binding:"required"`
	BabID       *int    `json:"bab_id"`
	NomorPasal  string  `json:"nomor_pasal" binding:"required"`
	JudulPasal  *string `json:"judul_pasal"`
	KontenPasal *string `json:"konten_pasal"`
	Urutan      int     `json:"urutan"`
}

type UpdatePasalRequest struct {
	JudulPasal  *string `json:"judul_pasal"`
	KontenPasal *string `json:"konten_pasal"`
	BabID       *int    `json:"bab_id"`
}
