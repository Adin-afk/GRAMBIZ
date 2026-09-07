"""
Optional Gemini-powered explanation layer.

This module talks to Google's Gemini 2.5 Flash model to turn a completed
deterministic assessment (scores, competitor counts, financial engine
output, matched schemes) into:
  1. a short SWOT analysis, and
  2. a plain-language explanation a first-time entrepreneur can follow.

It is entirely optional and fails safe: every public function returns
``None`` (never raises) when ``GEMINI_API_KEY`` is unset or the API call
fails for any reason, so the financial engine, GIS scoring, and scheme
matching elsewhere in the app never depend on it being available.
"""
from __future__ import annotations

import json
import logging

from app.config import get_settings

logger = logging.getLogger("grambiz.ai.gemini")

settings = get_settings()

_model = None
_attempted_init = False

# Best-effort diagnostic of the most recent failure, so the API layer can
# tell the difference between "not configured for this deployment" and
# "was configured, but this particular call failed" without ever raising.
# Never contains secrets - only a short machine-readable code.
_last_error_code: str | None = None


def get_last_error_code() -> str | None:
    """Reason the most recent call returned None, if any. One of:
    'not_configured', 'client_init_failed', 'empty_response',
    'invalid_json', 'missing_keys', 'api_error', or None if the last
    call succeeded (or none has been made yet)."""
    return _last_error_code


def _strip_markdown_fence(text: str) -> str:
    """Defensively strip ```json ... ``` fences in case the model adds them
    despite being asked not to - keeps parsing robust for any input."""
    text = text.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[-1] if "\n" in text else text
        if text.endswith("```"):
            text = text[: -3]
        # Drop a leading language tag like "json" left over from the fence.
        first_line, _, rest = text.partition("\n")
        if first_line.strip().lower() in ("json", ""):
            text = rest
    return text.strip()


def _get_model():
    """Lazily configure and cache the Gemini client. Returns None if unset/unavailable."""
    global _model, _attempted_init
    if _attempted_init:
        return _model
    _attempted_init = True

    if not settings.GEMINI_API_KEY:
        logger.info("GEMINI_API_KEY not set; AI explanation layer is disabled.")
        global _last_error_code
        _last_error_code = "not_configured"
        return None

    try:
        import google.generativeai as genai

        genai.configure(api_key=settings.GEMINI_API_KEY)
        _model = genai.GenerativeModel(settings.GEMINI_MODEL)
        logger.info("Gemini client initialized with model %s", settings.GEMINI_MODEL)
    except Exception:
        logger.exception("Failed to initialize Gemini client; AI explanations disabled.")
        _model = None
        _last_error_code = "client_init_failed"

    return _model


def is_configured() -> bool:
    """True if a Gemini API key is set and the client initialized successfully."""
    return _get_model() is not None


_PROMPT_TEMPLATE = """You are a rural business advisor helping a first-time \
micro-entrepreneur in rural India. Using ONLY the structured data below \
(never invent numbers, competitor counts, or figures that aren't present), \
produce:

1. A SWOT analysis (strengths, weaknesses, opportunities, threats) as short \
   bullet phrases, 2-4 per category.
2. A 3-4 sentence plain-language explanation of this opportunity that \
   someone with limited financial literacy could understand.

Respond ONLY with valid JSON in exactly this shape, no markdown fences, no \
extra commentary:
{{
  "swot": {{
    "strengths": ["..."],
    "weaknesses": ["..."],
    "opportunities": ["..."],
    "threats": ["..."]
  }},
  "ai_explanation": "..."
}}

Data:
{data}
"""


def generate_assessment_explanation(context: dict) -> dict | None:
    """
    Ask Gemini 2.5 Flash for a SWOT analysis and plain-language explanation
    of a deterministic business assessment.

    ``context`` should be a JSON-serializable dict of the scores, competitor
    counts, financial figures, and matched schemes already computed by the
    deterministic engine (see app/api/assessment.py).

    Returns ``{"swot": {...}, "ai_explanation": "..."}`` on success, or
    ``None`` if the model isn't configured or the call fails for any reason.
    Never raises — callers can treat this as best-effort enrichment.
    """
    global _last_error_code

    model = _get_model()
    if model is None:
        # _last_error_code already set by _get_model() (not_configured /
        # client_init_failed).
        return None

    # json.dumps(..., default=str) already makes this robust to "any type of
    # input" - numpy scalars, Decimal, datetime, None, nested dicts/lists -
    # anything not natively JSON-serializable is coerced to its string form
    # instead of raising.
    try:
        prompt = _PROMPT_TEMPLATE.format(data=json.dumps(context, default=str))
    except Exception:
        logger.exception("Could not serialize assessment context for the AI explanation prompt.")
        _last_error_code = "api_error"
        return None

    try:
        response = model.generate_content(
            prompt,
            generation_config={
                "temperature": 0.4,
                "response_mime_type": "application/json",
            },
        )
    except Exception:
        logger.exception("Gemini call failed; continuing without AI explanation.")
        _last_error_code = "api_error"
        return None

    raw_text = (getattr(response, "text", None) or "").strip()
    if not raw_text:
        logger.warning("Gemini returned an empty response.")
        _last_error_code = "empty_response"
        return None

    # Be forgiving of the model wrapping its JSON in a markdown fence even
    # though the prompt asks it not to - this keeps the feature working for
    # any input rather than failing on a cosmetic formatting difference.
    cleaned_text = _strip_markdown_fence(raw_text)

    try:
        parsed = json.loads(cleaned_text)
    except json.JSONDecodeError:
        logger.warning("Gemini response was not valid JSON: %s", cleaned_text[:200])
        _last_error_code = "invalid_json"
        return None

    if not isinstance(parsed, dict) or "swot" not in parsed or "ai_explanation" not in parsed:
        logger.warning("Gemini response missing expected keys: %s", cleaned_text[:200])
        _last_error_code = "missing_keys"
        return None

    swot = parsed.get("swot")
    if not isinstance(swot, dict):
        logger.warning("Gemini response 'swot' was not an object: %s", cleaned_text[:200])
        _last_error_code = "missing_keys"
        return None

    # Normalize each SWOT category to a list of strings so any shape the
    # model returns (missing category, single string instead of a list,
    # non-string items) renders safely on the frontend instead of crashing.
    normalized_swot = {}
    for category in ("strengths", "weaknesses", "opportunities", "threats"):
        value = swot.get(category, [])
        if isinstance(value, str):
            value = [value]
        if not isinstance(value, list):
            value = []
        normalized_swot[category] = [str(item) for item in value if str(item).strip()]

    explanation = parsed.get("ai_explanation")
    if not isinstance(explanation, str) or not explanation.strip():
        logger.warning("Gemini response 'ai_explanation' was missing or empty.")
        _last_error_code = "missing_keys"
        return None

    _last_error_code = None
    return {"swot": normalized_swot, "ai_explanation": explanation.strip()}
