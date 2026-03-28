# REST API - Peraturan

REST API untuk mengelola data peraturan dengan arsitektur Clean Architecture menggunakan Go dan DI Container (samber/do).

## Architecture

```
apps/restapi/
├── cmd/main.go                              # Entry point
├── internal/
│   ├── config/config.go                    # Configuration loader (godotenv)
│   ├── container/container.go              # DI Container (samber/do v2)
│   ├── domain/
│   │   ├── model/
│   │   │   ├── peraturan.go               # Peraturan model
│   │   │   ├── bab.go                     # Bab model
│   │   │   ├── pasal.go                   # Pasal model
│   │   │   └── ayat.go                    # Ayat model
│   │   ├── repository/
│   │   │   ├── peraturan_repository.go    # Repository interface
│   │   │   ├── bab_repository.go          # Repository interface
│   │   │   ├── pasal_repository.go        # Repository interface
│   │   │   └── ayat_repository.go         # Repository interface
│   │   └── service/
│   │       ├── peraturan_service.go       # Business logic
│   │       ├── bab_service.go             # Business logic
│   │       ├── pasal_service.go           # Business logic
│   │       └── ayat_service.go            # Business logic
│   ├── handler/
│   │   ├── peraturan_handler.go           # HTTP handlers
│   │   ├── bab_handler.go                 # HTTP handlers
│   │   ├── pasal_handler.go               # HTTP handlers
│   │   └── ayat_handler.go                # HTTP handlers
│   └── infrastructure/repository/postgres/
│       ├── peraturan_repository.go        # Repository implementation
│       ├── bab_repository.go              # Repository implementation
│       ├── pasal_repository.go            # Repository implementation
│       └── ayat_repository.go             # Repository implementation
├── pkg/
│   ├── database/database.go               # Database connection (pgxpool)
│   └── response/response.go               # HTTP response helpers
├── .env.example                           # Environment variables template
├── go.mod
└── README.md
```

## Layers

### 1. **Domain Layer** (internal/domain/)
- **Model** - Enterprise business rules, entities
- **Repository** - Repository interfaces (contracts)
- **Service** - Business logic layer

### 2. **Infrastructure Layer** (internal/infrastructure/)
- **Repository** - Database implementation (PostgreSQL)
- External services, APIs

### 3. **Handler Layer** (internal/handler/)
- HTTP handlers (Gin)
- Request/Response transformation

### 4. **Container Layer** (internal/container/)
- DI Container using samber/do v2
- Dependency injection wiring

## Dependency Injection (samber/do v2)

```go
// container.go - Define providers
func Build() *do.RootScope {
    scope := do.New()
    do.ProvideValue(scope, config.Load())
    do.Provide(scope, NewDB)
    do.Provide(scope, NewPeraturanRepository)
    do.Provide(scope, NewPeraturanService)
    do.Provide(scope, NewPeraturanHandler)
    return scope
}

func NewPeraturanService(i do.Injector) (service.PeraturanService, error) {
    repo := do.MustInvoke[repository.PeraturanRepository](i)
    return service.NewPeraturanService(repo), nil
}

// main.go - Usage
scope := container.Build()
defer scope.Shutdown()

cfg := do.MustInvoke[*config.Config](scope)
handler := do.MustInvoke[*handler.PeraturanHandler](scope)
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /health | Health check |
| GET | /api/v1/peraturan | List peraturan |
| GET | /api/v1/peraturan/:id | Get peraturan by ID |
| POST | /api/v1/peraturan | Create peraturan |
| PUT | /api/v1/peraturan/:id | Update peraturan |
| DELETE | /api/v1/peraturan/:id | Delete peraturan |
| GET | /api/v1/peraturan/search?q=query | Search peraturan |
| GET | /api/v1/peraturan/:id/bab | List bab |
| GET | /api/v1/peraturan/:id/bab/:bab_id | Get bab by ID |
| GET | /api/v1/peraturan/:id/pasal | List pasal |
| GET | /api/v1/peraturan/:id/pasal/:pasal_id | Get pasal by ID |
| GET | /api/v1/peraturan/:id/pasal/:pasal_id/ayat | List ayat |
| GET | /api/v1/peraturan/:id/pasal/:pasal_id/ayat/:ayat_id | Get ayat by ID |

## Environment Variables

Copy `.env.example` to `.env` and configure:

```bash
cp .env.example .env
```

```env
# Server
SERVER_HOST=0.0.0.0
SERVER_PORT=8080
GIN_MODE=debug

# Database
DB_HOST=localhost
DB_PORT=5432
DB_USER=postgres
DB_PASSWORD=postgres
DB_NAME=peraturan_db
DB_SSLMODE=disable
```

## Running

```bash
cd apps/restapi

# Install dependencies
go mod tidy

# Copy environment file
cp .env.example .env

# Run
go run cmd/main.go

# Build
go build -o bin/app cmd/main.go
```

## Tech Stack

- **Language**: Go 1.22+
- **Framework**: Gin
- **Database**: PostgreSQL (pgx/v5)
- **DI Container**: samber/do v2
- **Env Loader**: godotenv
- **Architecture**: Clean Architecture / Hexagonal