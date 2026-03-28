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

// DI Container keys
const (
	ConfigKey           = "config"
	DBKey               = "db"
	PeraturanRepoKey    = "peraturan-repo"
	PeraturanServiceKey = "peraturan-service"
	PeraturanHandlerKey = "peraturan-handler"
)

func NewContainer() *do.RootScope {
	scope := do.NewRootScope()

	// Register providers
	do.Provide(scope, provideConfig)
	do.Provide(scope, provideDB)
	do.Provide(scope, providePeraturanRepository)
	do.Provide(scope, providePeraturanService)
	do.Provide(scope, providePeraturanHandler)

	return scope
}

func provideConfig(scope *do.RootScope) (*config.Config, error) {
	return do.NamedSingleton(scope, ConfigKey, func() (*config.Config, error) {
		return config.Load(), nil
	})
}

func provideDB(scope *do.RootScope, cfg *config.Config) (database.DB, error) {
	return do.NamedSingleton(scope, DBKey, func() (database.DB, error) {
		return database.NewConnection(database.DBConfig{
			Host:     cfg.Database.Host,
			Port:     cfg.Database.Port,
			User:     cfg.Database.User,
			Password: cfg.Database.Password,
			Name:     cfg.Database.Name,
			SSLMode:  cfg.Database.SSLMode,
		})
	})
}

func providePeraturanRepository(scope *do.RootScope, db database.DB) (repository.PeraturanRepository, error) {
	return do.NamedSingleton(scope, PeraturanRepoKey, func() (repository.PeraturanRepository, error) {
		return postgresrepo.NewPeraturanRepository(db), nil
	})
}

func providePeraturanService(scope *do.RootScope, repo repository.PeraturanRepository) (service.PeraturanService, error) {
	return do.NamedSingleton(scope, PeraturanServiceKey, func() (service.PeraturanService, error) {
		return service.NewPeraturanService(repo), nil
	})
}

func providePeraturanHandler(scope *do.RootScope, svc service.PeraturanService) (*handler.PeraturanHandler, error) {
	return do.NamedSingleton(scope, PeraturanHandlerKey, func() (*handler.PeraturanHandler, error) {
		return handler.NewPeraturanHandler(svc), nil
	})
}

// Getters for retrieving dependencies
func GetConfig(scope *do.RootScope) *config.Config {
	return do.MustInvoke[*config.Config](scope, provideConfig)
}

func GetDB(scope *do.RootScope) database.DB {
	return do.MustInvoke[database.DB](scope, provideDB)
}

func GetPeraturanRepository(scope *do.RootScope) repository.PeraturanRepository {
	return do.MustInvoke[repository.PeraturanRepository](scope, providePeraturanRepository)
}

func GetPeraturanService(scope *do.RootScope) service.PeraturanService {
	return do.MustInvoke[service.PeraturanService](scope, providePeraturanService)
}

func GetPeraturanHandler(scope *do.RootScope) *handler.PeraturanHandler {
	return do.MustInvoke[*handler.PeraturanHandler](scope, providePeraturanHandler)
}
