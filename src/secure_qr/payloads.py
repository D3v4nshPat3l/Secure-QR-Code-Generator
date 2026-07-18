"""Payload builders and protocol-aware validation."""

from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path
from urllib.parse import quote, urlencode

from .errors import SecurityError
from .models import Payload, Sensitivity
from .security import (
    analyze_https_url,
    decimal_amount,
    ensure_payload_size,
    reject_unsafe_unicode,
    validate_plain_text,
)

PHONE_RE = re.compile(r"^\+?[1-9][0-9]{6,14}$")
EMAIL_RE = re.compile(r"^[A-Za-z0-9.!#$%&'*+/=?^_`{|}~-]+@[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?(?:\.[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?)+$")
UPI_RE = re.compile(r"^[A-Za-z0-9._-]{2,256}@[A-Za-z][A-Za-z0-9.-]{1,63}$")
HEX_PSK_RE = re.compile(r"^[0-9A-Fa-f]{64}$")
SHA256_RE = re.compile(r"^[0-9A-Fa-f]{64}$")


def _phone(value: str) -> str:
    normalized = reject_unsafe_unicode(value, field="phone number").replace(" ", "").replace("-", "")
    if not PHONE_RE.fullmatch(normalized):
        raise SecurityError("Phone number must contain 7 to 15 digits and may start with +.")
    return normalized


def _email(value: str) -> str:
    normalized = reject_unsafe_unicode(value, field="email address")
    if len(normalized) > 254 or not EMAIL_RE.fullmatch(normalized):
        raise SecurityError("Invalid email address.")
    return normalized


def text_payload(value: str, *, allow_uri_like: bool = False) -> Payload:
    return Payload("text", validate_plain_text(value, allow_uri_like=allow_uri_like))


def url_payload(value: str, *, dns_check: bool = True) -> Payload:
    analysis = analyze_https_url(value, dns_check=dns_check)
    return Payload("url", analysis.canonical_url, warnings=analysis.warnings)


def phone_payload(phone: str) -> Payload:
    number = _phone(phone)
    return Payload("phone", f"tel:{number}", Sensitivity.PERSONAL)


def sms_payload(phone: str, message: str) -> Payload:
    number = _phone(phone)
    body = validate_plain_text(message, allow_uri_like=True)
    data = f"sms:{number}?body={quote(body, safe='')}"
    ensure_payload_size(data)
    return Payload("sms", data, Sensitivity.PERSONAL)


def email_payload(address: str, subject: str = "", body: str = "") -> Payload:
    mailbox = _email(address)
    params: dict[str, str] = {}
    if subject:
        params["subject"] = validate_plain_text(subject, allow_uri_like=True)
    if body:
        params["body"] = validate_plain_text(body, allow_uri_like=True)
    data = f"mailto:{mailbox}" + ("?" + urlencode(params) if params else "")
    ensure_payload_size(data)
    return Payload("email", data, Sensitivity.PERSONAL)


def whatsapp_payload(phone: str, message: str = "") -> Payload:
    number = _phone(phone).lstrip("+")
    data = f"https://wa.me/{number}"
    if message:
        body = validate_plain_text(message, allow_uri_like=True)
        data += f"?text={quote(body, safe='')}"
    ensure_payload_size(data)
    return Payload("whatsapp", data, Sensitivity.PERSONAL)


def _wifi_escape(value: str) -> str:
    value = reject_unsafe_unicode(value, field="Wi-Fi value")
    for source, target in (("\\", "\\\\"), (";", "\\;"), (",", "\\,"), (":", "\\:"), ('"', '\\"')):
        value = value.replace(source, target)
    return value


def wifi_payload(ssid: str, password: str, security: str = "WPA", hidden: bool = False) -> Payload:
    raw_ssid = reject_unsafe_unicode(ssid, field="Wi-Fi SSID")
    if not raw_ssid or len(raw_ssid.encode("utf-8")) > 32:
        raise SecurityError("Wi-Fi SSID must be 1 to 32 UTF-8 bytes.")
    mode = reject_unsafe_unicode(security, field="Wi-Fi security").upper()
    if mode not in {"WPA", "WEP", "NOPASS"}:
        raise SecurityError("Wi-Fi security must be WPA, WEP, or nopass.")
    warnings: list[str] = []
    raw_password = reject_unsafe_unicode(password or "", field="Wi-Fi password")
    if mode == "NOPASS":
        if raw_password:
            warnings.append("Password ignored because Wi-Fi security is nopass.")
        raw_password = ""
    elif mode == "WPA":
        pass_bytes = len(raw_password.encode("utf-8"))
        if not (8 <= pass_bytes <= 63 or HEX_PSK_RE.fullmatch(raw_password)):
            raise SecurityError("WPA password must be 8–63 UTF-8 bytes or a 64-character hexadecimal PSK.")
    elif mode == "WEP":
        length = len(raw_password)
        if length in {10, 26, 58} and not re.fullmatch(r"[0-9A-Fa-f]+", raw_password):
            raise SecurityError("Hexadecimal WEP keys must contain hexadecimal characters only.")
        if length not in {5, 10, 13, 16, 26, 29, 58}:
            raise SecurityError("WEP key length is invalid or unusual.")

    escaped_ssid = _wifi_escape(raw_ssid)
    escaped_password = _wifi_escape(raw_password) if raw_password else ""
    hidden_value = "true" if hidden else "false"
    if mode == "NOPASS":
        data = f"WIFI:T:nopass;S:{escaped_ssid};H:{hidden_value};;"
        redacted = data
    else:
        data = f"WIFI:T:{mode};S:{escaped_ssid};P:{escaped_password};H:{hidden_value};;"
        redacted = f"WIFI:T:{mode};S:{escaped_ssid};P:********;H:{hidden_value};;"
    ensure_payload_size(data)
    return Payload("wifi", data, Sensitivity.SECRET, tuple(warnings), redacted)


