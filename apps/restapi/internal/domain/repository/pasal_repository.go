package repository

import (
	"context"

	"github.com/hendrywilliam/norma/apps/restapi/internal/domain/model"
)

type PasalRepository interface {
	Create(ctx context.Context, pasal *model.Pasal) error
	GetByID(ctx context.Context, id int) (*model.Pasal, error)
	GetList(ctx context.Context, filter *model.PasalFilter) (*model.PasalListResponse, error)
	GetByPeraturanID(ctx context.Context, peraturanID string, skip, limit int) ([]model.Pasal, error)
	GetByBabID(ctx context.Context, babID int, skip, limit int) ([]model.Pasal, error)
	Update(ctx context.Context, id int, pasal *model.Pasal) error
	Delete(ctx context.Context, id int) error
	DeleteByPeraturanID(ctx context.Context, peraturanID string) error
}
