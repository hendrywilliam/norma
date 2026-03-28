package postgres

import (
	"context"
	"fmt"

	"github.com/hendrywilliam/norma/apps/restapi/internal/domain/model"
	"github.com/hendrywilliam/norma/apps/restapi/internal/domain/repository"
	"github.com/jackc/pgx/v5"
	"github.com/jackc/pgx/v5/pgxpool"
)

type pasalRepository struct {
	db *pgxpool.Pool
}

func NewPasalRepository(db *pgxpool.Pool) repository.PasalRepository {
	return &pasalRepository{db: db}
}

func (r *pasalRepository) Create(ctx context.Context, pasal *model.Pasal) error {
	query := `
		INSERT INTO pasals (peraturan_id, bab_id, nomor_pasal, judul_pasal, konten_pasal, urutan, metadata)
		VALUES ($1, $2, $3, $4, $5, $6, $7)
		RETURNING id
	`
	err := r.db.QueryRow(ctx, query,
		pasal.PeraturanID, pasal.BabID, pasal.NomorPasal, pasal.JudulPasal,
		pasal.KontenPasal, pasal.Urutan, pasal.Metadata,
	).Scan(&pasal.ID)
	return err
}

func (r *pasalRepository) GetByID(ctx context.Context, id int) (*model.Pasal, error) {
	query := `
		SELECT id, peraturan_id, bab_id, nomor_pasal, judul_pasal, konten_pasal, urutan, metadata, created_at
		FROM pasals WHERE id = $1
	`
	var pasal model.Pasal
	err := r.db.QueryRow(ctx, query, id).Scan(
		&pasal.ID, &pasal.PeraturanID, &pasal.BabID, &pasal.NomorPasal,
		&pasal.JudulPasal, &pasal.KontenPasal, &pasal.Urutan, &pasal.Metadata, &pasal.CreatedAt,
	)
	if err != nil {
		if err == pgx.ErrNoRows {
			return nil, nil
		}
		return nil, err
	}
	return &pasal, nil
}

func (r *pasalRepository) GetList(ctx context.Context, filter *model.PasalFilter) (*model.PasalListResponse, error) {
	query := `
		SELECT id, peraturan_id, bab_id, nomor_pasal, judul_pasal, konten_pasal, urutan, metadata, created_at
		FROM pasals
		WHERE peraturan_id = $1
		ORDER BY urutan ASC
		LIMIT $2 OFFSET $3
	`
	rows, err := r.db.Query(ctx, query, filter.PeraturanID, filter.Limit, filter.Skip)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	var pasals []model.Pasal
	for rows.Next() {
		var p model.Pasal
		err := rows.Scan(
			&p.ID, &p.PeraturanID, &p.BabID, &p.NomorPasal,
			&p.JudulPasal, &p.KontenPasal, &p.Urutan, &p.Metadata, &p.CreatedAt,
		)
		if err != nil {
			return nil, err
		}
		pasals = append(pasals, p)
	}

	countQuery := "SELECT COUNT(*) FROM pasals WHERE peraturan_id = $1"
	var total int
	err = r.db.QueryRow(ctx, countQuery, filter.PeraturanID).Scan(&total)
	if err != nil {
		return nil, err
	}

	return &model.PasalListResponse{
		Total: total,
		Skip:  filter.Skip,
		Limit: filter.Limit,
		Items: pasals,
	}, nil
}

func (r *pasalRepository) GetByPeraturanID(ctx context.Context, peraturanID string, skip, limit int) ([]model.Pasal, error) {
	query := `
		SELECT id, peraturan_id, bab_id, nomor_pasal, judul_pasal, konten_pasal, urutan, metadata, created_at
		FROM pasals
		WHERE peraturan_id = $1
		ORDER BY urutan ASC
		LIMIT $2 OFFSET $3
	`
	rows, err := r.db.Query(ctx, query, peraturanID, limit, skip)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	var pasals []model.Pasal
	for rows.Next() {
		var p model.Pasal
		err := rows.Scan(
			&p.ID, &p.PeraturanID, &p.BabID, &p.NomorPasal,
			&p.JudulPasal, &p.KontenPasal, &p.Urutan, &p.Metadata, &p.CreatedAt,
		)
		if err != nil {
			return nil, err
		}
		pasals = append(pasals, p)
	}
	return pasals, nil
}

func (r *pasalRepository) GetByBabID(ctx context.Context, babID int, skip, limit int) ([]model.Pasal, error) {
	query := `
		SELECT id, peraturan_id, bab_id, nomor_pasal, judul_pasal, konten_pasal, urutan, metadata, created_at
		FROM pasals
		WHERE bab_id = $1
		ORDER BY urutan ASC
		LIMIT $2 OFFSET $3
	`
	rows, err := r.db.Query(ctx, query, babID, limit, skip)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	var pasals []model.Pasal
	for rows.Next() {
		var p model.Pasal
		err := rows.Scan(
			&p.ID, &p.PeraturanID, &p.BabID, &p.NomorPasal,
			&p.JudulPasal, &p.KontenPasal, &p.Urutan, &p.Metadata, &p.CreatedAt,
		)
		if err != nil {
			return nil, err
		}
		pasals = append(pasals, p)
	}
	return pasals, nil
}

func (r *pasalRepository) Update(ctx context.Context, id int, pasal *model.Pasal) error {
	query := `
		UPDATE pasals SET
			judul_pasal = COALESCE($2, judul_pasal),
			konten_pasal = COALESCE($3, konten_pasal),
			bab_id = COALESCE($4, bab_id)
		WHERE id = $1
	`
	result, err := r.db.Exec(ctx, query, id, pasal.JudulPasal, pasal.KontenPasal, pasal.BabID)
	if err != nil {
		return err
	}
	if result.RowsAffected() == 0 {
		return fmt.Errorf("pasal not found")
	}
	return nil
}

func (r *pasalRepository) Delete(ctx context.Context, id int) error {
	query := "DELETE FROM pasals WHERE id = $1"
	result, err := r.db.Exec(ctx, query, id)
	if err != nil {
		return err
	}
	if result.RowsAffected() == 0 {
		return fmt.Errorf("pasal not found")
	}
	return nil
}

func (r *pasalRepository) DeleteByPeraturanID(ctx context.Context, peraturanID string) error {
	query := "DELETE FROM pasals WHERE peraturan_id = $1"
	_, err := r.db.Exec(ctx, query, peraturanID)
	return err
}
