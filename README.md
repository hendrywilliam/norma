# Norma - Indonesian Legal Documents Database & Chatbot

Platform for managing and querying Indonesian legal documents (peraturan) from peraturan.go.id.

## Project Structure

```
norma/
├── apps/
│   ├── parser/                    # PDF Parser Service (Python/FastAPI)
│   │   ├── api/                    # API routes
│   │   ├── db/                     # Database operations
│   │   ├── models/                 # Pydantic data models
│   │   ├── parser/                 # Core parsing logic
│   │   │   ├── scraper.py          # peraturan.go.id scraper
│   │   │   ├── pdf_parser.py       # PDF parser
│   │   │   └── status.py           # Parsing status management
│   │   ├── repositories/           # Database repositories
│   │   ├── migrations/             # SQL migration files
│   │   ├── main.py                # FastAPI entry point
│   │   ├── pyproject.toml         # UV package configuration
│   │   └── Dockerfile             # Docker container
│   │
│   ├── restapi/                   # REST API Service (Go/Gin)
│   │   ├── cmd/main.go            # Entry point
│   │   ├── internal/
│   │   │   ├── config/            # Configuration loader
│   │   │   ├── container/         # DI Container (samber/do)
│   │   │   ├── domain/            # Domain layer
│   │   │   │   ├── model/        # Entity models
│   │   │   │   ├── repository/   # Repository interfaces
│   │   │   │   └── service/      # Business logic
│   │   │   ├── handler/          # HTTP handlers
│   │   │   └── infrastructure/   # Infrastructure layer
│   │   │       └── repository/   # Repository implementations
│   │   ├── pkg/
│   │   │   ├── database/         # Database connection
│   │   │   └── response/        # HTTP response helpers
│   │   ├── go.mod
│   │   └── README.md
│   │
│   └── web/                       # Frontend (Planned)
│
├── docker/
│   └── postgres/
│       └── init.sql              # Database init script
│
├── docker-compose.yml            # Docker services
└── README.md                     # This file
```

## Features

- **Parser Service**: Scrape and parse PDF documents from peraturan.go.id
- **REST API**: Manage legal documents with Clean Architecture (Go)
- **Database**: PostgreSQL with full-text search support
- **Chatbot**: AI-powered Q&A about legal documents (Planned)

## Tech Stack

### Parser Service (Python)
- **Language**: Python 3.10+
- **Framework**: FastAPI
- **Package Manager**: UV
- **PDF Parsing**: pdfplumber, PyMuPDF
- **Web Scraping**: aiohttp + BeautifulSoup4
- **Database**: PostgreSQL (asyncpg)

### REST API Service (Go)
- **Language**: Go 1.23+
- **Framework**: Gin
- **Database**: PostgreSQL (pgx/v5)
- **DI Container**: samber/do v2
- **Architecture**: Clean Architecture / Hexagonal

### Database
- **Primary**: PostgreSQL 16
- **Admin**: pgAdmin4 (optional)

## Prerequisites

- Docker and Docker Compose
- Python 3.10+ (for local parser development)
- Go 1.23+ (for local REST API development)
- UV package manager: `pip install uv`

## Quick Start

### 1. Clone Repository

```bash
git clone https://github.com/hendrywilliam/norma.git
cd norma
```

### 2. Start PostgreSQL

```bash
# Using Docker (recommended)
docker run -d \
  --name peraturan_postgres \
  -e POSTGRES_DB=peraturan_db \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=postgres \
  -p 5432:5432 \
  postgres:16-alpine

# Or using docker-compose (if uncommented in docker-compose.yml)
docker-compose up -d postgres
```

### 3. Run Parser Service

```bash
cd apps/parser

# Copy environment file
cp .env.example .env

# Install dependencies
uv sync

# Run development server
uv run uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 4. Run REST API Service

```bash
cd apps/restapi

# Copy environment file
cp .env.example .env

# Install dependencies
go mod tidy

# Run server
go run cmd/main.go
```

## Environment Variables

### Parser Service (.env)

```env
# Database
DB_HOST=localhost
DB_PORT=5432
DB_NAME=peraturan_db
DB_USER=postgres
DB_PASSWORD=postgres
DB_MIN_CONNECTIONS=1
DB_MAX_CONNECTIONS=10

