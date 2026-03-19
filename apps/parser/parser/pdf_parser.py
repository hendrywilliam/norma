"""
PDF Parser untuk mengekstrak struktur peraturan (bab, pasal, ayat) dari PDF
"""

import pdfplumber
from typing import Dict, List, Optional, Any, Tuple
import logging
from io import BytesIO
import re
import asyncio

logger = logging.getLogger(__name__)


async def parse_pdf(pdf_source: Any, extract_images: bool = False) -> Dict:
    """
    Parse PDF dan extract konten, metadata, dan struktur peraturan

    Args:
        pdf_source: PDF file path, bytes, atau file-like object
        extract_images: Apakah extract images (default False)

    Returns:
        Dictionary berisi:
        - text: Full text dari PDF
        - pages: List text per halaman
        - metadata: Metadata PDF
        - structure: Struktur peraturan (bab, pasal, ayat)
        - tables: List tables jika ada (opsional)
    """
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
        "structure": {
            "bab": [],
            "pasal": [],
            "ayat": []
        },
        "tables": [],
        "page_count": 0
    }

    try:
        with pdfplumber.open(pdf_source) as pdf:
            # Extract metadata
            result["metadata"] = extract_metadata(pdf)
            result["page_count"] = len(pdf.pages)

            # Extract text per halaman
            full_text = []
            for page_num, page in enumerate(pdf.pages, 1):
                try:
                    text = page.extract_text() or ""
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

            # Extract structure peraturan
            result["structure"] = extract_peraturan_structure(full_text)

            logger.info(f"Successfully parsed PDF: {result['page_count']} pages, {len(result['text'])} chars")
            logger.info(f"Extracted structure: {len(result['structure']['bab'])} bab, {len(result['structure']['pasal'])} pasal, {len(result['structure']['ayat'])} ayat")

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


def extract_peraturan_structure(text_lines: List[str]) -> Dict[str, List[Dict]]:
    """
    Extract struktur peraturan (bab, pasal, ayat) dari text

    Args:
        text_lines: List text per halaman

    Returns:
        Dictionary dengan struktur:
        - bab: List bab
        - pasal: List pasal
        - ayat: List ayat
    """
    full_text = "\n\n".join(text_lines)
    lines = full_text.split('\n')

    structure = {
        "bab": [],
        "pasal": [],
        "ayat": []
    }

    current_bab = None
    current_pasal = None
    bab_counter = 0
    pasal_counter = 0
    ayat_counter = 0

    for line_num, line in enumerate(lines, 1):
        stripped = line.strip()

        # Detect Bab (Roman numeral I, II, III, atau angka 1, 2, 3)
        bab_match = re.match(r'^(BAB|Bagian)\s+([IVXLC]+|\d+)', stripped, re.IGNORECASE)
        if bab_match:
            bab_type = bab_match.group(1).upper()
            bab_number = bab_match.group(2)

            # Judul bab biasanya di line yang sama atau berikutnya
            judul_bab = stripped
            if bab_type in bab_number or len(bab_number) < 5:
                # Cari judul di line berikutnya jika belum ada
                if line_num < len(lines):
                    next_line = lines[line_num].strip()
                    if next_line and not re.match(r'^BAB|Bagian', next_line, re.IGNORECASE):
                        judul_bab += " " + next_line

            bab_counter += 1
            current_bab = {
                "nomor_bab": bab_number,
                "judul_bab": judul_bab.strip(),
                "urutan": bab_counter,
                "line_num": line_num
            }
            structure["bab"].append(current_bab)
            logger.debug(f"Found bab {bab_counter}: {bab_number}")
            continue

        # Detect Pasal
        pasal_match = re.match(r'^Pasal\s+(\d+)', stripped)
        if pasal_match:
            pasal_number = pasal_match.group(1)

            # Judul pasal biasanya di line yang sama atau berikutnya
            judul_pasal = stripped
            if f"Pasal {pasal_number}" in judul_pasal:
                # Cari judul di line berikutnya
                if line_num < len(lines):
                    next_line = lines[line_num].strip()
                    if next_line and not re.match(r'^Pasal', next_line):
                        judul_pasal += " " + next_line

            pasal_counter += 1
            current_pasal = {
                "nomor_pasal": pasal_number,
                "judul_pasal": judul_pasal.strip().replace(f"Pasal {pasal_number}", "").strip(),
                "urutan": pasal_counter,
                "line_num": line_num,
                "bab_id": current_bab["nomor_bab"] if current_bab else None
            }
            structure["pasal"].append(current_pasal)
            logger.debug(f"Found pasal {pasal_counter}: {pasal_number}")
            continue

        # Detect Ayat
        ayat_match = re.match(r'^\((\d+)\)', stripped)
        if ayat_match:
            ayat_number = ayat_match.group(1)

            ayat_counter += 1
            current_ayat = {
                "nomor_ayat": f"({ayat_number})",
                "konten_ayat": stripped.replace(f"({ayat_number})", "", 1).strip(),
                "urutan": ayat_counter,
                "line_num": line_num,
                "pasal_id": current_pasal["nomor_pasal"] if current_pasal else None
            }
            structure["ayat"].append(current_ayat)
            logger.debug(f"Found ayat {ayat_counter}: ({ayat_number})")

    logger.info(f"Extracted structure: {len(structure['bab'])} bab, {len(structure['pasal'])} pasal, {len(structure['ayat'])} ayat")
    return structure


