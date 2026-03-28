package service

import (
	"context"

	"github.com/hendrywilliam/norma/apps/restapi/internal/domain/model"
	"github.com/hendrywilliam/norma/apps/restapi/internal/domain/repository"
)

type PasalService interface {
	Create(ctx context.Context, pasal *model.Pasal) error
	GetByID(ctx context.Context, id int) (*model.Pasal, error)
	GetList(ctx context.Context, filter *model.PasalFilter) (*model.PasalListResponse, error)
	GetByPeraturanID(ctx context.Context, peraturanID string, skip, limit int) ([]model.Pasal, error)
	GetByBabID(ctx context.Context, babID int, skip, limit int) ([]model.Pasal, error)
	Update(ctx context.Context, id int, pasal *model.Pasal) error
	Delete(ctx context.Context, id int) error
	DeleteByPeraturanID(ctx context.Context, peraturanID string) error
}

type pasalService struct {
	repo repository.PasalRepository
}

func NewPasalService(repo repository.PasalRepository) PasalService {
	return &pasalService{repo: repo}
}

func (s *pasalService) Create(ctx context.Context, pasal *model.Pasal) error {
	return s.repo.Create(ctx, pasal)
}

func (s *pasalService) GetByID(ctx context.Context, id int) (*model.Pasal, error) {
	return s.repo.GetByID(ctx, id)
}

func (s *pasalService) GetList(ctx context.Context, filter *model.PasalFilter) (*model.PasalListResponse, error) {
	return s.repo.GetList(ctx, filter)
}

func (s *pasalService) GetByPeraturanID(ctx context.Context, peraturanID string, skip, limit int) ([]model.Pasal, error) {
	return s.repo.GetByPeraturanID(ctx, peraturanID, skip, limit)
}

func (s *pasalService) GetByBabID(ctx context.Context, babID int, skip, limit int) ([]model.Pasal, error) {
	return s.repo.GetByBabID(ctx, babID, skip, limit)
}

func (s *pasalService) Update(ctx context.Context, id int, pasal *model.Pasal) error {
	return s.repo.Update(ctx, id, pasal)
}

func (s *pasalService) Delete(ctx context.Context, id int) error {
	return s.repo.Delete(ctx, id)
}

func (s *pasalService) DeleteByPeraturanID(ctx context.Context, peraturanID string) error {
	return s.repo.DeleteByPeraturanID(ctx, peraturanID)
}
