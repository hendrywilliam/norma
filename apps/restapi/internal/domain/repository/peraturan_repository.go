package repository

import (
	"context"

	"github.com/hendrywilliam/norma/apps/restapi/internal/domain/model"
)

type PeraturanRepository interface {
	Create(ctx context.Context, peraturan *model.Peraturan) error
	GetByID(ctx context.Context, id string) (*model.Peraturan, error)
	GetList(ctx context.Context, filter *model.PeraturanFilter) (*model.PeraturanListResponse, error)
	Update(ctx context.Context, id string, peraturan *model.Peraturan) error
	Delete(ctx context.Context, id string) error
	Search(ctx context.Context, query string, skip, limit int) (*model.PeraturanListResponse, error)
}
