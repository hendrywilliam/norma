# Navigate ke parser directory
cd apps/parser

# Install dependencies dengan UV
uv sync

# Atau install dev dependencies
uv sync --extra dev
```

## Environment Variables

Buat file `.env` di root parser directory:

```env
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/peraturan_db

# API Configuration
HOST=0.0.0.0
PORT=8000

# Peraturan.go.id Configuration
BASE_URL=https://peraturan.go.id
```

## Running

```bash
# Run development server dengan UV
uv run uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Atau run langsung
python main.py
```

## API Endpoints

### Health Check
```http
GET /health
```

Response:
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T00:00:00"
}
```

### Get Parsing Status
```http
GET /status
```

Response:
```json
{
  "is_running": false,
  "last_run": "2024-01-01T00:00:00",
  "last_success": "2024-01-01T00:00:00",
  "total_parsed": 150,
  "error": null
}
```

### Trigger Parsing
```http
POST /parse
Content-Type: application/json

{
  "url": "https://peraturan.go.id/peraturan-detail",
  "category": "UU",
  "year": 2023
}
```

Request Body:
- `url` (optional): URL spesifik untuk parsing
- `category` (optional): Filter kategori (UU, PP, Perpres, dll)
- `year` (optional): Filter tahun

Response:
```json
{
  "status": "queued",
  "message": "Parsing task di-queue: https://peraturan.go.id/peraturan-detail",
  "job_id": "1704067200.0"
}
```

## Development

### Project Structure

```
apps/parser/
├── main.py              # Entry point FastAPI
├── pyproject.toml       # UV configuration & dependencies
├── api/                 # API routes
├── parser/              # Core parsing logic
├── db/                  # Database operations
├── models/              # Data models
└── README.md            # This file
```

### Testing

```bash
# Run tests
uv run pytest

# Run tests dengan coverage
uv run pytest --cov=parser
```

### Code Quality

```bash
# Format code dengan Black
uv run black .

# Lint dengan Ruff
uv run ruff check .
```

## Next Steps

- [ ] Implement core parsing logic di parser/
- [ ] Setup database models di db/
- [ ] Implement API routes di api/
- [ ] Add error handling dan logging
- [ ] Add unit tests