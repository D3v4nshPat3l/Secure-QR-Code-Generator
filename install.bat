@echo off
setlocal

echo [+] Secure QR Code Generator Windows setup

where python >nul 2>nul
if %errorlevel% neq 0 (
    echo [-] Python is not installed or not added to PATH.
    echo     Install Python from https://www.python.org/downloads/
    echo     During installation, enable "Add python.exe to PATH".
    exit /b 1
)

echo [+] Python version:
python --version

if not exist venv (
    echo [+] Creating virtual environment: venv
    python -m venv venv
)

echo [+] Activating virtual environment
call venv\Scripts\activate.bat

echo [+] Upgrading pip
python -m pip install --upgrade pip

echo [+] Installing Python dependencies
pip install -r requirements.txt

echo [+] Running self-test
python secure_qr_generator.py --self-test

echo.
echo [+] Setup completed successfully.
echo [+] Run interactive mode:
echo     run.bat
echo.
echo [+] Run CLI phone QR example:
echo     run.bat --type phone --phone 9754485390 --filename phone_qr --yes

endlocal
