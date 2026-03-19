"""
Scraper untuk peraturan.go.id
Scraping list peraturan, detail, dan download PDF
Mengambil data lengkap sesuai dengan database structure baru
"""

import aiohttp
import asyncio
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
import logging
from urllib.parse import urljoin
import re
from datetime import datetime

logger = logging.getLogger(__name__)

# Configuration
BASE_URL = "https://peraturan.go.id"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7",
}

# Rate limiting
REQUEST_DELAY = 1  # delay antar request dalam detik


async def scrape_peraturan(
    url: Optional[str] = None,
    category: Optional[str] = None,
    year: Optional[int] = None,
    limit: Optional[int] = None,
    session: Optional[aiohttp.ClientSession] = None
) -> List[Dict]:
    """
    Scrape list peraturan dari peraturan.go.id

    Args:
        url: URL spesifik untuk scraping (optional)
        category: Filter kategori (UU, PP, Perpres, dll)
        year: Filter tahun
        limit: Batas jumlah peraturan yang di-scrape
        session: aiohttp ClientSession (optional)

    Returns:
        List dictionary berisi info peraturan dengan field lengkap
    """
    if url:
        return await scrape_single_url(url, session)

    return await scrape_list_peraturan(category, year, limit, session)


async def scrape_list_peraturan(
    category: Optional[str] = None,
    year: Optional[int] = None,
    limit: Optional[int] = None,
    session: Optional[aiohttp.ClientSession] = None
) -> List[Dict]:
    """
    Scrape list peraturan berdasarkan filter

    Args:
        category: Kategori peraturan
        year: Tahun peraturan
        limit: Batas jumlah hasil
        session: aiohttp ClientSession

    Returns:
        List dictionary info peraturan
    """
    results = []
    page = 1
    close_session = False
    should_continue = True

    # Create session if not provided
    if session is None:
        session = aiohttp.ClientSession()
        close_session = True

    try:
        while should_continue:
            # Build URL untuk list peraturan
            search_url = f"{BASE_URL}/search"
            params = {
                "page": page
            }

            if category:
                params["jenis"] = category
            if year:
                params["tahun"] = str(year)

            logger.info(f"Scraping page {page}: category={category}, year={year}")

            # Make request
            async with session.get(search_url, params=params, headers=HEADERS, timeout=aiohttp.ClientTimeout(total=30)) as response:
                response.raise_for_status()
                html = await response.text()

            # Parse HTML
            soup = BeautifulSoup(html, 'html.parser')

            # Extract peraturan items - try multiple selectors for compatibility
            peraturan_items = (
                soup.find_all('div', class_='item-peraturan') or
                soup.find_all('div', class_='item') or
                soup.find_all('div', class_='list-item') or
                soup.find_all('article') or
                soup.find_all('div', class_='card')
            )

            # If still no items found, try to extract from table rows
            if not peraturan_items:
                table = soup.find('table')
                if table:
                    peraturan_items = table.find_all('tr')[1:]  # Skip header

            if not peraturan_items:
                logger.info(f"Tidak ada peraturan ditemukan di halaman {page}")
                # Try to get info from page structure
                logger.debug(f"Page HTML length: {len(html)}")
                logger.debug(f"Page content preview: {html[:500]}")
                should_continue = False
                continue

            # Extract data dari setiap item
            for item in peraturan_items:
                peraturan_data = extract_peraturan_info(item)
                if peraturan_data:
                    results.append(peraturan_data)

                    # Check limit
                    if limit and len(results) >= limit:
                        logger.info(f"Limit tercapai: {len(results)} peraturan")
                        return results

            # Check next page
            next_button = soup.find('a', class_='next-page')
            if not next_button or 'disabled' in next_button.get('class', []):
                # Also check for pagination indicators
                pagination = soup.find('div', class_='pagination') or soup.find('nav', {'aria-label': 'Pagination'})
                if pagination:
                    next_link = pagination.find('a', string=re.compile(r'Next|Selanjutnya'))
                    if not next_link:
                        logger.info("Halaman terakhir tercapai")
                        should_continue = False
                else:
                    logger.info("Halaman terakhir tercapai")
                    should_continue = False

            page += 1

            # Rate limiting
            await asyncio.sleep(REQUEST_DELAY)

    except Exception as e:
        logger.error(f"Error saat scraping: {e}")
    finally:
        if close_session and session:
            await session.close()

    return results


