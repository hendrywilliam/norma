package repository

import (
	"context"

	"github.com/hendrywilliam/norma/apps/restapi/internal/domain/model"
)

type AyatRepository interface {
	Create(ctx context.Context, ayat *model.Ayat) error
	GetByID(ctx context.Context, id int) (*model.Ayat, error)
	GetList(ctx context.Context, filter *model.AyatFilter) (*model.AyatListResponse, error)
	GetByPasalID(ctx context.Context, pasalID int, skip, limit int) ([]model.Ayat, error)
	GetByPeraturanID(ctx context.Context, peraturanID string) ([]model.Ayat, error)
	Update(ctx context.Context, id int, ayat *model.Ayat) error
	Delete(ctx context.Context, id int) error
	DeleteByPasalID(ctx context.Context, pasalID int) error
}
