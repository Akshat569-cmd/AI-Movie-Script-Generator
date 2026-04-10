@echo off
echo.
echo ============================================================
echo   AI Movie Script Generator - Auto Setup
echo ============================================================
echo.

:: Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found!
    echo Please install Python from https://python.org and re-run.
    pause
    exit /b 1
)

echo [1/4] Python found!
echo.
echo [2/4] Installing required packages...
pip install -r requirements.txt

echo.
echo [3/4] Installing latest HuggingFace package...
pip install langchain-huggingface

echo.
echo [4/4] All packages installed successfully!
echo.
echo ============================================================
echo   Setup Complete!
echo ============================================================
echo.
echo   NEXT STEPS:
echo   1. Double-click  1_ingest.bat
echo   2. Double-click  2_generate.bat
echo.
echo ============================================================
pause
