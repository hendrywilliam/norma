# Parser Service

Service untuk scraping dan parsing PDF peraturan dari peraturan.go.id dengan struktur BAB, Pasal, dan Ayat.

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           PARSER SERVICE ARCHITECTURE                        │
└─────────────────────────────────────────────────────────────────────────────┘

┌────────────────┐
│   PDF Source    │
│   (URL/Local)   │
└───────┬────────┘
        │
        ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                              PDF PARSER                                      │
│  ┌─────────────────────┐          ┌─────────────────────────────────────┐    ││
│  │    pdfplumber       │          │      PyMuPDF (fitz)                │    ││
│  │  (Text Extraction)  │          │   (PDF to Image Conversion)         │    ││
│  └─────────────────────┘          └─────────────────────────────────────┘    │
└───────┬──────────────────────────────────────┬────────────────────────────────┘│         │                                       │
        │                                       │
        ▼                                       ▼
┌────────────────────┐              ┌─────────────────────────┐
│   Text Content     │              │   Image per Page        │
│   (Raw Text)       │              │   (PNG/JPEG Base64)     │
└────────────────────┘              └───────────┬─────────────┘│
                                                    │
                                                    ▼
                                        ┌───────────────────────────────┐
                                        │      VISION MODEL / MCP       │
                                        │         (GLM-4V)              │
                                        │                               │
                                        │  Extract structured data:     │
                                        │  - BAB (chapters)             │
                                        │  - Pasal (articles)           │
                                        │  - Ayat (sections)            │
                                        │  - Konten (content)           │
                                        └───────────┬───────────────────┘
                                                    │
                                                    ▼
                                        ┌───────────────────────────────┐
                                        │      STRUCTURED JSON          │
                                        │                               │
                                        │  {                            │
                                        │    "bab": [...],              │
                                        │    "pasal": [...],            │
                                        │    "ayat": [...]              │
                                        │  }                            │
                                        └───────────┬───────────────────┘
                                                    │
        ┌───────────────────────────────────────────┘
        │
        ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           DATABASE LAYER                                     │
│  ┌────────────────┐    ┌────────────────┐    ┌────────────────┐            ││
│  │   PostgreSQL   │    │  Repository    │    │    Models      │            ││
│  │   (asyncpg)    │◄───│    Pattern     │◄───│   (Pydantic)   │            ││
│  └────────────────┘    └────────────────┘    └────────────────┘            ││
│                                                                               │
│  Tables:                                                                      │
│  - peraturan (regulations)                                                   │
│  - bab (chapters)                                                             │
│  - pasals (articles)                                                          │
│  - ayats (sections)                                                           │
│  - parsing_logs                                                               │
└─────────────────────────────────────────────────────────────────────────────┘
        │
        ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                              API LAYER                                        │
│  ┌────────────────┐    ┌────────────────┐    ┌────────────────┐            ││
│  │   FastAPI      │    │  REST Routes   │    │   Health       │            ││
│  │   Server       │    │  /api/parse    │    │   Check        │            ││
│  │   (Port 8000)  │    │  /api/peraturan│    │   /health      │            ││
│  └────────────────┘    └────────────────┘    └────────────────┘            │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Tech Stack

- **Language**: Python 3.10+
- **Package Manager**: uv
- **Framework**: FastAPI
- **Database**: PostgreSQL (asyncpg)
- **PDF Parsing**: pdfplumber, PyMuPDF
- **Vision**: GLM-4V / MCP Vision
- **Scraper**: aiohttp + beautifulsoup4

## Quick Start

```bash
# Navigate to parser directory
cd apps/parser

# Install dependencies
uv sync

# Run development server
uv run uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## Environment Variables

Buat file `.env` di root parser directory:

```env
# Database
DB_HOST=localhost
DB_PORT=5432
DB_NAME=peraturan_db
DB_USER=postgres
DB_PASSWORD=postgres

# API Configuration
HOST=0.0.0.0
PORT=8000

# Vision Model (GLM-4V)
GLM_API_KEY=your-api-key
GLM_MODEL=glm-4v-flash

# Peraturan.go.id
BASE_URL=https://peraturan.go.id
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |
| GET | `/api/status` | Parsing status |
| POST | `/api/parse` | Trigger parsing |
| GET | `/api/peraturan` | List peraturan |
| GET | `/api/peraturan/{id}` | Get peraturan detail |
| GET | `/api/peraturan/{id}/bab` | List bab |
| GET | `/api/peraturan/{id}/pasals` | List pasal |
| GET | `/api/peraturan/{id}/pasals/{pasal_id}/ayats` | List ayat |

## Development

### Project Structure

```
apps/parser/
├── main.py                    # FastAPI entry point
├── pyproject.toml             # UV configuration
├── api/
│   └── routes.py              # API routes
├── db/
│   └── db.py                  # Database connection
├── models/
│   ├── peraturan.py           # Peraturan model
│   ├── bab.py                 # Bab model
│   ├── pasal.py               # Pasal model
│   └── ayat.py                # Ayat model
├── parser/
│   ├── pdf_parser.py          # PDF parsing logic
│   ├── scraper.py             # Web scraping logic
│   └── status.py              # Status management
├── repositories/
│   ├── peraturan.py           # Peraturan CRUD
│   ├── bab.py                 # Bab CRUD
│   ├── pasal.py               # Pasal CRUD
│   └── ayat.py                # Ayat CRUD
└── migrations/                 # SQL migrations
```

### Testing

```bash
# Run tests
uv run pytest

# Run tests with coverage
uv run pytest --cov=.
```

### Linting & Formatting

```bash
# Format code
uv run ruff format .

# Lint code
uv run ruff check .
```

## Vision Model Integration

### GLM-4V / MCP Vision

PDF pages are converted to images and processed by GLM-4V for structured data extraction:

```python
import fitz  # PyMuPDF
from PIL import Image
import base64
import io

def pdf_to_images(pdf_path: str):
    doc = fitz.open(pdf_path)
    images = []
    
    for page_num in range(len(doc)):
        page = doc[page_num]
        pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))  # 2x scale
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        
        # Convert to base64
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        img_b64 = base64.b64encode(buffer.getvalue()).decode()
        images.append({
            "page": page_num + 1,
            "image_b64": img_b64
        })
    
    return images
```

### Structured Extraction Prompt

```python
VISION_PROMPT = """
Analisis dokumen hukum Indonesia ini. Ekstrak struktur lengkap:

1. BAB - Nomor (Romawi/Angka) dan Judul
2. Pasal - Nomor dan Isi lengkap
3. Ayat - Nomor dalam kurung dan Isi

Return dalam format JSON:
{
  "bab": {
    "nomor": "I",
    "judul": "KETENTUAN UMUM"
  },
  "pasal": [
    {
      "nomor": 1,
      "isi": "Dalam Undang-Undang ini yang dimaksud dengan...",
      "ayat": [
        {"nomor": 1, "isi": "..."},
        {"nomor": 2, "isi": "..."}
      ]
    }
  ]
}
"""
```

## Database Schema

See [DATABASE_SCHEMA.md](./DATABASE_SCHEMA.md) for complete schema documentation.

## Next Steps

- [ ] Implement vision-based parsing for better accuracy
- [ ] Add batch processing for multiple PDFs
- [ ] Implement caching for parsed results
- [ ] Add retry logic for failed parsing
- [ ] Support for different regulation types (UU, PP, Perpres, etc.)