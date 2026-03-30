# Norma - Indonesian Legal Documents Database

Platform for managing and querying Indonesian legal documents (peraturan) from peraturan.go.id with AI-powered parsing using GLM-4V Vision Model.

## Project Structure

```
norma/
├── apps/
│   ├── parser/                    # PDF Parser Service (Python/FastAPI)
│   │   ├── api/                    # API routes
│   │   ├── db/                     # Database operations
│   │   ├── models/                 # Pydantic data models
│   │   │   ├── peraturan.py        # Peraturan model
│   │   │   ├── bab.py              # Bab model
│   │   │   ├── pasal.py            # Pasal model
│   │   │   ├── ayat.py             # Ayat model
│   │   │   └── ai_parse.py         # AI parsing models
│   │   ├── parser/                 # Core parsing logic
│   │   │   ├── scraper.py          # peraturan.go.id scraper
│   │   │   ├── pdf_parser.py       # PDF parser
│   │   │   ├── ai_agent.py         # GLM-4V vision model integration
│   │   │   └── status.py           # Parsing status management
│   │   ├── repositories/           # Database repositories
│   │   ├── migrations/             # SQL migration files
│   │   ├── main.py                 # FastAPI entry point
│   │   ├── pyproject.toml          # UV package configuration
│   │   └── README.md               # Parser documentation
│   │
│   ├── restapi/                   # REST API Service (Go/Gin)
│   │   ├── cmd/main.go             # Entry point
│   │   ├── internal/
│   │   │   ├── config/            # Configuration loader
│   │   │   ├── container/         # DI Container (samber/do)
│   │   │   ├── domain/            # Domain layer
│   │   │   ├── handler/           # HTTP handlers
│   │   │   └── infrastructure/    # Infrastructure layer
│   │   ├── pkg/
│   │   │   ├── database/          # Database connection
│   │   │   └── response/           # HTTP response helpers
│   │   ├── go.mod
│   │   └── README.md
│   │
│   └── web/                        # Frontend (Next.js)
│       ├── app/
│       │   ├── layout.tsx          # Root layout
│       │   ├── page.tsx             # Homepage
│       │   ├── globals.css          # Civic Ledger theme
│       │   └── peraturan/
│       │       ├── page.tsx         # Peraturan list
│       │       └── [id]/page.tsx    # Peraturan detail
│       ├── components/
│       │   ├── navbar.tsx          # Navigation
│       │   └── ui/                  # shadcn components
│       ├── lib/utils.ts            # Utilities
│       ├── package.json
│       └── README.md
│
├── docker/
│   └── postgres/
│       └── init.sql               # Database init script
│
├── docker-compose.yml            # Docker services
└── README.md                     # This file
```

## Features

- **Parser Service**: Scrape and parse PDF documents from peraturan.go.id
  - Web scraping from peraturan.go.id
  - PDF to image conversion (PyMuPDF)
  - AI-powered parsing with GLM-4V Vision Model
  - Extract BAB, Pasal, Ayat structure
- **REST API**: Manage legal documents with Clean Architecture (Go)
- **Web Frontend**: Next.js 16 with shadcn/ui components
  - Civic Ledger theme (professional legal document styling)
  - Responsive design
  - Peraturan browsing and search
- **Database**: PostgreSQL with full-text search support

## Tech Stack

### Parser Service (Python)
- **Language**: Python 3.10+
- **Framework**: FastAPI
- **Package Manager**: UV
- **PDF Processing**: pdfplumber, PyMuPDF
- **AI Vision**: GLM-4V (Zhipu AI)
- **Web Scraping**: aiohttp + BeautifulSoup4
- **Database**: PostgreSQL (asyncpg)

### REST API Service (Go)
- **Language**: Go 1.23+
- **Framework**: Gin
- **Database**: PostgreSQL (pgx/v5)
- **DI Container**: samber/do v2
- **Architecture**: Clean Architecture / Hexagonal

