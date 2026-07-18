#!/usr/bin/env bash
set -euo pipefail
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

if ! command -v python3 >/dev/null 2>&1; then
  echo "python3 is required. Install Python 3.10 or newer using your operating system package manager." >&2
  exit 1
fi
if ! python3 -m venv --help >/dev/null 2>&1; then
  echo "Python venv support is missing. Install the appropriate python3-venv package, then rerun this script." >&2
  exit 1
fi

python3 -m venv venv
# shellcheck disable=SC1091
source venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e .
python secure_qr_generator.py --type text --text "Secure QR self-test" --filename self_test --output-dir output --overwrite --yes

echo "Installation complete. Run: ./run.sh"
