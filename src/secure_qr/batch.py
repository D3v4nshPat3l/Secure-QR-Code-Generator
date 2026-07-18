"""Batch QR generation from CSV or JSON."""

from __future__ import annotations

import csv
import json
from collections.abc import Iterable
from pathlib import Path
from typing import Any

from .errors import SecurityError
from .payloads import text_payload, url_payload, wifi_payload
from .renderer import render_qr

MAX_BATCH_ROWS = 1000


def _rows(path: Path) -> Iterable[dict[str, Any]]:
    if path.suffix.lower() == ".csv":
        with path.open(newline="", encoding="utf-8-sig") as handle:
            yield from csv.DictReader(handle)
    elif path.suffix.lower() == ".json":
        value = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(value, list) or not all(isinstance(item, dict) for item in value):
            raise SecurityError("Batch JSON must be an array of objects.")
        yield from value
    else:
        raise SecurityError("Batch input must be CSV or JSON.")


def generate_batch(input_path: Path, output_dir: Path, *, dry_run: bool = False) -> list[dict[str, Any]]:
    report: list[dict[str, Any]] = []
    seen_names: set[str] = set()
    for index, row in enumerate(_rows(input_path), start=1):
        if index > MAX_BATCH_ROWS:
            raise SecurityError(f"Batch exceeds maximum of {MAX_BATCH_ROWS} rows.")
        try:
            kind = str(row.get("type", "")).lower()
            filename = str(row.get("filename", f"row_{index}"))
            if filename in seen_names:
                raise SecurityError(f"Duplicate filename: {filename}")
            seen_names.add(filename)
            if kind == "text":
                payload = text_payload(str(row.get("text", "")), allow_uri_like=False)
            elif kind == "url":
                payload = url_payload(str(row.get("url", "")), dns_check=False)
            elif kind == "wifi":
                payload = wifi_payload(
                    str(row.get("ssid", "")), str(row.get("password", "")),
                    str(row.get("security", "WPA")), str(row.get("hidden", "false")).lower() in {"1", "true", "yes"},
                )
            else:
                raise SecurityError(f"Unsupported batch type: {kind}")
            output = None if dry_run else render_qr(payload, output_dir=output_dir, filename=filename)
            report.append({"row": index, "status": "ok", "type": kind, "output": str(output) if output else None})
        except Exception as exc:
            report.append({"row": index, "status": "error", "error": str(exc)})
    return report
