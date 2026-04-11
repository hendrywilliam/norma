# Norma - Indonesian Legal Documents Database

Platform for managing and querying Indonesian legal documents (peraturan) from peraturan.go.id with AI-powered parsing using GLM-4V Vision Model.

## Project Structure

```
norma/
├── apps/
│   ├── kubernetes/                  # Shared Kubernetes resources
│   │   ├── namespace.yaml           # Namespace definition
│   │   └── secret.yaml              # Shared secrets
│   │
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
│   │   ├── kubernetes/             # Kubernetes manifests
│   │   │   ├── namespace.yaml      # Parser namespace
│   │   │   ├── configmap.yaml      # ConfigMap
│   │   │   ├── secret.yaml         # Secrets
│   │   │   ├── parser-deployment.yaml
│   │   │   ├── parser-service.yaml
│   │   │   ├── ingress.yaml        # Ingress rules
│   │   │   ├── hpa.yaml            # Horizontal Pod Autoscaler
│   │   │   ├── pvc.yaml            # Persistent Volume Claims
│   │   │   └── postgres-*.yaml      # PostgreSQL resources
│   │   ├── main.py                 # FastAPI entry point
│   │   ├── Dockerfile              # Docker image
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
│   │   ├── kubernetes/             # Kubernetes manifests
│   │   │   ├── restapi-deployment.yaml
│   │   │   └── restapi-service.yaml
│   │   ├── Dockerfile              # Docker image
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
│       ├── kubernetes/             # Kubernetes manifests
│       │   ├── web-deployment.yaml
│       │   ├── web-service.yaml
│       │   └── web-ingress.yaml
│       ├── lib/utils.ts            # Utilities
│       ├── Dockerfile              # Docker image
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

## Kubernetes Deployment

Project ini mendukung deployment ke Kubernetes cluster. Struktur Kubernetes dibagi menjadi:

### Struktur Folder Kubernetes

```
apps/
├── kubernetes/                          # Shared Kubernetes resources
│   ├── namespace.yaml                   # Namespace definition (norma)
│   └── secret.yaml                      # Shared secrets (DB password)
│
├── parser/kubernetes/                   # Parser service K8s resources
│   ├── namespace.yaml                   # Parser namespace
│   ├── configmap.yaml                   # ConfigMap for env vars
│   ├── secret.yaml                      # Parser secrets
│   ├── parser-deployment.yaml           # Parser deployment
│   ├── parser-service.yaml              # Parser service
│   ├── ingress.yaml                     # Ingress rules
│   ├── hpa.yaml                         # Horizontal Pod Autoscaler
│   ├── pvc.yaml                         # Persistent Volume Claims
│   └── postgres-*.yaml                  # PostgreSQL resources
│
├── restapi/kubernetes/                  # REST API service K8s resources
│   ├── restapi-deployment.yaml          # REST API deployment
│   └── restapi-service.yaml             # REST API service
│
└── web/kubernetes/                      # Web frontend K8s resources
    ├── web-deployment.yaml              # Web deployment
    ├── web-service.yaml                 # Web service
    └── web-ingress.yaml                 # Web ingress
```

### Penjelasan Struktur

1. **`apps/kubernetes/`** - Shared resources yang digunakan oleh semua services:
   - `namespace.yaml` - Mendefinisikan namespace `norma` untuk mengelompokkan semua resources
   - `secret.yaml` - Secret yang digunakan bersama: `DB_PASSWORD`, `API_URL`

2. **`apps/parser/kubernetes/`** - Kubernetes resources khusus untuk parser service:
   - Deployment, Service, Ingress, HPA, PVC, ConfigMap, Secret, dan PostgreSQL resources

3. **`apps/restapi/kubernetes/`** - Kubernetes resources untuk REST API service:
   - Deployment dan Service untuk menjalankan Go REST API

4. **`apps/web/kubernetes/`** - Kubernetes resources untuk web frontend:
   - Deployment, Service, dan Ingress untuk Next.js web app

### Deploy ke Kubernetes

```bash
# 1. Create namespace dan shared secrets
kubectl apply -f apps/kubernetes/namespace.yaml
kubectl apply -f apps/kubernetes/secret.yaml

# 2. Deploy REST API (port 8080)
kubectl apply -f apps/restapi/kubernetes/

# 3. Deploy Web Frontend (port 3000)
kubectl apply -f apps/web/kubernetes/

# 4. Deploy Parser Service (jika diperlukan)
kubectl apply -f apps/parser/kubernetes/namespace.yaml
kubectl apply -f apps/parser/kubernetes/configmap.yaml
kubectl apply -f apps/parser/kubernetes/secret.yaml
kubectl apply -f apps/parser/kubernetes/parser-deployment.yaml
kubectl apply -f apps/parser/kubernetes/parser-service.yaml
kubectl apply -f apps/parser/kubernetes/ingress.yaml

# Check deployment status
kubectl get all -n norma
kubectl get all -n norma-parser

# View logs
kubectl logs -f deployment/restapi -n norma
kubectl logs -f deployment/web -n norma
kubectl logs -f deployment/parser-api -n norma-parser
```

### Build Docker Images

Sebelum deploy ke K8s, build Docker images terlebih dahulu:

```bash
# Build REST API image
docker build -t norma-restapi:latest apps/restapi/

# Build Web Frontend image
docker build -t norma-web:latest apps/web/

# Build Parser image
docker build -t norma-parser:latest apps/parser/
```

### Ingress Configuration

Pastikan ingress controller sudah terinstall di cluster (misalnya NGINX Ingress Controller):

```bash
# Install NGINX Ingress Controller (jika belum)
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.8.2/deploy/static/provider/cloud/deploy.yaml

# Update /etc/hosts untuk local development
echo "127.0.0.1 web.norma.local" | sudo tee -a /etc/hosts
echo "127.0.0.1 parser.norma.local" | sudo tee -a /etc/hosts
```

### Service URLs (dalam cluster)

- **REST API**: `http://restapi-service:8080`
- **Web Frontend**: `http://web-service:3000`
- **Parser**: `http://parser-api-service:8000`

### Environment Variables di Kubernetes

Environment variables dikonfigurasi di deployment files:

**REST API**:
- `SERVER_HOST`, `SERVER_PORT`, `GIN_MODE`
- `DB_HOST`, `DB_PORT`, `DB_USER`, `DB_NAME`, `DB_SSLMODE`
- `DB_PASSWORD` - dari Secret `norma-secrets`

**Web Frontend**:
- `NODE_ENV=production`
- `API_URL` - dari Secret `norma-secrets` (server-side only, tidak di-expose ke client)
- Catatan: Client mengakses backend melalui internal API routes (`/api/peraturan/*`)

**Parser**:
- Semua env vars dari ConfigMap dan Secret
- Lihat `apps/parser/kubernetes/configmap.yaml` dan `apps/parser/kubernetes/secret.yaml`

**Secrets**:

Secrets disimpan di `apps/kubernetes/secret.yaml`:
- `DB_PASSWORD` - Database password
- `API_URL` - REST API URL (server-side only, tidak di-expose ke client)

```bash
# Edit secret jika perlu
kubectl edit secret norma-secrets -n norma
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

## License

MIT License
