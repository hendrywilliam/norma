# Norma

Platform for managing and querying Indonesian legal documents (peraturan) from peraturan.go.id with AI-powered parsing using GLM-4V Vision Model.

Three services:
- **Parser** (Python/FastAPI) — Scrapes peraturan.go.id, converts PDF to images, extracts BAB/Pasal/Ayat structure via GLM-4V
- **REST API** (Go/Gin) — Clean Architecture CRUD for legal documents
- **Web** (Next.js 16/shadcn) — Browsing and search with Civic Ledger theme

Stack: PostgreSQL 16, Docker/K8s.

```bash
# Start Postgres
docker run -d --name peraturan_postgres -e POSTGRES_DB=peraturan_db -e POSTGRES_USER=postgres -e POSTGRES_PASSWORD=postgres -p 5432:5432 postgres:16-alpine

# Parser
cd apps/parser && cp .env.example .env && uv sync && uv run uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Web
cd apps/web && bun install && bun dev

# REST API
cd apps/restapi && cp .env.example .env && go mod tidy && go run cmd/main.go
```

AI parsing flow: Scrape HTML → Download PDF → Convert to images (PyMuPDF) → GLM-4V extracts structure → Save to DB.

See `apps/parser/DATABASE_SCHEMA.md` for schema details.

MIT License.
