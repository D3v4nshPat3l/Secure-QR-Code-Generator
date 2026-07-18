"""Passive QR decoder and risk analyzer. It never opens decoded destinations."""

from __future__ import annotations

import ipaddress
import re
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

from .renderer import decode_qr_image
from .security import DANGEROUS_SCHEMES, URI_PREFIX_RE, analyze_https_url


@dataclass(frozen=True)
class RiskReport:
    payload: str
    kind: str
    risk: str
    findings: tuple[str, ...]


def analyze_payload(data: str) -> RiskReport:
    findings: list[str] = []
    kind = "text"
    risk = "low"
    lower = data.lower()

    if data.startswith("SQRS1:"):
        return RiskReport(data, "signed-envelope", "medium", ("Signature requires an explicit public-key verification step.",))
    if data.startswith("SQRE1:"):
        return RiskReport(data, "encrypted-envelope", "low", ("Encrypted payload; contents are not visible without the password.",))
    if lower.startswith("wifi:"):
        return RiskReport(data, "wifi", "high", ("Contains network connection parameters and may include a plaintext password.",))
    if lower.startswith("upi://"):
        query = parse_qs(urlsplit(data).query)
        recipient = query.get("pa", ["unknown"])[0]
        amount = query.get("am", ["payer editable"])[0]
        return RiskReport(data, "payment", "high", (f"UPI recipient: {recipient}", f"Amount: {amount}", "Verify the recipient in the payment app before authorization."))
    if lower.startswith(("tel:", "sms:", "mailto:")):
        return RiskReport(data, "action-uri", "medium", ("Scanning may start a phone, message, or email action.",))

    if URI_PREFIX_RE.match(data):
        scheme = urlsplit(data).scheme.lower()
        kind = "url" if scheme in {"http", "https"} else "uri"
        if scheme in DANGEROUS_SCHEMES:
            return RiskReport(data, kind, "critical", (f"Dangerous URI scheme: {scheme}",))
        if scheme == "http":
            findings.append("Unencrypted HTTP destination.")
            risk = "high"
        elif scheme == "https":
            try:
                analysis = analyze_https_url(data, dns_check=False)
                findings.append(f"Canonical hostname: {analysis.hostname_ascii}")
                if analysis.hostname_unicode.lower() != analysis.hostname_ascii.lower():
                    findings.append(f"Internationalized hostname: {analysis.hostname_unicode}")
                    risk = "medium"
            except Exception as exc:
                findings.append(f"Malformed or policy-violating HTTPS URL: {exc}")
                risk = "high"
        else:
            findings.append(f"Custom URI scheme: {scheme}")
            risk = "medium"

    if re.search(r"[A-Za-z0-9.-]+@[A-Za-z0-9.-]+", data) and kind in {"url", "uri"}:
        findings.append("Contains an @ character; inspect for hostname/userinfo confusion.")
        risk = "high"
    for token in re.findall(r"(?:\d{1,3}\.){3}\d{1,3}", data):
        try:
            if not ipaddress.ip_address(token).is_global:
                findings.append(f"References non-public IP address {token}.")
                risk = "high"
        except ValueError:
            pass
    if not findings:
        findings.append("No active URI action was recognized; still inspect the text before trusting it.")
    return RiskReport(data, kind, risk, tuple(findings))


def decode_and_analyze(path: Path) -> RiskReport:
    return analyze_payload(decode_qr_image(path))
