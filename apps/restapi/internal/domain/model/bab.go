package model

import "time"

type Bab struct {
	ID          int       `json:"id" db:"id"`
	PeraturanID string    `json:"peraturan_id" db:"peraturan_id"`
	NomorBab    string    `json:"nomor_bab" db:"nomor_bab"`
	JudulBab    string    `json:"judul_bab" db:"judul_bab"`
	Urutan      int       `json:"urutan" db:"urutan"`
	KontenBab   *string   `json:"konten_bab" db:"konten_bab"`
	CreatedAt   time.Time `json:"created_at" db:"created_at"`
}

type BabFilter struct {
	PeraturanID string
	Skip        int
	Limit       int
}

type BabListResponse struct {
	Total int   `json:"total"`
	Skip  int   `json:"skip"`
	Limit int   `json:"limit"`
	Items []Bab `json:"items"`
}

type CreateBabRequest struct {
	PeraturanID string `json:"peraturan_id" binding:"required"`
	NomorBab    string `json:"nomor_bab" binding:"required"`
	JudulBab    string `json:"judul_bab" binding:"required"`
	Urutan      int    `json:"urutan"`
	KontenBab   string `json:"konten_bab"`
}

type UpdateBabRequest struct {
	JudulBab  *string `json:"judul_bab"`
	KontenBab *string `json:"konten_bab"`
}
