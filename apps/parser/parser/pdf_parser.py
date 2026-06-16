"""
PDF Parser for extracting regulation structure (bab, pasal, ayat) from PDF
"""

import pdfplumber
import fitz
from PIL import Image
from typing import Dict, List, Optional, Any, Tuple, Union
import logging
from io import BytesIO
import re
import asyncio
import aiohttp
import json
import base64
import tempfile
import os
from pathlib import Path
from datetime import datetime

logger = logging.getLogger(__name__)


async def download_pdf(url: str, session: Optional[aiohttp.ClientSession] = None) -> bytes:
    """
    Download PDF from URL and return as bytes

    Args:
        url: PDF URL
        session: aiohttp ClientSession (optional)

    Returns:
        PDF content as bytes
    """
    close_session = False
    if session is None:
        session = aiohttp.ClientSession()
        close_session = True

    try:
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        async with session.get(
            url, headers=headers, timeout=aiohttp.ClientTimeout(total=60)
        ) as response:
            response.raise_for_status()
            pdf_bytes = await response.read()
            logger.info(f"Downloaded PDF: {len(pdf_bytes)} bytes from {url}")
            return pdf_bytes
    finally:
        if close_session and session:
            await session.close()


def pdf_pages_to_images(
    pdf_source: Union[str, bytes, Any],
    output_dir: Optional[str] = None,
    scale: float = 2.0,
    image_format: str = "png",
) -> Dict[str, Any]:
    """
    Convert PDF pages to images using PyMuPDF (fitz)

    Args:
        pdf_source: PDF file path, bytes, or file-like object
        output_dir: Directory to save images (default: temp directory)
        scale: Scale factor for image quality (default: 2.0 for better quality)
        image_format: Image format (png, jpeg, etc.)

    Returns:
        Dictionary containing:
        - output_dir: Path to directory containing images
        - images: List of image info dicts with page, path, width, height
        - total_pages: Total number of pages converted
    """
    if output_dir is None:
        output_dir = tempfile.mkdtemp(prefix="pdf_pages_")

    Path(output_dir).mkdir(parents=True, exist_ok=True)

    images_info = []

    try:
        if isinstance(pdf_source, bytes):
            doc = fitz.open(stream=pdf_source, filetype="pdf")
        elif isinstance(pdf_source, str) and os.path.exists(pdf_source):
            doc = fitz.open(pdf_source)
        else:
            doc = fitz.open(stream=pdf_source.read(), filetype="pdf")

        total_pages = len(doc)
        logger.info(f"Converting {total_pages} PDF pages to images in {output_dir}")

        for page_num in range(total_pages):
            page = doc[page_num]
            mat = fitz.Matrix(scale, scale)
            pix = page.get_pixmap(matrix=mat)

            filename = f"page_{page_num + 1:04d}.{image_format}"
            filepath = os.path.join(output_dir, filename)

            pix.save(filepath)

            images_info.append(
                {
                    "page": page_num + 1,
                    "path": filepath,
                    "filename": filename,
                    "width": pix.width,
                    "height": pix.height,
                    "format": image_format,
                }
            )

            logger.debug(f"Saved page {page_num + 1} to {filepath}")

        doc.close()

        logger.info(f"Successfully converted {total_pages} pages to {output_dir}")

        return {
            "output_dir": output_dir,
            "images": images_info,
            "total_pages": total_pages,
        }

    except Exception as e:
        logger.error(f"Error converting PDF to images: {e}")
        raise


