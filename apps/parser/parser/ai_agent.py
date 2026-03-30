"""
AI Agent for PDF parsing using GLM-4.6V Vision Model
Processes PDF page images to extract structured legal document content
"""

import base64
import json
import logging
import aiohttp
import asyncio
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger(__name__)

GLM_46V_API_URL = "https://api.z.ai/api/paas/v4/chat/completions"


@dataclass
class GLMConfig:
    api_key: str
    model: str = "glm-4.6v"
    max_tokens: int = 4096
    temperature: float = 0.1
    timeout: int = 120


@dataclass
class ParsedPage:
    page_number: int
    bab_list: List[Dict[str, Any]]
    pasal_list: List[Dict[str, Any]]
    ayat_list: List[Dict[str, Any]]
    raw_text: str
    confidence: float


class GLM46VAgent:
    def __init__(self, config: GLMConfig):
        self.config = config
        self.api_url = GLM_46V_API_URL
        self._session: Optional[aiohttp.ClientSession] = None

    async def __aenter__(self):
        self._session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=self.config.timeout)
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self._session:
            await self._session.close()

    async def _ensure_session(self) -> aiohttp.ClientSession:
        if self._session is None:
            self._session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=self.config.timeout)
            )
        return self._session

    def _build_extraction_prompt(self, context: Dict[str, Any]) -> str:
        previous_babs = context.get("previous_babs", [])
        previous_pasals = context.get("previous_pasals", [])
        peraturan_info = context.get("peraturan_info", {})

        prompt = """You are a legal document parser for Indonesian regulations (peraturan). Analyze this PDF page image and extract the structure.

CRITICAL INSTRUCTIONS:
1. Extract ALL BAB (chapters) visible on this page
2. Extract ALL Pasal (articles) visible on this page
3. Extract ALL Ayat (paragraphs) visible on this page

EXTRACTION RULES:
- BAB format: "BAB I", "BAB II", etc. or "Bagian 1", "Bagian 2", etc.
- Each BAB has a judul_bab (title)
- Pasal format: "Pasal 1", "Pasal 2", etc.
- Each Pasal has konten_pasal (content)
- Ayat format: "(1)", "(2)", "(3)", etc. followed by content
- Each ayat has nomor_ayat and konten_ayat

CONTEXT FROM PREVIOUS PAGES:
"""
        if previous_babs:
            prompt += f"Previous BABs: {json.dumps(previous_babs[-3:], ensure_ascii=False)}\n"
        if previous_pasals:
            prompt += f"Previous Pasals: {json.dumps(previous_pasals[-3:], ensure_ascii=False)}\n"
        if peraturan_info:
            prompt += f"Regulation: {peraturan_info.get('judul', 'Unknown')} - {peraturan_info.get('nomor', 'Unknown')}\n"

        prompt += """
OUTPUT FORMAT (JSON ONLY, NO MARKDOWN):
{
    "bab_list": [
        {
            "nomor_bab": "I",
            "judul_bab": "KETENTUAN UMUM",
            "urutan": 1
        }
    ],
    "pasal_list": [
        {
            "nomor_pasal": "1",
            "judul_pasal": "",
            "konten_pasal": "Full pasal content...",
            "urutan": 1
        }
    ],
    "ayat_list": [
        {
            "nomor_ayat": "(1)",
            "konten_ayat": "Ayat content...",
            "nomor_pasal": "1",
            "urutan": 1
        }
    ],
    "raw_text": "All visible text from the page",
    "confidence": 0.95
}

IMPORTANT:
- Return ONLY valid JSON, no markdown formatting
- If nothing found, return empty arrays
- Extract ALL text visible in the image as raw_text
- Confidence should be between 0.0 and 1.0
- Maintain correct urutan (sequence) numbers
"""
        return prompt

    async def parse_page_image(
        self,
        image_base64: str,
        page_number: int,
        context: Optional[Dict[str, Any]] = None,
    ) -> ParsedPage:
        session = await self._ensure_session()

        prompt = self._build_extraction_prompt(context or {})

        logger.info(self.config.model)

        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/png;base64,{image_base64}"},
                    },
                ],
            }
        ]

        headers = {
            "Authorization": f"Bearer {self.config.api_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "model": self.config.model,
            "messages": messages,
            "max_tokens": self.config.max_tokens,
            "temperature": self.config.temperature,
        }

        try:
            async with session.post(self.api_url, headers=headers, json=payload) as response:
                if response.status != 200:
                    error_text = await response.text()
                    logger.error(f"GLM API error {response.status}: {error_text}")
                    raise Exception(f"GLM API error: {response.status} - {error_text}")

                result = await response.json()

            content = result.get("choices", [{}])[0].get("message", {}).get("content", "")

            parsed_data = self._parse_response(content)

            return ParsedPage(
                page_number=page_number,
                bab_list=parsed_data.get("bab_list", []),
                pasal_list=parsed_data.get("pasal_list", []),
                ayat_list=parsed_data.get("ayat_list", []),
                raw_text=parsed_data.get("raw_text", ""),
                confidence=parsed_data.get("confidence", 0.8),
            )

        except aiohttp.ClientError as e:
            logger.error(f"Network error parsing page {page_number}: {e}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error for page {page_number}: {e}")
            raise
        except Exception as e:
            logger.error(f"Error parsing page {page_number}: {e}")
            raise

    def _parse_response(self, content: str) -> Dict[str, Any]:
        content = content.strip()

        if content.startswith("```json"):
            content = content[7:]
        if content.startswith("```"):
            content = content[3:]
        if content.endswith("```"):
            content = content[:-3]

        content = content.strip()

        try:
            return json.loads(content)
        except json.JSONDecodeError:
            return self._extract_json_from_text(content)

    def _extract_json_from_text(self, text: str) -> Dict[str, Any]:
        start_idx = text.find("{")
        end_idx = text.rfind("}")

        if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
            json_str = text[start_idx : end_idx + 1]
            try:
                return json.loads(json_str)
            except json.JSONDecodeError:
                pass
        return {
            "bab_list": [],
            "pasal_list": [],
            "ayat_list": [],
            "raw_text": text,
            "confidence": 0.5,
        }

    async def parse_multiple_pages(
        self,
        pages: List[Dict[str, Any]],
        peraturan_info: Optional[Dict[str, Any]] = None,
        concurrency: int = 3,
    ) -> List[ParsedPage]:
        results = []
        previous_babs: List[Dict[str, Any]] = []
        previous_pasals: List[Dict[str, Any]] = []

        semaphore = asyncio.Semaphore(concurrency)

        async def parse_with_semaphore(page_data: Dict[str, Any], idx: int) -> ParsedPage:
            async with semaphore:
                context = {
                    "previous_babs": previous_babs.copy(),
                    "previous_pasals": previous_pasals.copy(),
                    "peraturan_info": peraturan_info or {},
                }

                result = await self.parse_page_image(
                    image_base64=page_data["image_b64"],
                    page_number=page_data["page"],
                    context=context,
                )

                previous_babs.extend(result.bab_list)
                previous_pasals.extend(result.pasal_list)

                return result

        tasks = [parse_with_semaphore(page, idx) for idx, page in enumerate(pages)]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        final_results = []
        for idx, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(Exception)
                logger.error(f"Failed to parse page {idx + 1}: {result}")
                final_results.append(
                    ParsedPage(
                        page_number=idx + 1,
                        bab_list=[],
                        pasal_list=[],
                        ayat_list=[],
                        raw_text="",
                        confidence=0.0,
                    )
                )
            else:
                final_results.append(result)

        return final_results


