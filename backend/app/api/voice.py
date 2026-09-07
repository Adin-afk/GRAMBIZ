from fastapi import APIRouter, HTTPException, status
from fastapi.responses import Response
from pydantic import BaseModel, Field

from app.ai import elevenlabs_service

router = APIRouter(prefix="/api/voice", tags=["voice"])


class SpeakRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=2000)


@router.post("/speak")
def speak(payload: SpeakRequest):
    """
    Text-to-speech via ElevenLabs ("read aloud"). The caller just sends
    whatever text is on screen (already in the user's chosen language);
    ElevenLabs' multilingual model detects the language automatically.
    Returns raw MP3 audio bytes.
    """
    try:
        audio = elevenlabs_service.synthesize_speech(payload.text)
    except elevenlabs_service.VoiceUnavailableError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={"success": False, "error_code": "VOICE_UNAVAILABLE", "message": str(e)},
        )
    return Response(content=audio, media_type="audio/mpeg")


@router.get("/status")
def voice_status():
    """Lets the frontend know up-front whether to show the Listen button at all."""
    return {"configured": elevenlabs_service.is_configured()}
