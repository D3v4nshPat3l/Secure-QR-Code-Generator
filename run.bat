@echo off
setlocal
cd /d "%~dp0"
if not exist venv\Scripts\python.exe (
  echo Virtual environment not found. Run: install.bat
  exit /b 1
)
venv\Scripts\python.exe -m secure_qr.cli %*
endlocal
