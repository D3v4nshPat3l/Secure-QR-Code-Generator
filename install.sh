#!/usr/bin/env bash
set -euo pipefail

echo "[+] Secure QR Code Generator Linux/Kali setup"

if ! command -v python3 >/dev/null 2>&1; then
    echo "[-] python3 is not installed."
    echo "    Install it using: sudo apt update && sudo apt install -y python3"
    exit 1
fi

echo "[+] Python version:"
python3 --version

if ! python3 -m venv --help >/dev/null 2>&1; then
    echo "[!] python3-venv is missing."
    echo "[*] Trying to install python3-venv and python3-pip using apt."
    sudo apt update
    sudo apt install -y python3-venv python3-pip
fi

if [ ! -d "venv" ]; then
    echo "[+] Creating virtual environment: venv"
    python3 -m venv venv
fi

echo "[+] Activating virtual environment"
source venv/bin/activate

echo "[+] Upgrading pip"
python -m pip install --upgrade pip

echo "[+] Installing Python dependencies"
pip install -r requirements.txt

echo "[+] Running self-test"
python secure_qr_generator.py --self-test

echo
echo "[+] Setup completed successfully."
echo "[+] Run interactive mode:"
echo "    source venv/bin/activate"
echo "    python secure_qr_generator.py"
echo
echo "[+] Run CLI phone QR example:"
echo "    python secure_qr_generator.py --type phone --phone 9754485390 --filename phone_qr --yes"
