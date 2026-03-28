package model

import "time"

type Ayat struct {
	ID         int       `json:"id" db:"id"`
	PasalID    int       `json:"pasal_id" db:"pasal_id"`
	NomorAyat  string    `json:"nomor_ayat" db:"nomor_ayat"`
	KontenAyat string    `json:"konten_ayat" db:"konten_ayat"`
	Urutan     int       `json:"urutan" db:"urutan"`
	Metadata   *string   `json:"metadata" db:"metadata"`
	CreatedAt  time.Time `json:"created_at" db:"created_at"`
}

type AyatFilter struct {
	PasalID int
	Skip    int
	Limit   int
}

type AyatListResponse struct {
	Total int    `json:"total"`
	Skip  int    `json:"skip"`
	Limit int    `json:"limit"`
	Items []Ayat `json:"items"`
}

type CreateAyatRequest struct {
	PasalID    int    `json:"pasal_id" binding:"required"`
	NomorAyat  string `json:"nomor_ayat" binding:"required"`
	KontenAyat string `json:"konten_ayat" binding:"required"`
	Urutan     int    `json:"urutan"`
}

type UpdateAyatRequest struct {
	KontenAyat *string `json:"konten_ayat"`
}
