@echo off
cd /d "%~dp0"
where py >nul 2>nul
if %errorlevel%==0 (
  py -3 scripts\build_content.py
) else (
  python scripts\build_content.py
)
if errorlevel 1 (
  echo.
  echo Build failed. Please check the error above.
) else (
  echo.
  echo Content updated successfully.
)
pause
