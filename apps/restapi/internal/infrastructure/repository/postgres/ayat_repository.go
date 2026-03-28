package postgres

import (
	"context"
	"fmt"

	"github.com/hendrywilliam/norma/apps/restapi/internal/domain/model"
	"github.com/hendrywilliam/norma/apps/restapi/internal/domain/repository"
	"github.com/jackc/pgx/v5"
	"github.com/jackc/pgx/v5/pgxpool"
)

type ayatRepository struct {
	db *pgxpool.Pool
}

func NewAyatRepository(db *pgxpool.Pool) repository.AyatRepository {
	return &ayatRepository{db: db}
}

func (r *ayatRepository) Create(ctx context.Context, ayat *model.Ayat) error {
	query := `
		INSERT INTO ayats (pasal_id, nomor_ayat, konten_ayat, urutan, metadata)
		VALUES ($1, $2, $3, $4, $5)
		RETURNING id
	`
	err := r.db.QueryRow(ctx, query,
		ayat.PasalID, ayat.NomorAyat, ayat.KontenAyat, ayat.Urutan, ayat.Metadata,
	).Scan(&ayat.ID)
	return err
}

func (r *ayatRepository) GetByID(ctx context.Context, id int) (*model.Ayat, error) {
	query := `
		SELECT id, pasal_id, nomor_ayat, konten_ayat, urutan, metadata, created_at
		FROM ayats WHERE id = $1
	`
	var ayat model.Ayat
	err := r.db.QueryRow(ctx, query, id).Scan(
		&ayat.ID, &ayat.PasalID, &ayat.NomorAyat, &ayat.KontenAyat,
		&ayat.Urutan, &ayat.Metadata, &ayat.CreatedAt,
	)
	if err != nil {
		if err == pgx.ErrNoRows {
			return nil, nil
		}
		return nil, err
	}
	return &ayat, nil
}

func (r *ayatRepository) GetList(ctx context.Context, filter *model.AyatFilter) (*model.AyatListResponse, error) {
	query := `
		SELECT id, pasal_id, nomor_ayat, konten_ayat, urutan, metadata, created_at
		FROM ayats
		WHERE pasal_id = $1
		ORDER BY urutan ASC
		LIMIT $2 OFFSET $3
	`
	rows, err := r.db.Query(ctx, query, filter.PasalID, filter.Limit, filter.Skip)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	var ayats []model.Ayat
	for rows.Next() {
		var a model.Ayat
		err := rows.Scan(
			&a.ID, &a.PasalID, &a.NomorAyat, &a.KontenAyat,
			&a.Urutan, &a.Metadata, &a.CreatedAt,
		)
		if err != nil {
			return nil, err
		}
		ayats = append(ayats, a)
	}

	countQuery := "SELECT COUNT(*) FROM ayats WHERE pasal_id = $1"
	var total int
	err = r.db.QueryRow(ctx, countQuery, filter.PasalID).Scan(&total)
	if err != nil {
		return nil, err
	}

	return &model.AyatListResponse{
		Total: total,
		Skip:  filter.Skip,
		Limit: filter.Limit,
		Items: ayats,
	}, nil
}

func (r *ayatRepository) GetByPasalID(ctx context.Context, pasalID int, skip, limit int) ([]model.Ayat, error) {
	query := `
		SELECT id, pasal_id, nomor_ayat, konten_ayat, urutan, metadata, created_at
		FROM ayats
		WHERE pasal_id = $1
		ORDER BY urutan ASC
		LIMIT $2 OFFSET $3
	`
	rows, err := r.db.Query(ctx, query, pasalID, limit, skip)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	var ayats []model.Ayat
	for rows.Next() {
		var a model.Ayat
		err := rows.Scan(
			&a.ID, &a.PasalID, &a.NomorAyat, &a.KontenAyat,
			&a.Urutan, &a.Metadata, &a.CreatedAt,
		)
		if err != nil {
			return nil, err
		}
		ayats = append(ayats, a)
	}
	return ayats, nil
}

func (r *ayatRepository) GetByPeraturanID(ctx context.Context, peraturanID string) ([]model.Ayat, error) {
	query := `
		SELECT a.id, a.pasal_id, a.nomor_ayat, a.konten_ayat, a.urutan, a.metadata, a.created_at
		FROM ayats a
		JOIN pasals p ON a.pasal_id = p.id
		WHERE p.peraturan_id = $1
		ORDER BY a.urutan ASC
	`
	rows, err := r.db.Query(ctx, query, peraturanID)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	var ayats []model.Ayat
	for rows.Next() {
		var a model.Ayat
		err := rows.Scan(
			&a.ID, &a.PasalID, &a.NomorAyat, &a.KontenAyat,
			&a.Urutan, &a.Metadata, &a.CreatedAt,
		)
		if err != nil {
			return nil, err
		}
		ayats = append(ayats, a)
	}
	return ayats, nil
}

func (r *ayatRepository) Update(ctx context.Context, id int, ayat *model.Ayat) error {
	query := `
		UPDATE ayats SET
			konten_ayat = COALESCE($2, konten_ayat)
		WHERE id = $1
	`
	result, err := r.db.Exec(ctx, query, id, ayat.KontenAyat)
	if err != nil {
		return err
	}
	if result.RowsAffected() == 0 {
		return fmt.Errorf("ayat not found")
	}
	return nil
}

func (r *ayatRepository) Delete(ctx context.Context, id int) error {
	query := "DELETE FROM ayats WHERE id = $1"
	result, err := r.db.Exec(ctx, query, id)
	if err != nil {
		return err
	}
	if result.RowsAffected() == 0 {
		return fmt.Errorf("ayat not found")
	}
	return nil
}

func (r *ayatRepository) DeleteByPasalID(ctx context.Context, pasalID int) error {
	query := "DELETE FROM ayats WHERE pasal_id = $1"
	_, err := r.db.Exec(ctx, query, pasalID)
	return err
}