async def scrape_single_url(url: str, session: Optional[aiohttp.ClientSession] = None) -> List[Dict]:
    """
    Scrape peraturan dari URL spesifik

    Args:
        url: URL peraturan
        session: aiohttp ClientSession (optional)

    Returns:
        List dengan satu element (dictionary info peraturan)
    """
    close_session = False

    # Create session if not provided
    if session is None:
        session = aiohttp.ClientSession()
        close_session = True

    try:
        logger.info(f"Scraping single URL: {url}")

        async with session.get(url, headers=HEADERS, timeout=aiohttp.ClientTimeout(total=30)) as response:
            response.raise_for_status()
            html = await response.text()

        soup = BeautifulSoup(html, 'html.parser')

        # Extract data lengkap dari detail page
        peraturan_data = {
            "url": url,
            "judul": extract_detail_text(soup, ['h1', 'h2'], ['judul-peraturan', 'title', 'main-title']),
            "nomor": extract_detail_text(soup, ['span', 'div'], ['nomor-peraturan', 'nomor', 'nomor_uu']),
            "tahun": extract_year_from_text(extract_detail_text(soup, ['span', 'div'], ['tahun-peraturan', 'tahun'])),
            "kategori": extract_detail_text(soup, ['span', 'div'], ['kategori-peraturan', 'kategori', 'jenis']),
            # Field baru sesuai database
            "jenis_peraturan": extract_detail_text(soup, ['span', 'div'], ['jenis-peraturan', 'jenis']),
            "pemrakarsa": extract_detail_text(soup, ['span', 'div'], ['pemrakarsa', 'author']),
            "tentang": extract_detail_text(soup, ['span', 'div'], ['tentang', 'subject', 'topik']),
            "tempat_penetapan": extract_detail_text(soup, ['span', 'div'], ['tempat-penetapan', 'tempat', 'lokasi']),
            "tanggal_ditetapkan": parse_date(extract_detail_text(soup, ['span', 'div'], ['tanggal-ditetapkan', 'tanggal-tetap'])),
            "pejabat_menetapkan": extract_detail_text(soup, ['span', 'div'], ['pejabat-menetapkan', 'pejabat']),
            "status_peraturan": extract_detail_text(soup, ['span', 'div'], ['status-peraturan', 'status']) or "Berlaku",
            "jumlah_dilihat": extract_count_from_text(extract_detail_text(soup, ['span', 'div'], ['dilihat', 'view'])),
            "jumlah_download": extract_count_from_text(extract_detail_text(soup, ['span', 'div'], ['download', 'unduh'])),
            # Field lama
            "tanggal_disahkan": parse_date(extract_detail_text(soup, ['span', 'div'], ['tanggal-disahkan'])),
            "tanggal_diundangkan": parse_date(extract_detail_text(soup, ['span', 'div'], ['tanggal-diundangkan'])),
            "deskripsi": extract_detail_text(soup, ['div', 'p'], ['deskripsi', 'description', 'abstrak']),
            "pdf_url": extract_pdf_url(soup)
        }

        return [peraturan_data] if peraturan_data.get('judul') else []

    except Exception as e:
        logger.error(f"Error saat scraping URL {url}: {e}")
        return []
    finally:
        if close_session and session:
            await session.close()


async def download_pdf(pdf_url: str, save_path: Optional[str] = None) -> bytes:
    """
    Download PDF file

    Args:
        pdf_url: URL PDF
        save_path: Path untuk menyimpan file (optional)

    Returns:
        PDF content sebagai bytes
    """
    try:
        logger.info(f"Downloading PDF: {pdf_url}")

        async with aiohttp.ClientSession() as session:
            async with session.get(pdf_url, headers=HEADERS, timeout=aiohttp.ClientTimeout(total=60)) as response:
                response.raise_for_status()
                pdf_content = await response.read()

                if save_path:
                    with open(save_path, 'wb') as f:
                        f.write(pdf_content)
                    logger.info(f"PDF saved to: {save_path}")

                return pdf_content

    except Exception as e:
        logger.error(f"Error downloading PDF {pdf_url}: {e}")
        raise