### Web Frontend (Next.js)
- **Framework**: Next.js 16 (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS v4
- **UI Components**: shadcn/ui
- **Theme**: Civic Ledger (professional legal document styling)
- **Icons**: Lucide React

### Database
- **Primary**: PostgreSQL 16
- **Admin**: pgAdmin4 (optional)

## Prerequisites

- Docker and Docker Compose
- Python 3.10+ (for local parser development)
- Go 1.23+ (for local REST API development)
- Node.js 18+ (for web development)
- UV package manager: `pip install uv`
- Bun: `npm install -g bun`

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

# Or using docker-compose
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

### 4. Run Web Frontend

```bash
cd apps/web

# Install dependencies
bun install

# Run development server
bun dev
```

### 5. Run REST API Service

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

# GLM AI Configuration (for AI-based parsing)
GLM_API_KEY=your_glm_api_key_here
GLM_MODEL=glm-4v
GLM_MAX_TOKENS=4096
GLM_TEMPERATURE=0.1
GLM_TIMEOUT=120

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
| GET | `/api/health` | Health check |
| GET | `/api/status` | Parsing status |
| POST | `/api/parse` | Trigger AI parsing (GLM-4V) |
| POST | `/api/parse/ai` | Trigger AI parsing for existing peraturan |
| POST | `/api/parse/ai/url` | AI parse from PDF URL |
| GET | `/api/parse/ai/status/{job_id}` | Get AI parsing job status |
| GET | `/api/parse/ai/result/{job_id}` | Get AI parsing result |
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
| GET | `/api/v1/peraturan/:id/pasal` | List pasal |
| GET | `/api/v1/peraturan/:id/pasal/:pasal_id/ayat` | List ayat |

### Web Frontend (Port 3000)

| Path | Description |
|------|-------------|
| `/` | Homepage with search and statistics |
| `/peraturan` | Peraturan list with filters |
| `/peraturan/[id]` | Peraturan detail with BAB/Pasal structure |

## AI Parsing Flow

```
POST /api/parse
       │
       ▼
┌─────────────────────────┐
│  1. Load GLM_API_KEY    │ → from environment
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────┐
│  2. Scrape HTML         │ → metadata (judul, nomor, pdf_url)
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────┐
│  3. Download PDF        │
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────┐
│  4. PDF → Images        │ → PyMuPDF convert pages
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────┐
│  5. GLM-4V Vision       │ → Extract BAB, Pasal, Ayat
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────┐
│  6. Save to Database    │ → peraturan, bab, pasal, ayat
└─────────────────────────┘
```

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
uv run ruff format .

# Lint code
uv run ruff check .
uv run ruff check --fix .
```

### Web Frontend

```bash
cd apps/web

# Run development server
bun dev

# Build for production
bun run build

# Run lint
bun run lint
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
  GLM-4V Agent (parser/ai_agent.py)
      │
      ├── PDF → Images (PyMuPDF)
      │
      └── GLM-4V API → Extract Structure
           │
           ▼
  Repository Layer (repositories/)
      │
      ▼
  PostgreSQL Database
```

### Web Frontend Architecture

```
Next.js App Router
      │
      ├── Layout (navbar, theme)
      │
      ├── Homepage
      │   ├── Search
      │   ├── Statistics Cards
      │   └── Recent Peraturan
      │
      └── Peraturan Pages
          ├── List (filter, search, table)
          └── Detail (BAB accordion, Pasal preview)
```

## Theme: Civic Ledger

The web frontend uses the **Civic Ledger** theme designed for professional legal document interfaces:

- **Primary**: Deep Navy Blue (`#1e3a5f`)
- **Accents**: 
  - Emerald (PP badges)
  - Amber (Perpres badges)
  - Teal (Permen badges)
- **Typography**: Inter font
- **Components**: shadcn/ui with Tailwind CSS v4

## License

MIT License