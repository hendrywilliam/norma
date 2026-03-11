# Platform Peraturan Database & Chatbot

Platform untuk mengelola dan menelusuri database peraturan dari peraturan.go.id dengan fitur chatbot berbasis AI.

## Struktur Project

```
norma/
├── apps/
│   ├── parser/                    # HTTP Server untuk parsing PDF
│   │   ├── api/                   # API routes
│   │   ├── db/                    # Database operations
│   │   ├── models/                # Pydantic data models
│   │   ├── parser/                # Core parsing logic
│   │   │   ├── scraper.py         # Scraper peraturan.go.id
│   │   │   ├── pdf_parser.py      # PDF parser
│   │   │   └── status.py          # Status management
│   │   ├── main.py                # FastAPI entry point
│   │   ├── pyproject.toml         # UV configuration
│   │   ├── Dockerfile             # Docker container
│   │   └── README.md              # Parser documentation
│   └── web/                       # Frontend (coming soon)
├── docker/
│   └── postgres/
│       └── init.sql               # Database init script
├── docker-compose.yml             # Docker services
└── README.md                      # This file
```

## Fitur Utama

- **Parser**: HTTP Server untuk scrape dan parse PDF dari peraturan.go.id
- **Database**: PostgreSQL dengan full-text search untuk menyimpan data peraturan
- **API**: REST API untuk trigger parsing, cek status, dan query peraturan
- **Chatbot**: Tanya jawab tentang peraturan menggunakan AI (coming soon)
- **Search**: Cari peraturan berdasarkan kategori, tahun, atau keyword dengan full-text search

## Tech Stack

### Parser
- **Language**: Python 3.11+
- **Framework**: FastAPI
- **Package Manager**: UV
- **PDF Parsing**: pdfplumber
- **Web Scraping**: BeautifulSoup4 + Requests
- **Database**: PostgreSQL + psycopg2
- **Docker**: Docker + Docker Compose

### Frontend (Coming Soon)
- **Framework**: React/Next.js
- **UI Library**: TBD
- **Chatbot**: OpenAI API / LangChain

## Prerequisites

- Docker dan Docker Compose
- Python 3.11+ (untuk local development)
- UV package manager (install: `pip install uv`)

## Instalasi

### Clone Repository

```bash
git clone https://github.com/username/norma.git
cd norma
```

### Setup Environment Variables

Buat file `.env` di root project:

```env
# Database
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/peraturan_db
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=peraturan_db

# Parser
PARSER_HOST=0.0.0.0
PARSER_PORT=8000

# Peraturan.go.id
PERATURAN_BASE_URL=https://peraturan.go.id
```

### Start Services dengan Docker

```bash
# Start semua services
docker-compose up -d

# Start PostgreSQL saja
docker-compose up -d postgres

# Start PostgreSQL dan Parser
docker-compose --profile parser up -d

# Start dengan PgAdmin (optional)
docker-compose --profile admin --profile parser up -d
```

### Install Parser Dependencies untuk Local Development

```bash
cd apps/parser

# Install dependencies dengan UV
uv sync

# Install dev dependencies
uv sync --extra dev
```

## Running

### Menggunakan Docker (Recommended)

```bash
# Start parser service
docker-compose --profile parser up -d parser

# Cek logs
docker-compose logs -f parser

# Stop service
docker-compose down
```

### Local Development

```bash
# Start PostgreSQL (jika belum berjalan)
docker-compose up -d postgres

# Run parser development server
cd apps/parser
uv run uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## API Endpoints

Parser API berjalan di `http://localhost:8000`

### Health Check
```http
GET /health
```

### Get Parsing Status
```http
GET /status
```

### Trigger Parsing
```http
POST /parse
Content-Type: application/json

{
  "url": "https://peraturan.go.id/peraturan-detail",
  "category": "UU",
  "year": 2023,
  "force": false
}
```

### List Peraturan
```http
GET /api/peraturan?skip=0&limit=20&category=UU&year=2023&search=keyword
```

### Get Peraturan Detail
```http
GET /api/peraturan/{peraturan_id}
```

### Re-parse Peraturan
```http
POST /api/peraturan/{peraturan_id}/reparse
```

Lihat dokumentasi lengkap API di `apps/parser/README.md`

## Database

### Access PostgreSQL

```bash
# Menggunakan psql
docker exec -it peraturan_postgres psql -U postgres -d peraturan_db

# Menggunakan PgAdmin
# Buka http://localhost:5050
# Email: admin@peraturan.local
# Password: admin
```

### Schema

Tabel utama: `peraturan`

| Column | Type | Description |
|--------|------|-------------|
| id | VARCHAR(255) | Primary Key |
| judul | VARCHAR(1000) | Judul peraturan |
| nomor | VARCHAR(100) | Nomor peraturan |
| tahun | INTEGER | Tahun peraturan |
| kategori | VARCHAR(50) | Kategori (UU, PP, Perpres, dll) |
| url | VARCHAR(500) | URL sumber |
| pdf_url | VARCHAR(500) | URL PDF |
| konten | TEXT | Konten dari PDF |
| created_at | TIMESTAMP | Waktu dibuat |
| updated_at | TIMESTAMP | Waktu diupdate |

## Development

### Testing

```bash
cd apps/parser

# Run tests
uv run pytest

# Run tests dengan coverage
uv run pytest --cov=parser --cov-report=html
```

### Code Quality

```bash
# Format code dengan Black
uv run black .

# Lint dengan Ruff
uv run ruff check .

# Fix lint issues
uv run ruff check --fix .
```

### Project Structure for Parser

```
apps/parser/
├── api/
│   └── routes.py              # API routes definitions
├── db/
│   └── peraturan.py           # Database CRUD operations
├── models/
│   └── peraturan.py           # Pydantic models
├── parser/
│   ├── scraper.py             # Scraping logic
│   ├── pdf_parser.py          # PDF parsing logic
│   └── status.py              # Status management
├── main.py                     # FastAPI application
├── pyproject.toml              # Project configuration
├── Dockerfile                  # Docker container
└── README.md                   # Parser documentation
```

## Troubleshooting

### Docker Issues

```bash
# Cek status containers
docker-compose ps

# Cek logs
docker-compose logs

# Rebuild container
docker-compose build --no-cache parser

# Reset semua volumes (WARNING: hapus semua data!)
docker-compose down -v
```

### Database Issues

```bash
# Reset database
docker exec -it peraturan_postgres psql -U postgres -d peraturan_db -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public;"
docker-compose restart postgres
```

### Parser Issues

```bash
# Cek parser status
curl http://localhost:8000/health

# Cek parsing status
curl http://localhost:8000/status

# Trigger parsing (debug)
curl -X POST http://localhost:8000/parse \
  -H "Content-Type: application/json" \
  -d '{"limit": 5}'
```

## Contributing

1. Fork repository
2. Buat feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push ke branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## License

TBD

## Authors

TBD

## Acknowledgments

- Peraturan.go.id untuk sumber data peraturan
- FastAPI untuk framework backend yang amazing
- UV untuk package manager yang super cepat