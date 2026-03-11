"""
Scraper untuk peraturan.go.id
Scraping list peraturan, detail, dan download PDF
"""

import aiohttp
import asyncio
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
import logging
from urllib.parse import urljoin
import re

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
        List dictionary berisi info peraturan
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
        session: aiohttp ClientSession (optional)

    Returns:
        List dictionary info peraturan
    """
    results = []
    page = 1
    close_session = False

    # Create session if not provided
    if session is None:
        session = aiohttp.ClientSession()
        close_session = True

    try:
        while True:
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
                break

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
                        break
                else:
                    logger.info("Halaman terakhir tercapai")
                    break

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

        # Extract data dari detail page
        peraturan_data = {
            "url": url,
            "judul": extract_detail_text(soup, ['h1', 'h2'], ['judul-peraturan', 'title', 'main-title']),
            "nomor": extract_detail_text(soup, ['span', 'div'], ['nomor-peraturan', 'nomor', 'nomor_uu']),
            "tahun": extract_year_from_text(extract_detail_text(soup, ['span', 'div'], ['tahun-peraturan', 'tahun'])),
            "kategori": extract_detail_text(soup, ['span', 'div'], ['kategori-peraturan', 'kategori', 'jenis']),
            "tanggal_disahkan": extract_detail_text(soup, ['span', 'div'], ['tanggal-disahkan', 'tanggal_ditetapkan']),
            "tanggal_diundangkan": extract_detail_text(soup, ['span', 'div'], ['tanggal-diundangkan', 'tanggal_diundangkan']),
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
                for cell in cells:
                    link = cell.find('a')
                    if link:
                        detail_url = urljoin(BASE_URL, link.get('href', ''))
                        break
            else:
                return None
        else:
            judul = title_element.get_text(strip=True)
            detail_url = urljoin(BASE_URL, title_element.get('href', ''))

        # Extract nomor dan tahun
        nomor = ""
        tahun = None

        # Try to extract from various element types
        for span in item.find_all('span'):
            classes = ' '.join(span.get('class', []))
            text = span.get_text(strip=True)

            if 'nomor' in classes.lower():
                nomor = text
            elif 'tahun' in classes.lower():
                tahun = extract_year_from_text(text)

        # If not found, try regex on the whole item
        if not nomor or not tahun:
            item_text = item.get_text()
            nomor_match = re.search(r'(?:Nomor|No\.?\s*)\s*:?\s*(\d+)', item_text, re.IGNORECASE)
            if nomor_match and not nomor:
                nomor = nomor_match.group(1)

            if not tahun:
                tahun = extract_year_from_text(item_text)

        # Extract kategori
        kategori = ""
        for span in item.find_all('span'):
            classes = ' '.join(span.get('class', []))
            if 'kategori' in classes.lower() or 'jenis' in classes.lower():
                kategori = span.get_text(strip=True)
                break

        # Extract tanggal
        tanggal = ""
        for span in item.find_all('span'):
            classes = ' '.join(span.get('class', []))
            if 'tanggal' in classes.lower() or 'date' in classes.lower():
                tanggal = span.get_text(strip=True)
                break

        return {
            "judul": judul,
            "url": detail_url,
            "nomor": nomor,
            "tahun": tahun,
            "kategori": kategori,
            "tanggal_disahkan": tanggal,
            "pdf_url": None  # Akan diambil dari detail page
        }

    except Exception as e:
        logger.error(f"Error extracting peraturan info: {e}")
        return None


async def download_pdf(pdf_url: str, save_path: Optional[str] = None) -> bytes:
    """
    Download PDF file

    Args:
        pdf_url: URL PDF
        save_path: Path untuk menyimpan file (optional)

    Returns:
        PDF content sebagai bytes
    """
    async with aiohttp.ClientSession() as session:
        try:
            logger.info(f"Downloading PDF: {pdf_url}")

            async with session.get(pdf_url, headers=HEADERS, timeout=aiohttp.ClientTimeout(total=60)) as response:
                response.raise_for_status()
                pdf_content = await response.read()

                if save_path:
                    import aiofiles
                    async with aiofiles.open(save_path, 'wb') as f:
                        await f.write(pdf_content)
                    logger.info(f"PDF saved to: {save_path}")

                return pdf_content

        except aiohttp.ClientError as e:
            logger.error(f"Error downloading PDF {pdf_url}: {e}")
            raise


# Helper Functions
def extract_detail_text(soup: BeautifulSoup, tags: List[str], classes: List[str]) -> str:
    """Extract text dari element HTML dengan multiple class candidates"""
    for tag in tags:
        for class_name in classes:
            element = soup.find(tag, class_=class_name)
            if element:
                return element.get_text(strip=True)
    return ""


def extract_text(soup: BeautifulSoup, tag: Optional[str] = None, class_: Optional[str] = None) -> str:
    """Extract text dari element HTML"""
    try:
        if tag:
            element = soup.find(tag, class_=class_)
        else:
            element = soup.find(class_=class_)

        return element.get_text(strip=True) if element else ""
    except:
        return ""


def extract_year(soup: BeautifulSoup, class_: str) -> Optional[int]:
    """Extract tahun dan convert ke integer"""
    text = extract_text(soup, class_=class_)
    return extract_year_from_text(text)


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


def extract_date(soup: BeautifulSoup, class_: str) -> Optional[str]:
    """Extract tanggal dari element HTML"""
    return extract_text(soup, class_=class_)


def extract_pdf_url(soup: BeautifulSoup) -> Optional[str]:
    """Extract URL PDF dari detail page"""
    try:
        # Cari link PDF dengan multiple selectors
        for selector in ['a.download-pdf', 'a.pdf-link', 'a[data-type="pdf"]']:
            pdf_link = soup.select_one(selector)
            if pdf_link:
                href = pdf_link.get('href', '')
                if href:
                    return urljoin(BASE_URL, href)

        # Alternatif: cari link dengan text "Download"
        for a in soup.find_all('a'):
            text = a.get_text().lower()
            href = a.get('href', '').lower()
            if 'download' in text and 'pdf' in href:
                return urljoin(BASE_URL, a.get('href', ''))
            elif 'pdf' in text and 'unduh' in text:
                return urljoin(BASE_URL, a.get('href', ''))

        # Check for iframe with PDF
        iframe = soup.find('iframe')
        if iframe:
            src = iframe.get('src', '')
            if '.pdf' in src.lower():
                return urljoin(BASE_URL, src)

        return None
    except:
        return None
