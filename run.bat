@echo off
setlocal

if not exist venv (
    echo [-] Virtual environment not found.
    echo     Run: install.bat
    exit /b 1
)

call venv\Scripts\activate.bat
python secure_qr_generator.py %*

endlocal
