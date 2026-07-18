"""Allow ``python -m secure_qr`` execution."""

from .cli import main

raise SystemExit(main())