def pdf_pages_to_base64(
    pdf_source: Union[str, bytes, Any], scale: float = 2.0, image_format: str = "png"
) -> List[Dict[str, Any]]:
    """
    Convert PDF pages to base64 encoded images (in-memory)

    Args:
        pdf_source: PDF file path, URL, bytes, or file-like object
        scale: Scale factor for image quality (default: 2.0)
        image_format: Image format (png, jpeg, etc.)

    Returns:
        List of dictionaries containing:
        - page: Page number (1-indexed)
        - image_b64: Base64 encoded image
        - width: Image width
        - height: Image height
    """
    pages = []

    try:
        if isinstance(pdf_source, bytes):
            doc = fitz.open(stream=pdf_source, filetype="pdf")
        elif isinstance(pdf_source, str):
            if pdf_source.startswith(("http://", "https://")):
                import requests

                response = requests.get(pdf_source, timeout=60)
                response.raise_for_status()
                pdf_bytes = response.content
                doc = fitz.open(stream=pdf_bytes, filetype="pdf")
                logger.info(f"Downloaded PDF from URL: {len(pdf_bytes)} bytes")
            elif os.path.exists(pdf_source):
                doc = fitz.open(pdf_source)
            else:
                raise ValueError(f"PDF source must be a valid file path or URL: {pdf_source}")
        else:
            doc = fitz.open(stream=pdf_source.read(), filetype="pdf")

        total_pages = len(doc)
        logger.info(f"Converting {total_pages} PDF pages to base64 images")

        for page_num in range(total_pages):
            page = doc[page_num]
            mat = fitz.Matrix(scale, scale)
            pix = page.get_pixmap(matrix=mat)

            img_bytes = pix.tobytes(image_format)
            img_b64 = base64.b64encode(img_bytes).decode("utf-8")

            pages.append(
                {
                    "page": page_num + 1,
                    "image_b64": img_b64,
                    "width": pix.width,
                    "height": pix.height,
                    "format": image_format,
                }
            )

            logger.debug(f"Converted page {page_num + 1} to base64")

        doc.close()

        logger.info(f"Successfully converted {total_pages} pages to base64")
        return pages

    except Exception as e:
        logger.error(f"Error converting PDF to base64: {e}")
        raise


async def parse_pdf(
    pdf_source: Union[str, bytes, Any],
    extract_images: bool = False,
    convert_to_images: bool = False,
    image_output_dir: Optional[str] = None,
    image_scale: float = 2.0,
) -> Dict:
    """
    Parse PDF and extract content, metadata, and regulation structure

    Args:
        pdf_source: PDF file path, URL, bytes, or file-like object
        extract_images: Whether to extract images (default False) - for tables
        convert_to_images: Whether to convert PDF pages to images (default False)
        image_output_dir: Directory for images (default: temp directory)
        image_scale: Scale factor for image quality (default: 2.0)

    Returns:
        Dictionary containing:
        - text: Full text from PDF
        - pages: List of text per page
        - metadata: PDF metadata
        - structure: Regulation structure (bab, pasal, ayat)
        - tables: List of tables if any (optional)
        - images: List of image info if convert_to_images=True
        - image_dir: Path to image directory if convert_to_images=True
    """
    # If pdf_source is a URL (string starting with http), download first
    if isinstance(pdf_source, str) and (
        pdf_source.startswith("http://") or pdf_source.startswith("https://")
    ):
        logger.info(f"Detected URL, downloading PDF from: {pdf_source}")
        pdf_bytes = await download_pdf(pdf_source)
        pdf_source = BytesIO(pdf_bytes)

    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(
        None,
        _parse_pdf_sync,
        pdf_source,
        extract_images,
        convert_to_images,
        image_output_dir,
        image_scale,
    )
    return result


