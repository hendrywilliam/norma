# REST API - Peraturan

REST API untuk mengelola data peraturan dengan arsitektur Clean Architecture menggunakan Go dan DI Container (samber/do).

## Architecture

```
apps/restapi/
├── cmd/
│   └── main.go                 # Entry point
├── internal/
│   ├── config/
│   │   └── config.go           # Configuration loader
│   ├── container/
│   │   └── container.go        # DI Container (samber/do)
│   ├── domain/
│   │   ├── model/
│   │   │   └── peraturan.go    # Domain models
│   │   ├── repository/
│   │   │   └── repository.go   # Repository interfaces
│   │   └── service/
│   │       └── peraturan_service.go  # Business logic
│   ├── handler/
│   │   └── peraturan_handler.go # HTTP handlers
│   └── infrastructure/
│       └── repository/
│           └── postgres/
│               └── peraturan_repository.go # Repository implementation
├── pkg/
│   ├── database/
│   │   └── database.go         # Database connection
│   └── response/
│       └── response.go         # HTTP response helpers
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
- DI Container using samber/do
- Dependency injection wiring

## Dependency Injection (samber/do)

```go
// Container initialization
scope := container.NewContainer()
defer scope.Shutdown()

// Get dependencies
cfg := container.GetConfig(scope)
db := container.GetDB(scope)
repo := container.GetPeraturanRepository(scope)
service := container.GetPeraturanService(scope)
handler := container.GetPeraturanHandler(scope)
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

## Environment Variables

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

# Run
go run cmd/main.go

# Build
go build -o bin/app cmd/main.go
```

## Tech Stack

- **Language**: Go 1.22+
- **Framework**: Gin
- **Database**: PostgreSQL (pgx)
- **DI Container**: samber/do v2
- **Architecture**: Clean Architecture / Hexagonal