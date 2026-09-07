"""
Optional ElevenLabs text-to-speech integration ("read aloud").

Turns any UI or report text - a translated label, the Gemini-generated
plain-language explanation, a SWOT bullet - into spoken audio in whichever
language it's written in. Entirely optional and fails safe: every function
here raises only ``VoiceUnavailableError`` (never anything else) when
``ELEVENLABS_API_KEY`` is unset or the call fails, so nothing else in the
app depends on this being available.

Coverage note: ElevenLabs' multilingual model natively covers most major
Indian languages (Hindi, Marathi, Bengali, Gujarati, Kannada, Malayalam,
Tamil, Telugu, Punjabi, Urdu, Assamese, Sindhi, Nepali, and more) and
auto-detects the language directly from the input text, so callers never
need to pass a language code. A handful of the low-resource languages in
this app's locale list (e.g. Bodo, Dogri, Kashmiri, Konkani, Maithili,
Manipuri, Sanskrit, Santali) may not be supported yet - rather than
hard-coding a guess at exactly which do or don't work (that list changes
as ElevenLabs adds languages), this module simply forwards the request and
lets an unsupported language surface as a normal "voice unavailable"
response, which the frontend already handles with a clear message and a
browser-speech fallback.
"""
from __future__ import annotations

import logging

import httpx

from app.config import get_settings

logger = logging.getLogger("grambiz.ai.elevenlabs")

settings = get_settings()

_TTS_URL_TEMPLATE = "https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"

MAX_CHARACTERS = 2000  # keep requests small/cheap - report sections are short


class VoiceUnavailableError(Exception):
    """Raised whenever audio can't be produced for the given text/voice/model."""


def is_configured() -> bool:
    return bool(settings.ELEVENLABS_API_KEY)


def synthesize_speech(text: str) -> bytes:
    """
    Convert text to speech using ElevenLabs. The multilingual model
    auto-detects the language from the text itself.

    Returns raw MP3 bytes on success.
    Raises VoiceUnavailableError if ElevenLabs isn't configured, the text is
    empty, or the API rejects the request for any reason (unsupported
    language/script, rate limit, network failure, etc). Never raises
    anything else.
    """
    if not settings.ELEVENLABS_API_KEY:
        raise VoiceUnavailableError("ElevenLabs is not configured (ELEVENLABS_API_KEY unset).")

    text = (text or "").strip()
    if not text:
        raise VoiceUnavailableError("No text provided.")
    text = text[:MAX_CHARACTERS]

    url = _TTS_URL_TEMPLATE.format(voice_id=settings.ELEVENLABS_VOICE_ID)
    headers = {
        "xi-api-key": settings.ELEVENLABS_API_KEY,
        "Content-Type": "application/json",
        "Accept": "audio/mpeg",
    }
    payload = {
        "text": text,
        "model_id": settings.ELEVENLABS_MODEL,
        "voice_settings": {"stability": 0.5, "similarity_boost": 0.75},
    }

    try:
        response = httpx.post(url, headers=headers, json=payload, timeout=30.0)
    except httpx.HTTPError:
        logger.exception("Network error calling ElevenLabs.")
        raise VoiceUnavailableError("Could not reach the voice service.") from None

    if response.status_code != 200:
        logger.warning("ElevenLabs TTS failed (%s): %s", response.status_code, response.text[:300])
        raise VoiceUnavailableError(
            "Voice isn't available for this text right now (the language may not be supported yet)."
        )

    return response.content
