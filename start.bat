@echo off
REM GramBiz - start the application (Windows)

docker --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Docker was not found. Install Docker Desktop first.
    pause
    exit /b 1
)

echo Starting database, backend, and frontend...
docker compose up --build -d

echo.
echo Waiting for the backend to become healthy...
:waitloop
timeout /t 3 /nobreak >nul
docker compose ps backend | findstr /C:"healthy" >nul
if errorlevel 1 goto waitloop

echo.
echo Ready. Open http://localhost:5173 in your browser.
echo Demo login: demo@solapur-rural-demo.com / ChangeMe123!
echo.
echo Run stop.bat to stop the application.
pause
