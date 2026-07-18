@echo off
setlocal
cd /d "%~dp0"
where python >nul 2>nul
if errorlevel 1 (
  echo Python 3.10 or newer is required and must be available on PATH.
  exit /b 1
)
if not exist venv python -m venv venv
call venv\Scripts\activate.bat
python -m pip install --upgrade pip
python -m pip install -e .
python secure_qr_generator.py --type text --text "Secure QR self-test" --filename self_test --output-dir output --overwrite --yes
if errorlevel 1 exit /b 1
echo Installation complete. Run: run.bat
endlocal