# API Configuration
HOST=0.0.0.0
PORT=8000
RELOAD=false
LOG_LEVEL=info

# Peraturan.go.id
BASE_URL=https://peraturan.go.id
```

### REST API Service (.env)

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

## API Endpoints

### Parser Service (Port 8000)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | API info |
| GET | `/api/health` | Health check |
| GET | `/api/status` | Parsing status |
| POST | `/api/parse` | Trigger parsing |
| GET | `/api/peraturan` | List peraturan |
| GET | `/api/peraturan/{id}` | Get peraturan detail |
| GET | `/api/peraturan/{id}/bab` | List bab |
| GET | `/api/peraturan/{id}/pasals` | List pasal |
| GET | `/api/peraturan/{id}/pasals/{pasal_id}/ayats` | List ayat |

### REST API Service (Port 8080)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |
| GET | `/api/v1/peraturan` | List peraturan |
| GET | `/api/v1/peraturan/:id` | Get peraturan by ID |
| POST | `/api/v1/peraturan` | Create peraturan |
| PUT | `/api/v1/peraturan/:id` | Update peraturan |
| DELETE | `/api/v1/peraturan/:id` | Delete peraturan |
| GET | `/api/v1/peraturan/search?q=query` | Search peraturan |
| GET | `/api/v1/peraturan/:id/bab` | List bab |
| GET | `/api/v1/peraturan/:id/bab/:bab_id` | Get bab by ID |
| GET | `/api/v1/peraturan/:id/pasal` | List pasal |
| GET | `/api/v1/peraturan/:id/pasal/:pasal_id` | Get pasal by ID |
| GET | `/api/v1/peraturan/:id/pasal/:pasal_id/ayat` | List ayat |
| GET | `/api/v1/peraturan/:id/pasal/:pasal_id/ayat/:ayat_id` | Get ayat by ID |

## Database Schema

Main tables:
- `peraturan` - Legal document metadata (UU, PP, Perpres, etc.)
- `bab` - Chapters (BAB) of legal documents
- `pasals` - Articles (Pasal) of legal documents
- `ayats` - Paragraphs (Ayat) of articles
- `parsing_logs` - Parsing operation logs

See `apps/parser/DATABASE_SCHEMA.md` for complete schema details.

## Development

### Parser Service

```bash
cd apps/parser

# Run tests
uv run pytest

# Run tests with coverage
uv run pytest --cov=. --cov-report=html

# Format code
uv run black .

# Lint code
uv run ruff check .
uv run ruff check --fix .
```

### REST API Service

```bash
cd apps/restapi

# Build binary
go build -o bin/app cmd/main.go

# Run tests
go test ./...
```

## Docker Deployment

```bash
# Run all services
docker-compose --profile parser up -d

# Run with pgAdmin
docker-compose --profile parser --profile admin up -d

# View logs
docker-compose logs -f parser

# Stop services
docker-compose down
```

## Architecture

### Parser Service Architecture

```
Client Request
      │
      ▼
  FastAPI Routes (api/routes.py)
      │
      ▼
  Repository Layer (repositories/)
      │
      ▼
  PostgreSQL Database
      │
      ▼
  Parser Modules (parser/)
      ├── scraper.py (web scraping)
      └── pdf_parser.py (PDF extraction)
```

### REST API Service Architecture (Clean Architecture)

```
Client Request
      │
      ▼
  Handler Layer (internal/handler/)
      │
      ▼
  Service Layer (internal/domain/service/)
      │
      ▼
  Repository Interface (internal/domain/repository/)
      │
      ▼
  Repository Implementation (internal/infrastructure/repository/)
      │
      ▼
  PostgreSQL Database
```

## Services Comparison

| Feature | Parser (Python) | REST API (Go) |
|---------|-----------------|---------------|
| Language | Python 3.10+ | Go 1.23+ |
| Framework | FastAPI | Gin |
| Architecture | Layered | Clean Architecture |
| DI Container | - | samber/do v2 |
| Database Driver | asyncpg | pgx/v5 |
| Async Support | Yes (async/await) | Yes (goroutines) |
| Purpose | Scrape & Parse PDF | CRUD Operations |

## License

MIT License
