# Parser

## Project Overview

Parser API adalah service untuk scraping dan parsing PDF peraturan dari peraturan.go.id. 
Service ini mengekstrak struktur peraturan (BAB, Pasal, Ayat) dan menyimpannya ke PostgreSQL database.

## Tech Stack

- **Language**: Python 3.10+
- **Package Manager**: uv
- **Framework**: FastAPI
- **Database**: PostgreSQL (asyncpg)
- **PDF Parser**: pdfplumber
- **Scraper**: aiohttp + beautifulsoup4

## Project Structure

```
apps/parser/
├── main.py              # FastAPI entry point
├── pyproject.toml       # Project configuration & dependencies
├── uv.lock              # Lock file for dependencies
├── .env                 # Environment variables (not committed)
├── .env.example         # Example environment variables
├── .python-version      # Python version (3.10)
├── api/
│   ├── __init__.py
│   └── routes.py        # FastAPI routes/endpoints
├── db/
│   ├── __init__.py
│   └── db.py            # Database connection pool & query helpers
├── models/
│   ├── __init__.py
│   ├── peraturan.py     # Peraturan Pydantic models
│   ├── bab.py           # Bab Pydantic models
│   ├── pasal.py         # Pasal Pydantic models
│   └── ayat.py          # Ayat Pydantic models
├── parser/
│   ├── __init__.py
│   ├── pdf_parser.py    # PDF parsing logic
│   ├── scraper.py       # Web scraping logic
│   └── status.py        # Parsing status management
├── repositories/
│   ├── __init__.py
│   ├── peraturan.py     # Peraturan database operations
│   ├── bab.py           # Bab database operations
│   ├── pasal.py         # Pasal database operations
│   └── ayat.py          # Ayat database operations
├── migrations/          # SQL migration files
│   ├── 001_create_tables.sql
│   ├── 002_create_indexes.sql
│   ├── 003_create_functions_triggers.sql
│   ├── 004_create_views.sql
│   └── 005_sample_data.sql
└── kubernetes/          # Kubernetes deployment files
```

## Commands

### Install Dependencies

```bash
cd apps/parser

# Install all dependencies
uv sync

# Install including dev dependencies
uv sync --all-extras
```

### Run Development Server

```bash
cd apps/parser

# Run with uvicorn (development mode)
uv run uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Or run directly
uv run python main.py
```

### Linting & Formatting

```bash
cd apps/parser

# Format code with Black
uv run black .

# Lint with Ruff
uv run ruff check .
```

### Testing

```bash
cd apps/parser

# Run tests
uv run pytest

# Run tests with coverage
uv run pytest --cov=.
```

## Database Schema

Database menggunakan PostgreSQL dengan tabel berikut:
- `peraturan` - Informasi peraturan (UU, PP, Perpres, dll)
- `bab` - BAB dari peraturan
- `pasals` - Pasal dari peraturan
- `ayats` - Ayat dari pasal
- `parsing_logs` - Log operasi parsing

Lihat `DATABASE_SCHEMA.md` untuk detail lengkap schema.

## Environment Variables

Buat file `.env` di root parser directory:

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

## Code Conventions

### Imports

```python
# Standard library
import os
import sys
from typing import Dict, List, Optional

# Third-party
from fastapi import FastAPI, HTTPException
import asyncpg

# Local modules
from db import get_db_connection, execute_query
from models.peraturan import PeraturanCreate, PeraturanResponse
```

### Database Operations

Gunakan `execute_query` helper untuk database operations:

```python
from db import execute_query

# SELECT single row
result = await execute_query(
    "SELECT * FROM peraturan WHERE id = $1",
    args=(peraturan_id,),
    fetch="one"
)

# SELECT value
count = await execute_query(
    "SELECT COUNT(*) FROM peraturan",
    fetch="val"
)

# SELECT multiple rows
results = await execute_query(
    "SELECT * FROM peraturan LIMIT $1 OFFSET $2",
    args=(limit, skip),
    fetch="all"
)

# INSERT/UPDATE/DELETE
affected = await execute_query(
    "DELETE FROM peraturan WHERE id = $1",
    args=(peraturan_id,),
    fetch="exec"
)
```

### Repository Pattern

Setiap tabel memiliki repository class dengan CRUD operations:

```python
class PeraturanRepository:
    async def create(self, data: Dict) -> str: ...
    async def get_by_id(self, id: str) -> Optional[Dict]: ...
    async def get_list(self, ...) -> Dict: ...
    async def update(self, id: str, data: Dict) -> bool: ...
    async def delete(self, id: str) -> bool: ...

# Singleton instance
peraturan_repository = PeraturanRepository()
```

### Async/Await

Semua database operations dan HTTP requests harus async:

```python
# Good
async def get_peraturan(peraturan_id: str):
    result = await execute_query(...)
    return result

# Bad - blocking
def get_peraturan(peraturan_id: str):
    result = execute_query(...)  # This will fail!
    return result
```

## API Endpoints

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

## Common Tasks

### Add New Model

1. Create model file in `models/`
2. Define Pydantic models (Base, Create, Update, Response)
3. Export from `models/__init__.py`

### Add New Repository

1. Create repository file in `repositories/`
2. Implement CRUD methods
3. Create singleton instance
4. Use in routes via import

### Add New API Endpoint

1. Add route in `api/routes.py`
2. Use repository for database operations
3. Return proper Pydantic response model

## Notes

- Gunakan `server_settings` untuk PostgreSQL settings, bukan `setup` parameter di asyncpg
- Semua SQL queries harus menggunakan positional parameters ($1, $2, dst) untuk mencegah SQL injection
- Return type dari `execute_query` dengan `fetch="exec"` adalah `int` (affected rows)
- Return type dari `execute_query` dengan `fetch="val"` bisa `None` jika tidak ada hasil