def extract_peraturan_info(item: BeautifulSoup) -> Optional[Dict]:
    """
    Extract info peraturan dari item HTML

    Args:
        item: BeautifulSoup element untuk item peraturan

    Returns:
        Dictionary info peraturan atau None
    """
    try:
        # Extract judul dan URL - try multiple selectors
        title_element = (
            item.find('a', class_=lambda x: x and 'judul' in x.lower()) or
            item.find('a', class_=lambda x: x and 'title' in x.lower()) or
            item.find('h3').find('a') if item.find('h3') else
            item.find('h4').find('a') if item.find('h4') else
            item.find('a')
        )

        if not title_element:
            # Try to get from table cells
            cells = item.find_all(['td', 'th'])
            if len(cells) > 0:
                judul = cells[0].get_text(strip=True)
                detail_url = None
                # Find link in the item
                link = item.find('a')
                if link:
                    detail_url = urljoin(BASE_URL, link.get('href', ''))

                nomor = ""
                tahun = None
                kategori = ""
                pdf_url = None

                if len(cells) > 1:
                    nomor = cells[1].get_text(strip=True)
                if len(cells) > 2:
                    kategori = cells[2].get_text(strip=True)
                    tahun = extract_year_from_text(kategori)

                return {
                    "judul": judul,
                    "url": detail_url,
                    "nomor": nomor,
                    "tahun": tahun,
                    "kategori": kategori,
                    "pdf_url": pdf_url
                }
            return None

        judul = title_element.get_text(strip=True)
        detail_url = urljoin(BASE_URL, title_element.get('href', ''))

        # Extract nomor dan tahun
        nomor_element = item.find('span', class_='nomor')
        nomor = nomor_element.get_text(strip=True) if nomor_element else ""

        tahun_element = item.find('span', class_='tahun')
        tahun = extract_year_from_text(tahun_element.get_text(strip=True)) if tahun_element else None

        # Extract kategori
        kategori_element = item.find('span', class_='kategori')
        kategori = kategori_element.get_text(strip=True) if kategori_element else ""

        # Extract tanggal
        tanggal_element = item.find('span', class_='tanggal')
        tanggal = tanggal_element.get_text(strip=True) if tanggal_element else ""

        # Extract PDF URL
        pdf_link = item.find('a', href=True)
        pdf_url = None
        if pdf_link and 'pdf' in pdf_link.get('href', '').lower():
            pdf_url = urljoin(BASE_URL, pdf_link.get('href', ''))

        return {
            "judul": judul,
            "url": detail_url,
            "nomor": nomor,
            "tahun": tahun,
            "kategori": kategori,
            "tanggal_disahkan": tanggal,
            "pdf_url": pdf_url,
            # Default values untuk field baru (akan diupdate dari detail page)
            "jenis_peraturan": None,
            "pemrakarsa": None,
            "tentang": None,
            "tempat_penetapan": None,
            "tanggal_ditetapkan": None,
            "pejabat_menetapkan": None,
            "status_peraturan": "Berlaku",
            "jumlah_dilihat": 0,
            "jumlah_download": 0
        }

    except Exception as e:
        logger.error(f"Error extracting peraturan info: {e}")
        return None


# Helper Functions
def extract_detail_text(soup: BeautifulSoup, tags: List[str], classes: Optional[List[str]] = None) -> str:
    """Extract text dari element HTML dengan multiple selector options"""
    try:
        if classes:
            for tag in tags:
                for class_name in classes:
                    element = soup.find(tag, class_=class_name)
                    if element:
                        return element.get_text(strip=True)
        else:
            for tag in tags:
                element = soup.find(tag)
                if element:
                    return element.get_text(strip=True)
        return ""
    except:
        return ""


def extract_year_from_text(text: str) -> Optional[int]:
    """Extract tahun dari string text"""
    try:
        # Cari pattern tahun 4 digit
        match = re.search(r'\b(19|20)\d{2}\b', text)
        if match:
            return int(match.group())
        return None
    except:
        return None


def parse_date(date_string: str) -> Optional[str]:
    """Parse tanggal dari string format Indonesia ke ISO format"""
    try:
        if not date_string:
            return None

        # Remove whitespace
        date_string = date_string.strip()

        # Pattern tanggal Indonesia: 02 Januari 2026
        months_indo = {
            'januari': '01', 'februari': '02', 'maret': '03', 'april': '04',
            'mei': '05', 'juni': '06', 'juli': '07', 'agustus': '08',
            'september': '09', 'oktober': '10', 'november': '11', 'desember': '12'
        }

        # Match pattern: DD Bulan YYYY
        match = re.match(r'(\d{1,2})\s+([a-zA-Z]+)\s+(\d{4})', date_string, re.IGNORECASE)
        if match:
            day = match.group(1).zfill(2)
            month_name = match.group(2).lower()
            year = match.group(3)

            if month_name in months_indo:
                month = months_indo[month_name]
                return f"{year}-{month}-{day}"

        # Try parse as ISO date
        try:
            parsed_date = datetime.strptime(date_string, '%Y-%m-%d')
            return date_string
        except:
            pass

        return date_string  # Return original if can't parse
    except:
        return None


def extract_count_from_text(text: str) -> int:
    """Extract number dari text (untuk jumlah dilihat/download)"""
    try:
        if not text:
            return 0

        # Remove thousand separators
        text = text.replace('.', '').replace(',', '')

        # Extract number
        match = re.search(r'\d+', text)
        if match:
            return int(match.group())

        return 0
    except:
        return 0


def extract_pdf_url(soup: BeautifulSoup) -> Optional[str]:
    """Extract URL PDF dari detail page"""
    try:
        # Cari link PDF
        pdf_link = soup.find('a', class_='download-pdf')
        if pdf_link:
            return urljoin(BASE_URL, pdf_link.get('href', ''))

        # Alternatif: cari link dengan text "Download"
        for a in soup.find_all('a'):
            if 'download' in a.get_text().lower() and 'pdf' in a.get('href', '').lower():
                return urljoin(BASE_URL, a.get('href', ''))

        return None
    except:
        return None
