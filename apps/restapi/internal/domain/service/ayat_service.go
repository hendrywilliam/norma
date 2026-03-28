package service

import (
	"context"

	"github.com/hendrywilliam/norma/apps/restapi/internal/domain/model"
	"github.com/hendrywilliam/norma/apps/restapi/internal/domain/repository"
)

type AyatService interface {
	Create(ctx context.Context, ayat *model.Ayat) error
	GetByID(ctx context.Context, id int) (*model.Ayat, error)
	GetList(ctx context.Context, filter *model.AyatFilter) (*model.AyatListResponse, error)
	GetByPasalID(ctx context.Context, pasalID int, skip, limit int) ([]model.Ayat, error)
	GetByPeraturanID(ctx context.Context, peraturanID string) ([]model.Ayat, error)
	Update(ctx context.Context, id int, ayat *model.Ayat) error
	Delete(ctx context.Context, id int) error
	DeleteByPasalID(ctx context.Context, pasalID int) error
}

type ayatService struct {
	repo repository.AyatRepository
}

func NewAyatService(repo repository.AyatRepository) AyatService {
	return &ayatService{repo: repo}
}

func (s *ayatService) Create(ctx context.Context, ayat *model.Ayat) error {
	return s.repo.Create(ctx, ayat)
}

func (s *ayatService) GetByID(ctx context.Context, id int) (*model.Ayat, error) {
	return s.repo.GetByID(ctx, id)
}

func (s *ayatService) GetList(ctx context.Context, filter *model.AyatFilter) (*model.AyatListResponse, error) {
	return s.repo.GetList(ctx, filter)
}

func (s *ayatService) GetByPasalID(ctx context.Context, pasalID int, skip, limit int) ([]model.Ayat, error) {
	return s.repo.GetByPasalID(ctx, pasalID, skip, limit)
}

func (s *ayatService) GetByPeraturanID(ctx context.Context, peraturanID string) ([]model.Ayat, error) {
	return s.repo.GetByPeraturanID(ctx, peraturanID)
}

func (s *ayatService) Update(ctx context.Context, id int, ayat *model.Ayat) error {
	return s.repo.Update(ctx, id, ayat)
}

func (s *ayatService) Delete(ctx context.Context, id int) error {
	return s.repo.Delete(ctx, id)
}

func (s *ayatService) DeleteByPasalID(ctx context.Context, pasalID int) error {
	return s.repo.DeleteByPasalID(ctx, pasalID)
}
