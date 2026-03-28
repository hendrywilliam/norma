package repository

import (
	"context"

	"github.com/hendrywilliam/norma/apps/restapi/internal/domain/model"
)

type BabRepository interface {
	Create(ctx context.Context, bab *model.Bab) error
	GetByID(ctx context.Context, id int) (*model.Bab, error)
	GetList(ctx context.Context, filter *model.BabFilter) (*model.BabListResponse, error)
	GetByPeraturanID(ctx context.Context, peraturanID string, skip, limit int) ([]model.Bab, error)
	Update(ctx context.Context, id int, bab *model.Bab) error
	Delete(ctx context.Context, id int) error
	DeleteByPeraturanID(ctx context.Context, peraturanID string) error
}
