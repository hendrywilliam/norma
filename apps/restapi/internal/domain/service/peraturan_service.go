package service

import (
	"context"

	"github.com/hendrywilliam/norma/apps/restapi/internal/domain/model"
	"github.com/hendrywilliam/norma/apps/restapi/internal/domain/repository"
)

type PeraturanService interface {
	Create(ctx context.Context, peraturan *model.Peraturan) error
	GetByID(ctx context.Context, id string) (*model.Peraturan, error)
	GetList(ctx context.Context, filter *model.PeraturanFilter) (*model.PeraturanListResponse, error)
	Update(ctx context.Context, id string, peraturan *model.Peraturan) error
	Delete(ctx context.Context, id string) error
	Search(ctx context.Context, query string, skip, limit int) (*model.PeraturanListResponse, error)
}

type peraturanService struct {
	repo repository.PeraturanRepository
}

func NewPeraturanService(repo repository.PeraturanRepository) PeraturanService {
	return &peraturanService{repo: repo}
}

func (s *peraturanService) Create(ctx context.Context, peraturan *model.Peraturan) error {
	return s.repo.Create(ctx, peraturan)
}

func (s *peraturanService) GetByID(ctx context.Context, id string) (*model.Peraturan, error) {
	return s.repo.GetByID(ctx, id)
}

func (s *peraturanService) GetList(ctx context.Context, filter *model.PeraturanFilter) (*model.PeraturanListResponse, error) {
	return s.repo.GetList(ctx, filter)
}

func (s *peraturanService) Update(ctx context.Context, id string, peraturan *model.Peraturan) error {
	return s.repo.Update(ctx, id, peraturan)
}

func (s *peraturanService) Delete(ctx context.Context, id string) error {
	return s.repo.Delete(ctx, id)
}

func (s *peraturanService) Search(ctx context.Context, query string, skip, limit int) (*model.PeraturanListResponse, error) {
	return s.repo.Search(ctx, query, skip, limit)
}