def extract_peraturan_content_by_structure(
    text_lines: List[str],
    structure: Dict[str, List[Dict]]
) -> Dict[str, List[Dict]]:
    """
    Extract konten lengkap untuk bab, pasal, dan ayat berdasarkan struktur

    Args:
        text_lines: List text per halaman
        structure: Struktur peraturan (dari extract_peraturan_structure)

    Returns:
        Dictionary dengan konten lengkap untuk bab, pasal, dan ayat
    """
    full_text = "\n\n".join(text_lines)
    lines = full_text.split('\n')

    result = {
        "bab": [],
        "pasal": [],
        "ayat": []
    }

    # Extract konten bab
    for i, bab in enumerate(structure["bab"]):
        next_bab_line = structure["bab"][i + 1]["line_num"] if i < len(structure["bab"]) - 1 else len(lines)

        # Extract text dari line bab sampai line bab berikutnya
        bab_lines = lines[bab["line_num"] - 1:next_bab_line - 1]
        bab_content = "\n".join(bab_lines)

        result["bab"].append({
            **bab,
            "konten_bab": bab_content,
            "char_count": len(bab_content)
        })

    # Extract konten pasal
    for i, pasal in enumerate(structure["pasal"]):
        next_pasal_line = structure["pasal"][i + 1]["line_num"] if i < len(structure["pasal"]) - 1 else len(lines)

        # Extract text dari line pasal sampai line pasal berikutnya
        pasal_lines = lines[pasal["line_num"] - 1:next_pasal_line - 1]
        pasal_content = "\n".join(pasal_lines)

        result["pasal"].append({
            **pasal,
            "konten_pasal": pasal_content,
            "char_count": len(pasal_content)
        })

    # Extract konten ayat (sudah di extract di extract_peraturan_structure)
    result["ayat"] = structure["ayat"]

    return result


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


