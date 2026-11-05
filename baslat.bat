@echo off
cd /d "%~dp0"
py -m venv .venv
if errorlevel 1 goto fail
.venv\Scripts\python -m pip install -U -r backend\requirements.txt
if errorlevel 1 goto fail
.venv\Scripts\python backend\server.py
:fail
pause
