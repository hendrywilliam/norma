package postgres

import (
	"context"
	"fmt"

	"github.com/hendrywilliam/norma/apps/restapi/internal/domain/model"
	"github.com/hendrywilliam/norma/apps/restapi/internal/domain/repository"
	"github.com/jackc/pgx/v5"
	"github.com/jackc/pgx/v5/pgxpool"
)

type peraturanRepository struct {
	db *pgxpool.Pool
}

func NewPeraturanRepository(db *pgxpool.Pool) repository.PeraturanRepository {
	return &peraturanRepository{db: db}
}

func (r *peraturanRepository) Create(ctx context.Context, peraturan *model.Peraturan) error {
	query := `
		INSERT INTO peraturan (
			id, judul, nomor, tahun, kategori, url, pdf_url,
			jenis_peraturan, pemrakarsa, tentang, tempat_penetapan,
			tanggal_ditetapkan, pejabat_menetapkan, status_peraturan,
			jumlah_dilihat, jumlah_download, tanggal_diundangkan,
			tanggal_disahkan, deskripsi, metadata
		) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16, $17, $18, $19, $20)
		ON CONFLICT (id) DO UPDATE SET
			judul = EXCLUDED.judul,
			nomor = EXCLUDED.nomor,
			tahun = EXCLUDED.tahun,
			kategori = EXCLUDED.kategori,
			url = EXCLUDED.url,
			pdf_url = EXCLUDED.pdf_url,
			updated_at = CURRENT_TIMESTAMP
	`

	_, err := r.db.Exec(ctx, query,
		peraturan.ID, peraturan.Judul, peraturan.Nomor, peraturan.Tahun,
		peraturan.Kategori, peraturan.URL, peraturan.PDFURL,
		peraturan.JenisPeraturan, peraturan.Pemrakarsa, peraturan.Tentang,
		peraturan.TempatPenetapan, peraturan.TanggalDitetapkan,
		peraturan.PejabatMenetapkan, peraturan.StatusPeraturan,
		peraturan.JumlahDilihat, peraturan.JumlahDownload,
		peraturan.TanggalDiundangkan, peraturan.TanggalDisahkan,
		peraturan.Deskripsi, peraturan.Metadata,
	)

	return err
}

func (r *peraturanRepository) GetByID(ctx context.Context, id string) (*model.Peraturan, error) {
	query := `
		SELECT id, judul, nomor, tahun, kategori, url, pdf_url,
			   jenis_peraturan, pemrakarsa, tentang, tempat_penetapan,
			   tanggal_ditetapkan, pejabat_menetapkan, status_peraturan,
			   jumlah_dilihat, jumlah_download, tanggal_diundangkan,
			   tanggal_disahkan, deskripsi, metadata,
			   created_at, updated_at, parsed_at, reparse_count, last_reparse_at
		FROM peraturan WHERE id = $1
	`

	var peraturan model.Peraturan
	err := r.db.QueryRow(ctx, query, id).Scan(
		&peraturan.ID, &peraturan.Judul, &peraturan.Nomor, &peraturan.Tahun,
		&peraturan.Kategori, &peraturan.URL, &peraturan.PDFURL,
		&peraturan.JenisPeraturan, &peraturan.Pemrakarsa, &peraturan.Tentang,
		&peraturan.TempatPenetapan, &peraturan.TanggalDitetapkan,
		&peraturan.PejabatMenetapkan, &peraturan.StatusPeraturan,
		&peraturan.JumlahDilihat, &peraturan.JumlahDownload,
		&peraturan.TanggalDiundangkan, &peraturan.TanggalDisahkan,
		&peraturan.Deskripsi, &peraturan.Metadata,
		&peraturan.CreatedAt, &peraturan.UpdatedAt, &peraturan.ParsedAt,
		&peraturan.ReparseCount, &peraturan.LastReparseAt,
	)

	if err != nil {
		if err == pgx.ErrNoRows {
			return nil, nil
		}
		return nil, err
	}

	return &peraturan, nil
}

