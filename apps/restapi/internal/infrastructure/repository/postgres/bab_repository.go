package postgres

import (
	"context"
	"fmt"

	"github.com/hendrywilliam/norma/apps/restapi/internal/domain/model"
	"github.com/hendrywilliam/norma/apps/restapi/internal/domain/repository"
	"github.com/jackc/pgx/v5"
	"github.com/jackc/pgx/v5/pgxpool"
)

type babRepository struct {
	db *pgxpool.Pool
}

func NewBabRepository(db *pgxpool.Pool) repository.BabRepository {
	return &babRepository{db: db}
}

func (r *babRepository) Create(ctx context.Context, bab *model.Bab) error {
	query := `
		INSERT INTO bab (peraturan_id, nomor_bab, judul_bab, urutan, konten_bab)
		VALUES ($1, $2, $3, $4, $5)
		RETURNING id
	`
	err := r.db.QueryRow(ctx, query,
		bab.PeraturanID, bab.NomorBab, bab.JudulBab, bab.Urutan, bab.KontenBab,
	).Scan(&bab.ID)
	return err
}

func (r *babRepository) GetByID(ctx context.Context, id int) (*model.Bab, error) {
	query := `
		SELECT id, peraturan_id, nomor_bab, judul_bab, urutan, konten_bab, created_at
		FROM bab WHERE id = $1
	`
	var bab model.Bab
	err := r.db.QueryRow(ctx, query, id).Scan(
		&bab.ID, &bab.PeraturanID, &bab.NomorBab, &bab.JudulBab,
		&bab.Urutan, &bab.KontenBab, &bab.CreatedAt,
	)
	if err != nil {
		if err == pgx.ErrNoRows {
			return nil, nil
		}
		return nil, err
	}
	return &bab, nil
}

func (r *babRepository) GetList(ctx context.Context, filter *model.BabFilter) (*model.BabListResponse, error) {
	query := `
		SELECT id, peraturan_id, nomor_bab, judul_bab, urutan, konten_bab, created_at
		FROM bab
		WHERE peraturan_id = $1
		ORDER BY urutan ASC
		LIMIT $2 OFFSET $3
	`
	rows, err := r.db.Query(ctx, query, filter.PeraturanID, filter.Limit, filter.Skip)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	var babs []model.Bab
	for rows.Next() {
		var b model.Bab
		err := rows.Scan(
			&b.ID, &b.PeraturanID, &b.NomorBab, &b.JudulBab,
			&b.Urutan, &b.KontenBab, &b.CreatedAt,
		)
		if err != nil {
			return nil, err
		}
		babs = append(babs, b)
	}

	countQuery := "SELECT COUNT(*) FROM bab WHERE peraturan_id = $1"
	var total int
	err = r.db.QueryRow(ctx, countQuery, filter.PeraturanID).Scan(&total)
	if err != nil {
		return nil, err
	}

	return &model.BabListResponse{
		Total: total,
		Skip:  filter.Skip,
		Limit: filter.Limit,
		Items: babs,
	}, nil
}

func (r *babRepository) GetByPeraturanID(ctx context.Context, peraturanID string, skip, limit int) ([]model.Bab, error) {
	query := `
		SELECT id, peraturan_id, nomor_bab, judul_bab, urutan, konten_bab, created_at
		FROM bab
		WHERE peraturan_id = $1
		ORDER BY urutan ASC
		LIMIT $2 OFFSET $3
	`
	rows, err := r.db.Query(ctx, query, peraturanID, limit, skip)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	var babs []model.Bab
	for rows.Next() {
		var b model.Bab
		err := rows.Scan(
			&b.ID, &b.PeraturanID, &b.NomorBab, &b.JudulBab,
			&b.Urutan, &b.KontenBab, &b.CreatedAt,
		)
		if err != nil {
			return nil, err
		}
		babs = append(babs, b)
	}
	return babs, nil
}

func (r *babRepository) Update(ctx context.Context, id int, bab *model.Bab) error {
	query := `
		UPDATE bab SET
			judul_bab = COALESCE($2, judul_bab),
			konten_bab = COALESCE($3, konten_bab)
		WHERE id = $1
	`
	result, err := r.db.Exec(ctx, query, id, bab.JudulBab, bab.KontenBab)
	if err != nil {
		return err
	}
	if result.RowsAffected() == 0 {
		return fmt.Errorf("bab not found")
	}
	return nil
}

func (r *babRepository) Delete(ctx context.Context, id int) error {
	query := "DELETE FROM bab WHERE id = $1"
	result, err := r.db.Exec(ctx, query, id)
	if err != nil {
		return err
	}
	if result.RowsAffected() == 0 {
		return fmt.Errorf("bab not found")
	}
	return nil
}

func (r *babRepository) DeleteByPeraturanID(ctx context.Context, peraturanID string) error {
	query := "DELETE FROM bab WHERE peraturan_id = $1"
	_, err := r.db.Exec(ctx, query, peraturanID)
	return err
}