async def parse_pdf_with_ai(
    pdf_source: Any,
    api_key: str,
    peraturan_info: Optional[Dict[str, Any]] = None,
    model: str = "glm-4v-flash",
    concurrency: int = 3,
    scale: float = 2.0,
) -> Dict[str, Any]:
    """
    Parse PDF using AI vision model

    Args:
        pdf_source: PDF file path, bytes, or file-like object
        api_key: GLM API key
        peraturan_info: Info about the regulation (judul, nomor, etc.)
        model: Model to use (default: glm-4v-flash)
        concurrency: Number of concurrent page processing
        scale: Image scale factor

    Returns:
        Dictionary with bab_list, pasal_list, ayat_list
    """
    from parser.pdf_parser import pdf_pages_to_base64

    pages = pdf_pages_to_base64(pdf_source, scale=scale)

    if not pages:
        raise ValueError("No pages found in PDF")

    logger.info(f"Processing {len(pages)} pages with AI")

    config = GLMConfig(api_key=api_key, model=model)

    async with GLM46VAgent(config) as agent:
        parsed_pages = await agent.parse_multiple_pages(
            pages=pages,
            peraturan_info=peraturan_info,
            concurrency=concurrency,
        )

    all_babs: List[Dict[str, Any]] = []
    all_pasals: List[Dict[str, Any]] = []
    all_ayats: List[Dict[str, Any]] = []
    all_text: List[str] = []
    total_confidence = 0.0

    bab_urutan = 0
    pasal_urutan = 0
    ayat_urutan = 0

    seen_babs: set = set()
    seen_pasals: set = set()

    for page in parsed_pages:
        all_text.append(page.raw_text)
        total_confidence += page.confidence

        for bab in page.bab_list:
            bab_key = bab.get("nomor_bab", "")
            if bab_key and bab_key not in seen_babs:
                bab_urutan += 1
                seen_babs.add(bab_key)
                all_babs.append(
                    {
                        "nomor_bab": bab_key,
                        "judul_bab": bab.get("judul_bab", ""),
                        "urutan": bab_urutan,
                    }
                )

        for pasal in page.pasal_list:
            pasal_key = pasal.get("nomor_pasal", "")
            if pasal_key and pasal_key not in seen_pasals:
                pasal_urutan += 1
                seen_pasals.add(pasal_key)
                all_pasals.append(
                    {
                        "nomor_pasal": pasal_key,
                        "judul_pasal": pasal.get("judul_pasal", ""),
                        "konten_pasal": pasal.get("konten_pasal", ""),
                        "urutan": pasal_urutan,
                    }
                )

        for ayat in page.ayat_list:
            ayat_urutan += 1
            all_ayats.append(
                {
                    "nomor_ayat": ayat.get("nomor_ayat", ""),
                    "konten_ayat": ayat.get("konten_ayat", ""),
                    "nomor_pasal": ayat.get("nomor_pasal", ""),
                    "urutan": ayat_urutan,
                }
            )

    avg_confidence = total_confidence / len(parsed_pages) if parsed_pages else 0.0

    return {
        "bab_list": all_babs,
        "pasal_list": all_pasals,
        "ayat_list": all_ayats,
        "full_text": "\n\n".join(all_text),
        "page_count": len(pages),
        "confidence": avg_confidence,
        "pages_processed": len(parsed_pages),
    }
