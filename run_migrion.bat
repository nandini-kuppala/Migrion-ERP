@echo off
echo ============================================
echo Starting Migrion - ERP Data Migration Platform
echo ============================================
echo.

REM Check if .env file exists
if not exist ".env" (
    echo WARNING: .env file not found!
    echo Please copy .env.example to .env and add your API keys
    echo.
    pause
    exit /b 1
)

echo Starting Streamlit application...
echo Open your browser to: http://localhost:8501
echo.
echo Press Ctrl+C to stop the server
echo.

streamlit run app.py

pause
