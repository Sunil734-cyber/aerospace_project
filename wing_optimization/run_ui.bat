@echo off
REM Aircraft Wing Optimization UI Launcher
echo.
echo ============================================
echo   Wing Optimization - Interactive UI
echo ============================================
echo.
echo Starting Streamlit server...
echo Opening browser at http://localhost:8501
echo.
echo Press Ctrl+C to stop the server
echo.

cd /d "%~dp0"
"c:/Users/sunil/OneDrive/Desktop/New folder (4)/.venv/Scripts/python.exe" -m streamlit run app.py

pause
