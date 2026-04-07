@echo off
echo Starting YouTube Lecture Synthesizer...
echo.

call venv\Scripts\activate.bat
streamlit run app.py
