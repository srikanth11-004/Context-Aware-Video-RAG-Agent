@echo off
echo ========================================
echo YouTube Lecture Synthesizer - Setup
echo ========================================
echo.

echo [1/4] Creating virtual environment...
py -m venv venv
if errorlevel 1 (
    echo ERROR: Python not found! Please install Python from python.org
    pause
    exit /b 1
)

echo [2/4] Activating virtual environment...
call venv\Scripts\activate.bat

echo [3/4] Upgrading pip...
python -m pip install --upgrade pip

echo [4/4] Installing dependencies...
pip install -r requirements.txt

echo.
echo ========================================
echo Setup Complete!
echo ========================================
echo.3
echo Next steps:
echo 1. Copy .env.example to .env
echo 2. Add your Gemini API key to .env
echo 3. Run: streamlit run app.py
echo.
pause
