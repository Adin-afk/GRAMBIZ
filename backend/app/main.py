import logging

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api import assessment, auth, businesses, financial, health, locations, market, users, voice
from app.config import get_settings

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
logger = logging.getLogger("grambiz")

settings = get_settings()

app = FastAPI(
    title="GramBiz API",
    description="AI-Driven Hyper-Local Business Advisory and Financial Structuring Assistant "
    "for Rural Micro-Entrepreneurs - Solapur District, Maharashtra.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    # Ensure a consistent structured error envelope even for exceptions that
    # weren't raised with the {success, error_code, message} shape already.
    detail = exc.detail
    if isinstance(detail, dict) and "success" in detail:
        body = detail
    else:
        body = {"success": False, "error_code": "ERROR", "message": str(detail)}
    logger.warning("HTTPException %s on %s: %s", exc.status_code, request.url.path, body.get("message"))
    return JSONResponse(status_code=exc.status_code, content=body)


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    # Never leak stack traces / internals to the client.
    logger.exception("Unhandled error on %s", request.url.path)
    return JSONResponse(
        status_code=500,
        content={"success": False, "error_code": "INTERNAL_ERROR", "message": "An unexpected error occurred."},
    )


app.include_router(health.router)
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(locations.router)
app.include_router(businesses.router)
app.include_router(market.router)
app.include_router(financial.router)
app.include_router(assessment.router)
app.include_router(voice.router)