def _parse_pdf_sync(
    pdf_source: Any,
    extract_images: bool,
    convert_to_images: bool,
    image_output_dir: Optional[str],
    image_scale: float,
) -> Dict:
    """
    Synchronous PDF parsing function - run in executor
    """
    result = {
        "text": "",
        "pages": [],
        "metadata": {},
        "structure": {"bab": [], "pasal": [], "ayat": []},
        "tables": [],
        "page_count": 0,
        "images": [],
        "image_dir": None,
    }

    try:
        # Convert PDF to images if requested
        if convert_to_images:
            logger.info("Converting PDF pages to images...")

            # Handle different input types
            if isinstance(pdf_source, bytes):
                pdf_bytes_input = pdf_source
            elif isinstance(pdf_source, str) and os.path.exists(pdf_source):
                with open(pdf_source, "rb") as f:
                    pdf_bytes_input = f.read()
            else:
                pdf_bytes_input = pdf_source.read()

            image_result = pdf_pages_to_images(
                pdf_bytes_input,
                output_dir=image_output_dir,
                scale=image_scale,
            )

            result["images"] = image_result["images"]
            result["image_dir"] = image_result["output_dir"]
            result["page_count"] = image_result["total_pages"]

            logger.info(
                f"Converted {len(result['images'])} pages to images in {result['image_dir']}"
            )

        # Parse PDF for text extraction
        pdf_input = pdf_source
        if convert_to_images and isinstance(pdf_source, bytes):
            # If already converted, use same bytes for text extraction
            pdf_input = BytesIO(pdf_source)
        elif convert_to_images and hasattr(pdf_source, "read"):
            # Reset stream if already read
            pdf_source.seek(0)
            pdf_input = pdf_source

        with pdfplumber.open(pdf_input) as pdf:
            # Extract metadata
            result["metadata"] = extract_metadata(pdf)
            if not convert_to_images:
                result["page_count"] = len(pdf.pages)

            # Extract text per page
            full_text = []
            for page_num, page in enumerate(pdf.pages, 1):
                try:
                    text = page.extract_text() or ""
                    text = clean_text(text)

                    # Extract tables if any
                    tables = []
                    if extract_images:
                        tables = page.extract_tables()
                        if tables:
                            result["tables"].extend(
                                [{"page": page_num, "table": table} for table in tables]
                            )

                    # Save per page
                    page_data = {"page": page_num, "text": text, "char_count": len(text)}

                    result["pages"].append(page_data)
                    full_text.append(text)

                    logger.debug(f"Parsed page {page_num}/{len(pdf.pages)}")

                except Exception as e:
                    logger.warning(f"Error parsing page {page_num}: {e}")
                    result["pages"].append({"page": page_num, "text": "", "error": str(e)})

            # Combine all text
            result["text"] = "\n\n".join(full_text)

            # Extract regulation structure
            result["structure"] = extract_peraturan_structure(full_text)

            logger.info(
                f"Successfully parsed PDF: {result['page_count']} pages, {len(result['text'])} chars"
            )
            logger.info(
                f"Extracted structure: {len(result['structure']['bab'])} bab, {len(result['structure']['pasal'])} pasal, {len(result['structure']['ayat'])} ayat"
            )

    except Exception as e:
        logger.error(f"Error parsing PDF: {e}")
        raise

    return result


