#!/usr/bin/env python3
"""Compatibility entry point. Prefer the installed ``secure-qr`` command."""

import sys
from pathlib import Path

SOURCE_DIR = Path(__file__).resolve().parent / "src"
if SOURCE_DIR.is_dir():
    sys.path.insert(0, str(SOURCE_DIR))

from secure_qr.cli import main  # noqa: E402

if __name__ == "__main__":
    raise SystemExit(main())
