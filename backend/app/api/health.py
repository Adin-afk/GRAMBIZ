from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.ai import elevenlabs_service, gemini_service
from app.config import get_settings
from app.database.session import get_db

router = APIRouter(tags=["health"])
settings = get_settings()


@router.get("/health")
def health():
    return {"status": "ok", "environment": settings.ENVIRONMENT, "demo_mode": settings.DEMO_MODE}


@router.get("/api/health/database")
def database_health(db: Session = Depends(get_db)):
    result = {"postgresql": False, "postgis": False, "pgvector": False}
    try:
        db.execute(text("SELECT 1"))
        result["postgresql"] = True
    except Exception:
        pass
    try:
        db.execute(text("SELECT postgis_version()"))
        result["postgis"] = True
    except Exception:
        pass
    try:
        db.execute(text("SELECT '[1,2,3]'::vector"))
        result["pgvector"] = True
    except Exception:
        pass
    return result


@router.get("/api/health/services")
def services_health():
    """Optional AI services must never crash the app when unavailable."""
    return {
        "ml_model": "not_trained",  # replaced by real status once app/ml/train.py has run
        "rag": "no_documents_ingested",
        "llm_provider": "configured" if settings.LLM_API_KEY else "not_configured",
        "gemini": "configured" if gemini_service.is_configured() else "not_configured",
        "gemini_last_error": gemini_service.get_last_error_code(),
        "elevenlabs_voice": "configured" if elevenlabs_service.is_configured() else "not_configured",
        "note": "The application remains fully functional (financial engine, GIS, deterministic "
        "scoring) even when these optional AI services are unavailable.",
    }