def extract_metadata(pdf: pdfplumber.PDF) -> Dict:
    """
    Extract metadata from PDF

    Args:
        pdf: pdfplumber PDF object

    Returns:
        Metadata dictionary
    """
    metadata = {}

    try:
        if hasattr(pdf, "metadata") and pdf.metadata:
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
    Clean text from PDF

    Args:
        text: Raw text from PDF

    Returns:
        Cleaned text
    """
    if not text:
        return ""

    # Remove extra whitespace
    text = re.sub(r"\s+", " ", text)

    # Remove page numbers at end/start of line
    text = re.sub(r"^\s*\d+\s*$", "", text, flags=re.MULTILINE)

    # Remove headers/footers that are too short
    lines = text.split("\n")
    cleaned_lines = []

    for line in lines:
        stripped = line.strip()
        # Skip lines that are too short (possibly page number or noise)
        if len(stripped) > 3:
            cleaned_lines.append(stripped)

    return "\n".join(cleaned_lines)


def extract_peraturan_structure(text_lines: List[str]) -> Dict[str, List[Dict]]:
    """
    Extract regulation structure (bab, pasal, ayat) from text

    Args:
        text_lines: List of text per page

    Returns:
        Dictionary with structure:
        - bab: List of bab
        - pasal: List of pasal
        - ayat: List of ayat
    """
    full_text = "\n\n".join(text_lines)
    lines = full_text.split("\n")

    structure = {"bab": [], "pasal": [], "ayat": []}

    current_bab = None
    current_pasal = None
    bab_counter = 0
    pasal_counter = 0
    ayat_counter = 0

    for line_num, line in enumerate(lines, 1):
        stripped = line.strip()

        # Detect Bab (Roman numeral I, II, III, or number 1, 2, 3)
        bab_match = re.match(r"^(BAB|Bagian)\s+([IVXLC]+|\d+)", stripped, re.IGNORECASE)
        if bab_match:
            bab_type = bab_match.group(1).upper()
            bab_number = bab_match.group(2)

            # Bab title usually on the same or next line
            judul_bab = stripped
            if len(bab_number) < 5:
                # Look for title on the next line if not present yet
                if line_num < len(lines):
                    next_line = lines[line_num].strip()
                    if next_line and not re.match(r"^BAB|Bagian", next_line, re.IGNORECASE):
                        judul_bab += " " + next_line

            bab_counter += 1
            current_bab = {
                "nomor_bab": bab_number,
                "judul_bab": judul_bab.strip(),
                "urutan": bab_counter,
                "line_num": line_num,
            }
            structure["bab"].append(current_bab)
            logger.debug(f"Found bab {bab_counter}: {bab_number}")
            continue

        # Detect Pasal
        pasal_match = re.match(r"^Pasal\s+(\d+)", stripped)
        if pasal_match:
            pasal_number = pasal_match.group(1)

            # Pasal title usually on the same or next line
            judul_pasal = stripped
            if f"Pasal {pasal_number}" in judul_pasal:
                # Look for title on the next line
                if line_num < len(lines):
                    next_line = lines[line_num].strip()
                    if next_line and not re.match(r"^Pasal", next_line):
                        judul_pasal += " " + next_line

            pasal_counter += 1
            current_pasal = {
                "nomor_pasal": pasal_number,
                "judul_pasal": judul_pasal.strip().replace(f"Pasal {pasal_number}", "").strip(),
                "urutan": pasal_counter,
                "line_num": line_num,
                "bab_id": current_bab["nomor_bab"] if current_bab else None,
            }
            structure["pasal"].append(current_pasal)
            logger.debug(f"Found pasal {pasal_counter}: {pasal_number}")
            continue

        # Detect Ayat
        ayat_match = re.match(r"^\((\d+)\)", stripped)
        if ayat_match:
            ayat_number = ayat_match.group(1)

            ayat_counter += 1
            current_ayat = {
                "nomor_ayat": f"({ayat_number})",
                "konten_ayat": stripped.replace(f"({ayat_number})", "", 1).strip(),
                "urutan": ayat_counter,
                "line_num": line_num,
                "pasal_id": current_pasal["nomor_pasal"] if current_pasal else None,
            }
            structure["ayat"].append(current_ayat)
            logger.debug(f"Found ayat {ayat_counter}: ({ayat_number})")

    logger.info(
        f"Extracted structure: {len(structure['bab'])} bab, {len(structure['pasal'])} pasal, {len(structure['ayat'])} ayat"
    )
    return structure


def extract_peraturan_content_by_structure(
    text_lines: List[str], structure: Dict[str, List[Dict]]
) -> Dict[str, List[Dict]]:
    """
    Extract complete content for bab, pasal, and ayat based on structure

    Args:
        text_lines: List of text per page
        structure: Regulation structure (from extract_peraturan_structure)

    Returns:
        Dictionary with complete content for bab, pasal, and ayat
    """
    full_text = "\n\n".join(text_lines)
    lines = full_text.split("\n")

    result = {"bab": [], "pasal": [], "ayat": []}

    # Extract bab content
    for i, bab in enumerate(structure["bab"]):
        next_bab_line = (
            structure["bab"][i + 1]["line_num"] if i < len(structure["bab"]) - 1 else len(lines)
        )

        # Extract text from bab line to the next bab line
        bab_lines = lines[bab["line_num"] - 1 : next_bab_line - 1]
        bab_content = "\n".join(bab_lines)

        result["bab"].append({**bab, "konten_bab": bab_content, "char_count": len(bab_content)})

    # Extract pasal content
    for i, pasal in enumerate(structure["pasal"]):
        next_pasal_line = (
            structure["pasal"][i + 1]["line_num"] if i < len(structure["pasal"]) - 1 else len(lines)
        )

        # Extract text from pasal line to the next pasal line
        pasal_lines = lines[pasal["line_num"] - 1 : next_pasal_line - 1]
        pasal_content = "\n".join(pasal_lines)

        result["pasal"].append(
            {**pasal, "konten_pasal": pasal_content, "char_count": len(pasal_content)}
        )

    # Extract ayat content (already extracted in extract_peraturan_structure)
    result["ayat"] = structure["ayat"]

    return result


def validate_pdf(pdf_source: Any) -> bool:
    """
    Validate whether the file is a valid PDF

    Args:
        pdf_source: PDF file path, bytes, or file-like object

    Returns:
        True if valid, False otherwise
    """
    try:
        with pdfplumber.open(pdf_source) as pdf:
            # Check if there are any pages
            if len(pdf.pages) == 0:
                logger.warning("PDF has no pages")
                return False

            # Check if text can be extracted from first page
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
    Download and parse PDF from URL

    Args:
        url: PDF URL
        download_func: Function to download PDF (must return bytes)

    Returns:
        Parsing result dictionary
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

        # Add source URL to result
        result["source_url"] = url

        return result

    except Exception as e:
        logger.error(f"Error parsing PDF from URL {url}: {e}")
        raise


def extract_keywords(text: str, min_freq: int = 2) -> List[str]:
    """
    Extract keywords from regulation text

    Args:
        text: Full text from PDF
        min_freq: Minimum frequency for keyword

    Returns:
        List of frequently occurring keywords
    """
    try:
        # Tokenize and count frequency
        words = re.findall(r"\b[A-Za-z]{4,}\b", text.lower())

        # Filter stop words (Indonesian)
        stop_words = {
            "yang",
            "dan",
            "atau",
            "untuk",
            "dengan",
            "dari",
            "pada",
            "ke",
            "sebagai",
            "dalam",
            "oleh",
            "tersebut",
            "ini",
            "itu",
            "adalah",
            "dapat",
            "akan",
            "telah",
            "harus",
            "wajib",
            "semua",
            "setiap",
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


async def parse_peraturan_complete(
    pdf_source: Any,
    peraturan_id: str,
    extract_images: bool = False,
    convert_to_images: bool = False,
    image_output_dir: Optional[str] = None,
    image_scale: float = 2.0,
) -> Dict[str, Any]:
    """
    Parse regulation PDF completely with database-ready structure

    Args:
        pdf_source: PDF file path, bytes, or file-like object
        peraturan_id: Regulation ID from database
        extract_images: Whether to extract images/tables
        convert_to_images: Whether to convert PDF pages to images
        image_output_dir: Directory for images (default: temp directory)
        image_scale: Scale factor for image quality (default: 2.0)

    Returns:
        Dictionary containing data ready to be saved to the database
    """
    try:
        logger.info(f"Starting complete parsing for peraturan {peraturan_id}")

        # Parse PDF with all options
        parse_result = await parse_pdf(
            pdf_source,
            extract_images=extract_images,
            convert_to_images=convert_to_images,
            image_output_dir=image_output_dir,
            image_scale=image_scale,
        )

        logger.info(json.dumps(parse_result, default=str))

        # Extract regulation structure
        structure = parse_result["structure"]

        # Extract complete content for bab and pasal
        # pages is a list of dicts with key "text", extract text only
        page_texts = [page.get("text", "") for page in parse_result["pages"]]
        content_structure = extract_peraturan_content_by_structure(page_texts, structure)

        # Build database-ready result
        result = {
            "peraturan": {
                "id": peraturan_id,
                "parsed_at": None,  # Will be updated when saving to database
                "metadata": {
                    "page_count": parse_result["page_count"],
                    "char_count": len(parse_result["text"]),
                    "bab_count": len(content_structure["bab"]),
                    "pasal_count": len(content_structure["pasal"]),
                    "ayat_count": len(content_structure["ayat"]),
                    "keywords": extract_keywords(parse_result["text"]),
                    **parse_result["metadata"],
                },
            },
            "bab": content_structure["bab"],
            "pasal": content_structure["pasal"],
            "ayat": content_structure["ayat"],
            "parse_stats": {
                "total_pages": parse_result["page_count"],
                "total_chars": len(parse_result["text"]),
                "bab_count": len(content_structure["bab"]),
                "pasal_count": len(content_structure["pasal"]),
                "ayat_count": len(content_structure["ayat"]),
            },
        }

        # Add image info if any
        if convert_to_images and parse_result.get("images"):
            result["images"] = parse_result["images"]
            result["image_dir"] = parse_result.get("image_dir")

        logger.info(f"Complete parsing finished: {result['parse_stats']}")
        return result

    except Exception as e:
        logger.error(f"Error in complete parsing: {e}")
        raise


def format_peraturan_data_for_db(
    peraturan_data: Dict[str, Any],
    bab_data: List[Dict],
    pasal_data: List[Dict],
    ayat_data: List[Dict],
) -> Tuple[Dict, List[Dict], List[Dict], List[Dict]]:
    """
    Format regulation data for database storage

    Args:
        peraturan_data: Basic regulation data (from scraper)
        bab_data: List of bab data (from parser)
        pasal_data: List of pasal data (from parser)
        ayat_data: List of ayat data (from parser)

    Returns:
        Tuple (peraturan, bab_list, pasal_list, ayat_list) properly formatted
    """
    # Format peraturan data
    peraturan = {
        "id": peraturan_data.get("id"),
        "judul": peraturan_data.get("judul"),
        "nomor": peraturan_data.get("nomor"),
        "tahun": peraturan_data.get("tahun"),
        "kategori": peraturan_data.get("kategori"),
        "url": peraturan_data.get("url"),
        "pdf_url": peraturan_data.get("pdf_url"),
        "jenis_peraturan": peraturan_data.get("jenis_peraturan"),
        "pemrakarsa": peraturan_data.get("pemrakarsa"),
        "tentang": peraturan_data.get("tentang"),
        "tempat_penetapan": peraturan_data.get("tempat_penetapan"),
        "tanggal_ditetapkan": peraturan_data.get("tanggal_ditetapkan"),
        "pejabat_menetapkan": peraturan_data.get("pejabat_menetapkan"),
        "status_peraturan": peraturan_data.get("status_peraturan", "Berlaku"),
        "jumlah_dilihat": peraturan_data.get("jumlah_dilihat", 0),
        "jumlah_download": peraturan_data.get("jumlah_download", 0),
        "tanggal_disahkan": peraturan_data.get("tanggal_disahkan"),
        "tanggal_diundangkan": peraturan_data.get("tanggal_diundangkan"),
        "deskripsi": peraturan_data.get("deskripsi"),
        "metadata": peraturan_data.get("metadata", {}),
        "parsed_at": None,  # Will be updated when saving to database
    }

    # Format bab data
    bab_list = []
    for bab in bab_data:
        bab_list.append(
            {
                "peraturan_id": peraturan["id"],
                "nomor_bab": bab.get("nomor_bab"),
                "judul_bab": bab.get("judul_bab"),
                "urutan": bab.get("urutan"),
            }
        )

    # Format pasal data
    pasal_list = []
    for pasal in pasal_data:
        # Find bab_id based on nomor_bab
        bab_id = None
        for bab in bab_list:
            if bab["nomor_bab"] == pasal.get("bab_id"):
                # Bab_id will be generated after database insert
                break

        pasal_list.append(
            {
                "peraturan_id": peraturan["id"],
                "nomor_pasal": pasal.get("nomor_pasal"),
                "judul_pasal": pasal.get("judul_pasal"),
                "konten_pasal": pasal.get("konten_pasal"),
                "urutan": pasal.get("urutan"),
                "bab_id": bab_id,  # Will be updated after bab insert
                "metadata": {},
            }
        )

    # Format ayat data
    ayat_list = []
    for ayat in ayat_data:
        # Find pasal_id based on nomor_pasal
        pasal_id = None
        for pasal in pasal_list:
            if pasal["nomor_pasal"] == ayat.get("pasal_id"):
                # Pasal_id will be generated after database insert
                break

        ayat_list.append(
            {
                "pasal_id": pasal_id,  # Will be updated after pasal insert
                "nomor_ayat": ayat.get("nomor_ayat"),
                "konten_ayat": ayat.get("konten_ayat"),
                "urutan": ayat.get("urutan"),
                "metadata": {},
            }
        )

    return peraturan, bab_list, pasal_list, ayat_list
