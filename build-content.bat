@echo off
cd /d "%~dp0"
python scripts\build.py || goto :error
python scripts\check.py || goto :error
echo.
echo Build and validation completed successfully.
pause
exit /b 0
:error
echo.
echo Build failed. Review the message above.
pause
exit /b 1
