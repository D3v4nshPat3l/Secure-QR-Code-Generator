#!/usr/bin/env bash
set -euo pipefail

if [ ! -d "venv" ]; then
    echo "[-] Virtual environment not found."
    echo "    Run: bash install.sh"
    exit 1
fi

source venv/bin/activate
python secure_qr_generator.py "$@"
