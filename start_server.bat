@echo off
chcp 65001 > nul
echo Starting Cafe Management System...

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Set Flask environment variables
set FLASK_APP=app.py
set FLASK_ENV=development
set FLASK_DEBUG=1

REM Open browser
start http://127.0.0.1:5000/

REM Start Flask server
echo Starting Flask server...
venv\Scripts\python.exe -m flask run

pause 