func (r *peraturanRepository) GetList(ctx context.Context, filter *model.PeraturanFilter) (*model.PeraturanListResponse, error) {
	query := `
		SELECT id, judul, nomor, tahun, kategori, url, pdf_url,
			   jenis_peraturan, pemrakarsa, tentang, status_peraturan,
			   created_at, updated_at, parsed_at
		FROM peraturan
		ORDER BY created_at DESC
		LIMIT $1 OFFSET $2
	`

	rows, err := r.db.Query(ctx, query, filter.Limit, filter.Skip)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	var peraturans []model.Peraturan
	for rows.Next() {
		var p model.Peraturan
		err := rows.Scan(
			&p.ID, &p.Judul, &p.Nomor, &p.Tahun,
			&p.Kategori, &p.URL, &p.PDFURL,
			&p.JenisPeraturan, &p.Pemrakarsa, &p.Tentang,
			&p.StatusPeraturan,
			&p.CreatedAt, &p.UpdatedAt, &p.ParsedAt,
		)
		if err != nil {
			return nil, err
		}
		peraturans = append(peraturans, p)
	}

	countQuery := "SELECT COUNT(*) FROM peraturan"
	var total int
	err = r.db.QueryRow(ctx, countQuery).Scan(&total)
	if err != nil {
		return nil, err
	}

	return &model.PeraturanListResponse{
		Total: total,
		Skip:  filter.Skip,
		Limit: filter.Limit,
		Items: peraturans,
	}, nil
}

func (r *peraturanRepository) Update(ctx context.Context, id string, peraturan *model.Peraturan) error {
	query := `
		UPDATE peraturan SET
			judul = COALESCE($2, judul),
			nomor = COALESCE($3, nomor),
			tahun = COALESCE($4, tahun),
			updated_at = CURRENT_TIMESTAMP
		WHERE id = $1
	`

	result, err := r.db.Exec(ctx, query, id, peraturan.Judul, peraturan.Nomor, peraturan.Tahun)
	if err != nil {
		return err
	}

	if result.RowsAffected() == 0 {
		return fmt.Errorf("peraturan not found")
	}

	return nil
}

func (r *peraturanRepository) Delete(ctx context.Context, id string) error {
	query := "DELETE FROM peraturan WHERE id = $1"
	result, err := r.db.Exec(ctx, query, id)
	if err != nil {
		return err
	}

	if result.RowsAffected() == 0 {
		return fmt.Errorf("peraturan not found")
	}

	return nil
}

func (r *peraturanRepository) Search(ctx context.Context, query string, skip, limit int) (*model.PeraturanListResponse, error) {
	searchQuery := `
		SELECT id, judul, nomor, tahun, kategori, url, pdf_url,
			   jenis_peraturan, pemrakarsa, tentang, status_peraturan,
			   created_at, updated_at, parsed_at
		FROM peraturan
		WHERE to_tsvector('indonesian', coalesce(judul, '') || ' ' || coalesce(nomor, '') || ' ' || coalesce(tentang, ''))
			  @@ plainto_tsquery('indonesian', $1)
		ORDER BY created_at DESC
		LIMIT $2 OFFSET $3
	`

	rows, err := r.db.Query(ctx, searchQuery, query, limit, skip)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	var peraturans []model.Peraturan
	for rows.Next() {
		var p model.Peraturan
		err := rows.Scan(
			&p.ID, &p.Judul, &p.Nomor, &p.Tahun,
			&p.Kategori, &p.URL, &p.PDFURL,
			&p.JenisPeraturan, &p.Pemrakarsa, &p.Tentang,
			&p.StatusPeraturan,
			&p.CreatedAt, &p.UpdatedAt, &p.ParsedAt,
		)
		if err != nil {
			return nil, err
		}
		peraturans = append(peraturans, p)
	}

	return &model.PeraturanListResponse{
		Total: len(peraturans),
		Skip:  skip,
		Limit: limit,
		Items: peraturans,
	}, nil
}