def _vcard_escape(value: str) -> str:
    return reject_unsafe_unicode(value, field="vCard value").replace("\\", "\\\\").replace("\n", "\\n").replace(";", "\\;").replace(",", "\\,")


def vcard_payload(
    name: str,
    phone: str = "",
    email: str = "",
    company: str = "",
    website: str = "",
    title: str = "",
) -> Payload:
    full_name = _vcard_escape(name)
    if not full_name:
        raise SecurityError("Contact name cannot be empty.")
    lines = ["BEGIN:VCARD", "VERSION:3.0", f"FN:{full_name}", f"N:;{full_name};;;" ]
    if company:
        lines.append(f"ORG:{_vcard_escape(company)}")
    if title:
        lines.append(f"TITLE:{_vcard_escape(title)}")
    if phone:
        lines.append(f"TEL;TYPE=CELL:{_phone(phone)}")
    if email:
        lines.append(f"EMAIL;TYPE=INTERNET:{_email(email)}")
    warnings: list[str] = []
    if website:
        analysis = analyze_https_url(website)
        lines.append(f"URL:{analysis.canonical_url}")
        warnings.extend(analysis.warnings)
    lines.append("END:VCARD")
    data = "\r\n".join(lines)
    ensure_payload_size(data)
    return Payload("vcard", data, Sensitivity.PERSONAL, tuple(warnings))


def upi_payload(
    upi_id: str,
    receiver_name: str,
    amount: str = "",
    note: str = "",
    reference: str = "",
) -> Payload:
    identifier = reject_unsafe_unicode(upi_id, field="UPI ID")
    if not UPI_RE.fullmatch(identifier):
        raise SecurityError("Invalid UPI ID format.")
    name = validate_plain_text(receiver_name, allow_uri_like=True)
    params = {"pa": identifier, "pn": name, "cu": "INR"}
    if amount:
        params["am"] = decimal_amount(amount)
    if note:
        params["tn"] = validate_plain_text(note, allow_uri_like=True)
    if reference:
        params["tr"] = validate_plain_text(reference, allow_uri_like=True)
    data = "upi://pay?" + urlencode(params)
    ensure_payload_size(data)
    return Payload("upi", data, Sensitivity.FINANCIAL)


def geo_payload(latitude: str, longitude: str, label: str = "") -> Payload:
    try:
        lat = float(latitude)
        lon = float(longitude)
    except ValueError as exc:
        raise SecurityError("Latitude and longitude must be numeric.") from exc
    if not -90 <= lat <= 90 or not -180 <= lon <= 180:
        raise SecurityError("Latitude or longitude is outside its valid range.")
    data = f"geo:{lat:.6f},{lon:.6f}"
    if label:
        data += "?q=" + quote(validate_plain_text(label, allow_uri_like=True), safe="")
    return Payload("geo", data)


def calendar_payload(title: str, start: str, end: str, location: str = "", description: str = "") -> Payload:
    def parse_dt(value: str) -> datetime:
        try:
            return datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError as exc:
            raise SecurityError("Calendar timestamps must be ISO-8601 values.") from exc

    def serialize_dt(value: datetime) -> str:
        return value.strftime("%Y%m%dT%H%M%S") + ("Z" if value.tzinfo else "")

    start_dt = parse_dt(start)
    end_dt = parse_dt(end)
    try:
        valid_order = end_dt > start_dt
    except TypeError as exc:
        raise SecurityError("Calendar start and end must use compatible timezone forms.") from exc
    if not valid_order:
        raise SecurityError("Calendar end time must be after the start time.")
    lines = [
        "BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//Secure QR//EN", "BEGIN:VEVENT",
        f"SUMMARY:{_vcard_escape(title)}", f"DTSTART:{serialize_dt(start_dt)}",
        f"DTEND:{serialize_dt(end_dt)}",
    ]
    if location:
        lines.append(f"LOCATION:{_vcard_escape(location)}")
    if description:
        lines.append(f"DESCRIPTION:{_vcard_escape(description)}")
    lines += ["END:VEVENT", "END:VCALENDAR"]
    data = "\r\n".join(lines)
    ensure_payload_size(data)
    return Payload("calendar", data, Sensitivity.PERSONAL)


def json_payload(value: str) -> Payload:
    raw = reject_unsafe_unicode(value, field="JSON")
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise SecurityError(f"Invalid JSON: {exc.msg}.") from exc
    canonical = json.dumps(parsed, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    ensure_payload_size(canonical)
    return Payload("json", canonical, Sensitivity.PERSONAL)


def file_hash_payload(path: Path, sha256_hex: str) -> Payload:
    digest = reject_unsafe_unicode(sha256_hex, field="SHA-256 digest").lower()
    if not SHA256_RE.fullmatch(digest):
        raise SecurityError("SHA-256 digest must contain exactly 64 hexadecimal characters.")
    filename = _vcard_escape(path.name)
    data = f"urn:sha256:{digest}?name={quote(filename, safe='')}"
    return Payload("file-hash", data)
