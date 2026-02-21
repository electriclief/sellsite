@echo off
echo ========================================
echo  Jim's Stuff for Sale - Static Server
echo ========================================
echo.
echo Starting local web server...
echo.
echo Open your browser to: http://localhost:8000
echo.
echo Press Ctrl+C to stop the server
echo ========================================
echo.
cd /d "%~dp0docs"
python -m http.server 8000
