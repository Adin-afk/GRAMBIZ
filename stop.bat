@echo off
REM GramBiz - stop the application (Windows)
REM Data is preserved (Docker volume is not deleted).

docker compose down
echo.
echo Stopped. Your data is preserved - run start.bat to resume.
pause
