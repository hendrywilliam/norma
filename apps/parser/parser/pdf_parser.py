"""
PDF Parser untuk mengekstrak konten dari PDF peraturan
"""

import pdfplumber
from typing import Dict, List, Optional, Any
import logging
from io import BytesIO
import re
import asyncio

logger = logging.getLogger(__name__)


async def parse_pdf(pdf_source: Any, extract_images: bool = False) -> Dict:
    """
    Parse PDF dan extract konten, metadata, dan text

    Args:
        pdf_source: PDF file path, bytes, atau file-like object
        extract_images: Apakah extract images (default False)

    Returns:
        Dictionary berisi:
        - text: Full text dari PDF
        - pages: List text per halaman
        - metadata: Metadata PDF
        - tables: List tables jika ada (opsional)
    """
    # Run pdfplumber in executor to avoid blocking event loop
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(None, _parse_pdf_sync, pdf_source, extract_images)
    return result


def _parse_pdf_sync(pdf_source: Any, extract_images: bool) -> Dict:
    """
    Synchronous PDF parsing function - run in executor
    """
    result = {
        "text": "",
        "pages": [],
        "metadata": {},
        "tables": [],
        "page_count": 0
    }

    try:
        # Buka PDF
        with pdfplumber.open(pdf_source) as pdf:
            # Extract metadata
            result["metadata"] = extract_metadata(pdf)
            result["page_count"] = len(pdf.pages)

            # Extract text per halaman
            full_text = []
            for page_num, page in enumerate(pdf.pages, 1):
                try:
                    # Extract text dari halaman
                    text = page.extract_text() or ""

                    # Clean text
                    text = clean_text(text)

                    # Extract tables jika ada
                    tables = []
                    if extract_images:
                        tables = page.extract_tables()
                        if tables:
                            result["tables"].extend([
                                {
                                    "page": page_num,
                                    "table": table
                                }
                                for table in tables
                            ])

                    # Simpan per halaman
                    page_data = {
                        "page": page_num,
                        "text": text,
                        "char_count": len(text)
                    }

                    result["pages"].append(page_data)
                    full_text.append(text)

                    logger.debug(f"Parsed page {page_num}/{len(pdf.pages)}")

                except Exception as e:
                    logger.warning(f"Error parsing page {page_num}: {e}")
                    result["pages"].append({
                        "page": page_num,
                        "text": "",
                        "error": str(e)
                    })

            # Gabungkan semua text
            result["text"] = "\n\n".join(full_text)

            logger.info(f"Successfully parsed PDF: {result['page_count']} pages, {len(result['text'])} chars")

    except Exception as e:
        logger.error(f"Error parsing PDF: {e}")
        raise

    return result


def extract_metadata(pdf: pdfplumber.PDF) -> Dict:
    """
    Extract metadata dari PDF

    Args:
        pdf: pdfplumber PDF object

    Returns:
        Dictionary metadata
    """
    metadata = {}

    try:
        if hasattr(pdf, 'metadata') and pdf.metadata:
            pdf_metadata = pdf.metadata

            metadata = {
                "title": pdf_metadata.get("Title", ""),
                "author": pdf_metadata.get("Author", ""),
                "subject": pdf_metadata.get("Subject", ""),
                "creator": pdf_metadata.get("Creator", ""),
                "producer": pdf_metadata.get("Producer", ""),
                "creation_date": str(pdf_metadata.get("CreationDate", "")),
                "modification_date": str(pdf_metadata.get("ModDate", "")),
            }

    except Exception as e:
        logger.warning(f"Error extracting metadata: {e}")

    return metadata


def clean_text(text: str) -> str:
    """
    Bersihkan text dari PDF

    Args:
        text: Raw text dari PDF

    Returns:
        Cleaned text
    """
    if not text:
        return ""

    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)

    # Remove page numbers di akhir/awal line
    text = re.sub(r'^\s*\d+\s*$', '', text, flags=re.MULTILINE)

    # Remove headers/footers yang terlalu pendek
    lines = text.split('\n')
    cleaned_lines = []

    for line in lines:
        stripped = line.strip()
        # Skip line yang terlalu pendek (mungkin page number atau noise)
        if len(stripped) > 3:
            cleaned_lines.append(stripped)

    return '\n'.join(cleaned_lines)