async def parse_peraturan_complete(
    pdf_source: Any,
    peraturan_id: str,
    extract_images: bool = False
) -> Dict[str, Any]:
    """
    Parse PDF peraturan secara lengkap dengan struktur database-ready

    Args:
        pdf_source: PDF file path, bytes, atau file-like object
        peraturan_id: ID peraturan dari database
        extract_images: Apakah extract images

    Returns:
        Dictionary berisi data yang sudah siap untuk disimpan ke database
    """
    try:
        logger.info(f"Starting complete parsing for peraturan {peraturan_id}")

        # Parse PDF dasar
        parse_result = await parse_pdf(pdf_source, extract_images)

        # Extract struktur peraturan
        structure = parse_result["structure"]

        # Extract konten lengkap untuk bab dan pasal
        content_structure = extract_peraturan_content_by_structure(
            parse_result["pages"],
            structure
        )

        # Build hasil yang database-ready
        result = {
            "peraturan": {
                "id": peraturan_id,
                "parsed_at": None,  # Akan di-update saat save ke database
                "metadata": {
                    "page_count": parse_result["page_count"],
                    "char_count": len(parse_result["text"]),
                    "bab_count": len(content_structure["bab"]),
                    "pasal_count": len(content_structure["pasal"]),
                    "ayat_count": len(content_structure["ayat"]),
                    "keywords": extract_keywords(parse_result["text"]),
                    **parse_result["metadata"]
                }
            },
            "bab": content_structure["bab"],
            "pasal": content_structure["pasal"],
            "ayat": content_structure["ayat"],
            "parse_stats": {
                "total_pages": parse_result["page_count"],
                "total_chars": len(parse_result["text"]),
                "bab_count": len(content_structure["bab"]),
                "pasal_count": len(content_structure["pasal"]),
                "ayat_count": len(content_structure["ayat"])
            }
        }

        logger.info(f"Complete parsing finished: {result['parse_stats']}")
        return result

    except Exception as e:
        logger.error(f"Error in complete parsing: {e}")
        raise


def format_peraturan_data_for_db(
    peraturan_data: Dict[str, Any],
    bab_data: List[Dict],
    pasal_data: List[Dict],
    ayat_data: List[Dict]
) -> Tuple[Dict, List[Dict], List[Dict], List[Dict]]:
    """
    Format data peraturan untuk disimpan ke database

    Args:
        peraturan_data: Data peraturan dasar (dari scraper)
        bab_data: List data bab (dari parser)
        pasal_data: List data pasal (dari parser)
        ayat_data: List data ayat (dari parser)

    Returns:
        Tuple (peraturan, bab_list, pasal_list, ayat_list) yang sudah diformat
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
        "parsed_at": None  # Akan di-update saat save ke database
    }

    # Format bab data
    bab_list = []
    for bab in bab_data:
        bab_list.append({
            "peraturan_id": peraturan["id"],
            "nomor_bab": bab.get("nomor_bab"),
            "judul_bab": bab.get("judul_bab"),
            "urutan": bab.get("urutan")
        })

    # Format pasal data
    pasal_list = []
    for pasal in pasal_data:
        # Find bab_id berdasarkan nomor_bab
        bab_id = None
        for bab in bab_list:
            if bab["nomor_bab"] == pasal.get("bab_id"):
                # Bab_id akan di-generate setelah insert ke database
                break

        pasal_list.append({
            "peraturan_id": peraturan["id"],
            "nomor_pasal": pasal.get("nomor_pasal"),
            "judul_pasal": pasal.get("judul_pasal"),
            "konten_pasal": pasal.get("konten_pasal"),
            "urutan": pasal.get("urutan"),
            "bab_id": bab_id,  # Akan di-update setelah insert bab
            "metadata": {}
        })

    # Format ayat data
    ayat_list = []
    for ayat in ayat_data:
        # Find pasal_id berdasarkan nomor_pasal
        pasal_id = None
        for pasal in pasal_list:
            if pasal["nomor_pasal"] == ayat.get("pasal_id"):
                # Pasal_id akan di-generate setelah insert ke database
                break

        ayat_list.append({
            "pasal_id": pasal_id,  # Akan di-update setelah insert pasal
            "nomor_ayat": ayat.get("nomor_ayat"),
            "konten_ayat": ayat.get("konten_ayat"),
            "urutan": ayat.get("urutan"),
            "metadata": {}
        })

    return peraturan, bab_list, pasal_list, ayat_list
