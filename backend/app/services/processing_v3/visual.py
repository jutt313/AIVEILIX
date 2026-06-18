"""
Visual understanding adapter for pipeline v3.

Uses Gemini 3.1 Flash-Lite to classify and describe cropped visual regions.
(Replaced the slower Kimi vision adapter — Gemini Flash-Lite is faster and
much cheaper per image.)
"""

import asyncio
import json
import logging
import re
from typing import Protocol, runtime_checkable

from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from app.config import settings

logger = logging.getLogger(__name__)

_MAX_ATTEMPTS = 3

_PROMPT = (
    "You are extracting data from an image cropped from a document page. "
    "Read the image carefully and return ONLY a JSON object with these fields:\n"
    "- asset_type: choose the single best fit:\n"
    "    photo            — a real-world photograph: places, scenery, buildings, "
    "people, food, objects. Use this for ordinary photos even if some signage or "
    "text is visible in the scene.\n"
    "    product_photo    — ONLY a product shot staged for sale or marketing "
    "(catalog/e-commerce style).\n"
    "    before_after     — a side-by-side before/after comparison.\n"
    "    review_screenshot— a screenshot of a review, rating, or testimonial.\n"
    "    chart            — a graph, bar/line/pie chart, or data visualization.\n"
    "    logo             — a brand logo.\n"
    "    icon             — a small UI/pictogram icon.\n"
    "    button           — a UI call-to-action button.\n"
    "    text_block       — an image that is PREDOMINANTLY text (a quote graphic, "
    "a screenshot of a text passage). Do NOT use this for a photo that merely "
    "contains some text — pick 'photo' for that.\n"
    "    unknown          — none of the above.\n"
    "- summary: a DETAILED, DATA-RICH description. Do NOT be vague.\n"
    "    * If asset_type is 'chart': state the chart type (bar/line/pie/etc), the "
    "title, the axis labels and units, EVERY series/category name, and the ACTUAL "
    "NUMERIC VALUE you can read for each bar/point/slice (read them off the axis, "
    "gridlines, and any data labels). Then state which series is highest/lowest and "
    "the clear takeaway (e.g. 'AIveilix 4.75 vs AnythingLLM 4.17 — AIveilix higher'). "
    "NEVER say bars are 'equal' or 'comparing values' without giving the numbers. "
    "If a value is not labeled, estimate it from the axis and prefix with '~'.\n"
    "    * Otherwise: describe what is actually shown in 1-3 specific sentences.\n"
    "- visible_text: ALL text visible in the image verbatim — every label, number, "
    "legend entry, axis tick and annotation (empty string if none).\n"
    "- confidence: your confidence score from 0.0 to 1.0\n\n"
    "Return only valid JSON, no markdown fences or other text."
)

_FALLBACK = {
    "asset_type": "unknown",
    "summary": "",
    "visible_text": "",
    "confidence": 0.0,
    "visual_error": True,
}


@runtime_checkable
class VisualUnderstandingProvider(Protocol):
    async def understand(self, image_data: bytes) -> dict: ...


class GeminiVisualUnderstandingAdapter:
    def __init__(self, api_key: str, model: str) -> None:
        self._api_key = api_key
        self._model_name = model

    def _model(self):
        import google.generativeai as genai

        genai.configure(api_key=self._api_key)
        return genai.GenerativeModel(self._model_name)

    @retry(
        retry=retry_if_exception_type(Exception),
        stop=stop_after_attempt(_MAX_ATTEMPTS),
        wait=wait_exponential(multiplier=1, min=2, max=20),
        reraise=True,
    )
    def _request(self, image_data: bytes) -> str:
        model = self._model()
        response = model.generate_content([
            _PROMPT,
            {"mime_type": "image/png", "data": image_data},
        ])
        return (response.text or "").strip()

    def _call(self, image_data: bytes) -> dict:
        raw = self._request(image_data)
        m = re.search(r"\{.*\}", raw, re.DOTALL)
        parsed = json.loads(m.group() if m else raw)
        if not isinstance(parsed, dict):
            raise ValueError(f"visual model returned non-object JSON: {type(parsed).__name__}")
        parsed.setdefault("provider", "gemini")
        parsed.setdefault("model", self._model_name)
        return parsed

    async def understand(self, image_data: bytes) -> dict:
        try:
            result = await asyncio.to_thread(self._call, image_data)
        except Exception as exc:
            logger.warning(
                "visual_understand_failed model=%s error_type=%s error=%s",
                self._model_name, type(exc).__name__, exc,
            )
            result = dict(_FALLBACK)
            result["provider"] = "gemini"
            result["model"] = self._model_name
        return result


class KimiVisualUnderstandingAdapter:
    """Visual understanding via Moonshot/Kimi vision models (OpenAI-compatible API)."""

    _TIMEOUT_SECONDS = 90

    def __init__(self, api_key: str, base_url: str, model: str) -> None:
        self._api_key = api_key
        self._base_url = base_url
        self._model_name = model

    @retry(
        retry=retry_if_exception_type(Exception),
        stop=stop_after_attempt(_MAX_ATTEMPTS),
        wait=wait_exponential(multiplier=1, min=2, max=20),
        reraise=True,
    )
    def _request(self, image_url: str) -> str:
        import openai

        client = openai.OpenAI(
            api_key=self._api_key,
            base_url=self._base_url,
            timeout=self._TIMEOUT_SECONDS,
        )
        response = client.chat.completions.create(
            model=self._model_name,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "image_url", "image_url": {"url": image_url}},
                        {"type": "text", "text": _PROMPT},
                    ],
                }
            ],
        )
        return (response.choices[0].message.content or "").strip()

    def _call(self, image_data: bytes) -> dict:
        import base64

        image_url = "data:image/png;base64," + base64.b64encode(image_data).decode("ascii")
        raw = self._request(image_url)
        m = re.search(r"\{.*\}", raw, re.DOTALL)
        parsed = json.loads(m.group() if m else raw)
        if not isinstance(parsed, dict):
            raise ValueError(f"visual model returned non-object JSON: {type(parsed).__name__}")
        parsed.setdefault("provider", "kimi")
        parsed.setdefault("model", self._model_name)
        return parsed

    async def understand(self, image_data: bytes) -> dict:
        try:
            result = await asyncio.to_thread(self._call, image_data)
        except Exception as exc:
            logger.warning(
                "visual_understand_failed provider=kimi model=%s error_type=%s error=%s",
                self._model_name, type(exc).__name__, exc,
            )
            result = dict(_FALLBACK)
            result["provider"] = "kimi"
            result["model"] = self._model_name
        return result


def get_visual_understanding_provider() -> VisualUnderstandingProvider | None:
    # Prefer Kimi/Moonshot vision when configured; fall back to Gemini.
    if settings.moonshot_api_key:
        return KimiVisualUnderstandingAdapter(
            api_key=settings.moonshot_api_key,
            base_url=settings.moonshot_base_url,
            model=settings.moonshot_visual_model,
        )
    if settings.gemini_api_key:
        return GeminiVisualUnderstandingAdapter(
            api_key=settings.gemini_api_key,
            model=settings.gemini_visual_model,
        )
    return None
