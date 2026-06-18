"""
Mistral OCR adapter for pipeline v3.

Ported verbatim from Aiveilix-pipline app/adapters/ocr.py.
"""

import asyncio
import base64
import logging
from dataclasses import dataclass
from typing import Protocol, runtime_checkable

import httpx
from tenacity import retry, retry_if_exception, stop_after_attempt, wait_exponential

from app.config import settings

logger = logging.getLogger(__name__)

# Transient HTTP statuses worth retrying. 4xx client errors are excluded.
_RETRYABLE_STATUS = {429, 500, 502, 503, 504}
_MAX_ATTEMPTS = 4
_OCR_TIMEOUT_SECONDS = 60


@dataclass
class OCRResult:
    page_number: int
    text: str
    raw_response: dict
    provider: str
    model: str


@runtime_checkable
class OCRProvider(Protocol):
    async def run(self, image_data: bytes, page_number: int) -> OCRResult: ...


def _is_retryable(exc: BaseException) -> bool:
    if isinstance(exc, (httpx.TimeoutException, httpx.ConnectError, httpx.ReadError, httpx.RemoteProtocolError)):
        return True
    if isinstance(exc, httpx.HTTPStatusError):
        return exc.response.status_code in _RETRYABLE_STATUS
    return False


class MistralOCRProvider:
    MODEL = "mistral-ocr-latest"

    def __init__(self, api_key: str) -> None:
        self._api_key = api_key

    @retry(
        retry=retry_if_exception(_is_retryable),
        stop=stop_after_attempt(_MAX_ATTEMPTS),
        wait=wait_exponential(multiplier=1, min=2, max=30),
        reraise=True,
    )
    def _call(self, payload: dict) -> dict:
        resp = httpx.post(
            "https://api.mistral.ai/v1/ocr",
            headers={"Authorization": f"Bearer {self._api_key}"},
            json=payload,
            timeout=_OCR_TIMEOUT_SECONDS,
        )
        resp.raise_for_status()
        return resp.json()

    async def run(self, image_data: bytes, page_number: int) -> OCRResult:
        b64 = base64.b64encode(image_data).decode()
        payload = {
            "model": self.MODEL,
            "document": {
                "type": "image_url",
                "image_url": f"data:image/png;base64,{b64}",
            },
        }
        logger.info("mistral_ocr_start model=%s page=%s image_bytes=%s", self.MODEL, page_number, len(image_data))

        try:
            raw = await asyncio.to_thread(self._call, payload)
        except httpx.HTTPStatusError as exc:
            logger.error("mistral_ocr_http_error page=%s status=%s", page_number, exc.response.status_code)
            raise RuntimeError(
                f"Mistral OCR failed for page {page_number}: HTTP {exc.response.status_code}"
            ) from exc
        except httpx.HTTPError as exc:
            logger.error("mistral_ocr_transport_error page=%s error=%s", page_number, exc)
            raise RuntimeError(f"Mistral OCR failed for page {page_number}: {exc}") from exc

        if not isinstance(raw, dict):
            raise RuntimeError(f"Mistral OCR returned a non-object response for page {page_number}")
        pages = raw.get("pages", [])
        if not isinstance(pages, list):
            pages = []
        text = "\n".join(p.get("markdown", "") for p in pages if isinstance(p, dict)).strip()
        logger.info("mistral_ocr_done page=%s page_count=%s chars=%s", page_number, len(pages), len(text))
        return OCRResult(
            page_number=page_number,
            text=text,
            raw_response=raw,
            provider="mistral",
            model=self.MODEL,
        )


def get_ocr_provider() -> OCRProvider | None:
    if not settings.mistral_api_key:
        return None
    return MistralOCRProvider(api_key=settings.mistral_api_key)