def extract_structure(text: str) -> Dict[str, List[str]]:
    """
    Extract structure dari text peraturan (bab, pasal, ayat)

    Args:
        text: Full text dari PDF

    Returns:
        Dictionary dengan sections:
        - bab: List bab
        - pasal: List pasal
        - ayat: List ayat
    """
    structure = {
        "bab": [],
        "pasal": [],
        "ayat": []
    }

    try:
        lines = text.split('\n')

        for line in lines:
            stripped = line.strip()

            # Detect Bab
            bab_match = re.match(r'^BAB\s+[IVXLC]+', stripped.upper())
            if bab_match:
                structure["bab"].append(stripped)

            # Detect Pasal
            pasal_match = re.match(r'^Pasal\s+\d+', stripped)
            if pasal_match:
                structure["pasal"].append(stripped)

            # Detect Ayat
            ayat_match = re.match(r'^\(\d+\)', stripped)
            if ayat_match:
                structure["ayat"].append(stripped)

    except Exception as e:
        logger.warning(f"Error extracting structure: {e}")

    return structure


def validate_pdf(pdf_source: Any) -> bool:
    """
    Validate apakah file adalah PDF valid

    Args:
        pdf_source: PDF file path, bytes, atau file-like object

    Returns:
        True jika valid, False jika tidak
    """
    try:
        with pdfplumber.open(pdf_source) as pdf:
            # Cek apakah ada halaman
            if len(pdf.pages) == 0:
                logger.warning("PDF has no pages")
                return False

            # Cek apakah bisa extract text dari halaman pertama
            first_page_text = pdf.pages[0].extract_text()
            if not first_page_text:
                logger.warning("Cannot extract text from first page")
                return False

        return True

    except Exception as e:
        logger.error(f"PDF validation failed: {e}")
        return False


async def parse_pdf_from_url(url: str, download_func: callable) -> Dict:
    """
    Download dan parse PDF dari URL

    Args:
        url: URL PDF
        download_func: Function untuk download PDF (harus return bytes)

    Returns:
        Dictionary hasil parsing
    """
    try:
        logger.info(f"Downloading PDF from {url}")

        # Download PDF
        pdf_bytes = await download_func(url)

        if not pdf_bytes:
            raise ValueError("Failed to download PDF")

        # Validate PDF
        if not validate_pdf(BytesIO(pdf_bytes)):
            raise ValueError("Invalid PDF file")

        # Parse PDF
        result = await parse_pdf(BytesIO(pdf_bytes))

        # Add source URL ke result
        result["source_url"] = url

        return result

    except Exception as e:
        logger.error(f"Error parsing PDF from URL {url}: {e}")
        raise


async def parse_pdf_from_bytes(pdf_bytes: bytes) -> Dict:
    """
    Parse PDF dari bytes

    Args:
        pdf_bytes: PDF content sebagai bytes

    Returns:
        Dictionary hasil parsing
    """
    try:
        if not pdf_bytes:
            raise ValueError("PDF bytes is empty")

        # Validate PDF
        if not validate_pdf(BytesIO(pdf_bytes)):
            raise ValueError("Invalid PDF file")

        # Parse PDF
        result = await parse_pdf(BytesIO(pdf_bytes))

        return result

    except Exception as e:
        logger.error(f"Error parsing PDF from bytes: {e}")
        raise


def extract_keywords(text: str, min_freq: int = 2) -> List[str]:
    """
    Extract keywords dari text peraturan

    Args:
        text: Full text dari PDF
        min_freq: Minimum frequency untuk keyword

    Returns:
        List keywords yang sering muncul
    """
    try:
        # Tokenize dan hitung frequency
        words = re.findall(r'\b[A-Za-z]{4,}\b', text.lower())

        # Filter stop words (Indonesian)
        stop_words = {
            'yang', 'dan', 'atau', 'untuk', 'dengan', 'dari', 'pada', 'ke',
            'sebagai', 'dalam', 'oleh', 'tersebut', 'ini', 'itu', 'adalah',
            'dapat', 'akan', 'telah', 'harus', 'wajib', 'semua', 'setiap'
        }

        filtered_words = [w for w in words if w not in stop_words]

        # Count frequency
        from collections import Counter
        word_counts = Counter(filtered_words)

        # Filter by min_freq
        keywords = [word for word, count in word_counts.items() if count >= min_freq]

        return sorted(keywords, key=lambda x: word_counts[x], reverse=True)

    except Exception as e:
        logger.warning(f"Error extracting keywords: {e}")
        return []
