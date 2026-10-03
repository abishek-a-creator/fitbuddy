"""Shared Gemini helper: one place for the API key, model names and fallbacks.

Model names are configurable because Google retires models regularly
(Gemini 1.5 is already gone). The first model that answers wins.
"""
import logging
import os

from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger("fitbuddy.gemini")

# "Pro" tier  -> workout generation and plan updates
# "Flash" tier -> quick nutrition tips
PRO_MODELS = [
    os.getenv("GEMINI_PRO_MODEL", "gemini-pro-latest"),
    "gemini-3.1-pro-preview",
    "gemini-2.5-pro",
]
FLASH_MODELS = [
    os.getenv("GEMINI_FLASH_MODEL", "gemini-flash-latest"),
    "gemini-3-flash-preview",
    "gemini-2.5-flash",
]

_client = None


class GeminiUnavailable(Exception):
    """Raised when Gemini cannot be used; callers fall back to built-in content."""


def _get_client():
    global _client
    api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise GeminiUnavailable("GOOGLE_API_KEY is not set")
    if _client is None:
        try:
            from google import genai
        except ImportError as exc:
            raise GeminiUnavailable("google-genai package is not installed") from exc
        _client = genai.Client(api_key=api_key)
    return _client


def generate_text(prompt: str, tier: str = "pro") -> str:
    """Return Gemini's text answer or raise GeminiUnavailable."""
    client = _get_client()
    models = PRO_MODELS if tier == "pro" else FLASH_MODELS
    errors = []
    for model_name in dict.fromkeys(m for m in models if m):
        try:
            response = client.models.generate_content(model=model_name, contents=prompt)
            text = (response.text or "").strip()
            if text:
                return text
            errors.append(f"{model_name}: empty response")
        except Exception as exc:  # network, quota, retired model, blocked prompt...
            logger.warning("Gemini model %s failed: %s", model_name, exc)
            errors.append(f"{model_name}: {str(exc)[:80]}")
    raise GeminiUnavailable("; ".join(errors)[:300])
