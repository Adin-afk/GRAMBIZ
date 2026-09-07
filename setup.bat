@echo off
REM GramBiz - first-time setup (Windows)
REM Builds all Docker images. Run start.bat afterwards to launch everything.

echo Checking Docker is available...
docker --version >nul 2>&1
if errorlevel 1 (
    echo.
    echo ERROR: Docker was not found. Install Docker Desktop first:
    echo https://www.docker.com/products/docker-desktop/
    echo.
    pause
    exit /b 1
)

if not exist ".env" (
    echo Creating .env from .env.example ...
    copy .env.example .env >nul
)

echo Building images - this can take a few minutes on first run...
docker compose build

echo.
echo Setup complete. Run start.bat to launch the application.
pause
