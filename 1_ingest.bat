@echo off
echo.
echo ============================================================
echo   Step 1: Ingesting scripts into Vector DB...
echo ============================================================
python script_generator.py --ingest
echo.
pause
