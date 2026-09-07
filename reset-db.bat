@echo off
REM GramBiz - reset the database (Windows)
REM WARNING: this permanently deletes all data in the Docker volume,
REM including any accounts or assessments you've created.

echo WARNING: this will permanently delete all database data.
set /p CONFIRM="Type YES to continue: "
if /I not "%CONFIRM%"=="YES" (
    echo Cancelled.
    pause
    exit /b 0
)

docker compose down -v
docker compose up --build -d

echo.
echo Database reset. Fresh demo data will be seeded automatically.
pause
