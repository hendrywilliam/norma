package service

import (
	"context"

	"github.com/hendrywilliam/norma/apps/restapi/internal/domain/model"
	"github.com/hendrywilliam/norma/apps/restapi/internal/domain/repository"
)

type BabService interface {
	Create(ctx context.Context, bab *model.Bab) error
	GetByID(ctx context.Context, id int) (*model.Bab, error)
	GetList(ctx context.Context, filter *model.BabFilter) (*model.BabListResponse, error)
	GetByPeraturanID(ctx context.Context, peraturanID string, skip, limit int) ([]model.Bab, error)
	Update(ctx context.Context, id int, bab *model.Bab) error
	Delete(ctx context.Context, id int) error
	DeleteByPeraturanID(ctx context.Context, peraturanID string) error
}

type babService struct {
	repo repository.BabRepository
}

func NewBabService(repo repository.BabRepository) BabService {
	return &babService{repo: repo}
}

func (s *babService) Create(ctx context.Context, bab *model.Bab) error {
	return s.repo.Create(ctx, bab)
}

func (s *babService) GetByID(ctx context.Context, id int) (*model.Bab, error) {
	return s.repo.GetByID(ctx, id)
}

func (s *babService) GetList(ctx context.Context, filter *model.BabFilter) (*model.BabListResponse, error) {
	return s.repo.GetList(ctx, filter)
}

func (s *babService) GetByPeraturanID(ctx context.Context, peraturanID string, skip, limit int) ([]model.Bab, error) {
	return s.repo.GetByPeraturanID(ctx, peraturanID, skip, limit)
}

func (s *babService) Update(ctx context.Context, id int, bab *model.Bab) error {
	return s.repo.Update(ctx, id, bab)
}

func (s *babService) Delete(ctx context.Context, id int) error {
	return s.repo.Delete(ctx, id)
}

func (s *babService) DeleteByPeraturanID(ctx context.Context, peraturanID string) error {
	return s.repo.DeleteByPeraturanID(ctx, peraturanID)
}
