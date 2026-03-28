package container

import (
	"github.com/samber/do/v2"

	"github.com/hendrywilliam/norma/apps/restapi/internal/config"
	"github.com/hendrywilliam/norma/apps/restapi/internal/domain/repository"
	"github.com/hendrywilliam/norma/apps/restapi/internal/domain/service"
	"github.com/hendrywilliam/norma/apps/restapi/internal/handler"
	postgresrepo "github.com/hendrywilliam/norma/apps/restapi/internal/infrastructure/repository/postgres"
	"github.com/hendrywilliam/norma/apps/restapi/pkg/database"
)

// Build creates and configures all dependencies
func Build() *do.RootScope {
	scope := do.New()

	// Config
	do.ProvideValue(scope, config.Load())

	// Database
	do.Provide(scope, NewDB)

	// Repositories
	do.Provide(scope, NewPeraturanRepository)
	do.Provide(scope, NewBabRepository)
	do.Provide(scope, NewPasalRepository)
	do.Provide(scope, NewAyatRepository)

	// Services
	do.Provide(scope, NewPeraturanService)
	do.Provide(scope, NewBabService)
	do.Provide(scope, NewPasalService)
	do.Provide(scope, NewAyatService)

	// Handlers
	do.Provide(scope, NewPeraturanHandler)
	do.Provide(scope, NewBabHandler)
	do.Provide(scope, NewPasalHandler)
	do.Provide(scope, NewAyatHandler)

	return scope
}

// Database
func NewDB(i do.Injector) (database.DB, error) {
	cfg := do.MustInvoke[*config.Config](i)
	return database.NewConnection(database.DBConfig{
		Host:     cfg.Database.Host,
		Port:     cfg.Database.Port,
		User:     cfg.Database.User,
		Password: cfg.Database.Password,
		Name:     cfg.Database.Name,
		SSLMode:  cfg.Database.SSLMode,
	})
}

// Repositories
func NewPeraturanRepository(i do.Injector) (repository.PeraturanRepository, error) {
	db := do.MustInvoke[database.DB](i)
	return postgresrepo.NewPeraturanRepository(db), nil
}

func NewBabRepository(i do.Injector) (repository.BabRepository, error) {
	db := do.MustInvoke[database.DB](i)
	return postgresrepo.NewBabRepository(db), nil
}

func NewPasalRepository(i do.Injector) (repository.PasalRepository, error) {
	db := do.MustInvoke[database.DB](i)
	return postgresrepo.NewPasalRepository(db), nil
}

func NewAyatRepository(i do.Injector) (repository.AyatRepository, error) {
	db := do.MustInvoke[database.DB](i)
	return postgresrepo.NewAyatRepository(db), nil
}

// Services
func NewPeraturanService(i do.Injector) (service.PeraturanService, error) {
	repo := do.MustInvoke[repository.PeraturanRepository](i)
	return service.NewPeraturanService(repo), nil
}

func NewBabService(i do.Injector) (service.BabService, error) {
	repo := do.MustInvoke[repository.BabRepository](i)
	return service.NewBabService(repo), nil
}

func NewPasalService(i do.Injector) (service.PasalService, error) {
	repo := do.MustInvoke[repository.PasalRepository](i)
	return service.NewPasalService(repo), nil
}

func NewAyatService(i do.Injector) (service.AyatService, error) {
	repo := do.MustInvoke[repository.AyatRepository](i)
	return service.NewAyatService(repo), nil
}

// Handlers
func NewPeraturanHandler(i do.Injector) (*handler.PeraturanHandler, error) {
	svc := do.MustInvoke[service.PeraturanService](i)
	return handler.NewPeraturanHandler(svc), nil
}

func NewBabHandler(i do.Injector) (*handler.BabHandler, error) {
	svc := do.MustInvoke[service.BabService](i)
	return handler.NewBabHandler(svc), nil
}

func NewPasalHandler(i do.Injector) (*handler.PasalHandler, error) {
	svc := do.MustInvoke[service.PasalService](i)
	return handler.NewPasalHandler(svc), nil
}

func NewAyatHandler(i do.Injector) (*handler.AyatHandler, error) {
	svc := do.MustInvoke[service.AyatService](i)
	return handler.NewAyatHandler(svc), nil
}
