"""Security primitives, normalization, URL analysis, and output safeguards."""

from __future__ import annotations

import base64
import ipaddress
import json
import os
import re
import secrets
import socket
import stat
import unicodedata
from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path
from typing import Any
from urllib.parse import SplitResult, urlsplit, urlunsplit

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey, Ed25519PublicKey
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt
from PIL import ImageColor

from .errors import SecurityError

MAX_PAYLOAD_BYTES = 2953  # Conservative byte cap for dense QR payloads.
URI_PREFIX_RE = re.compile(r"^[A-Za-z][A-Za-z0-9+.-]*:")
DOMAIN_LABEL_RE = re.compile(r"^[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?$")
FILENAME_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]{0,119}$")
BIDI_OR_FORMAT_CLASSES = {"Cf"}
DANGEROUS_SCHEMES = {
    "javascript", "data", "file", "vbscript", "intent", "market", "shell",
    "cmd", "powershell", "ms-excel", "ms-word", "ms-powerpoint",
}


@dataclass(frozen=True)
class UrlAnalysis:
    canonical_url: str
    hostname_unicode: str
    hostname_ascii: str
    resolved_addresses: tuple[str, ...]
    warnings: tuple[str, ...]


def reject_unsafe_unicode(value: str, *, field: str = "input") -> str:
    if value is None:
        raise SecurityError(f"{field.capitalize()} cannot be empty.")
    normalized = unicodedata.normalize("NFC", value)
    for char in normalized:
        codepoint = ord(char)
        if codepoint < 32 or codepoint == 127:
            raise SecurityError(f"{field.capitalize()} contains control characters.")
        if unicodedata.category(char) in BIDI_OR_FORMAT_CLASSES:
            raise SecurityError(
                f"{field.capitalize()} contains invisible or bidirectional formatting characters."
            )
    return normalized.strip()


def ensure_payload_size(value: str, max_bytes: int = MAX_PAYLOAD_BYTES) -> None:
    size = len(value.encode("utf-8"))
    if size > max_bytes:
        raise SecurityError(f"Payload is {size} bytes; maximum allowed is {max_bytes} bytes.")


def is_non_public_ip(address: str) -> bool:
    ip = ipaddress.ip_address(address.strip("[]"))
    return not ip.is_global


def _validate_hostname(hostname: str) -> tuple[str, str]:
    unicode_host = reject_unsafe_unicode(hostname, field="hostname").rstrip(".")
    if not unicode_host or any(c.isspace() for c in unicode_host) or "\\" in unicode_host:
        raise SecurityError("Hostname contains invalid whitespace or separators.")

    try:
        ip = ipaddress.ip_address(unicode_host.strip("[]"))
    except ValueError:
        try:
            ascii_host = unicode_host.encode("idna").decode("ascii").lower()
        except UnicodeError as exc:
            raise SecurityError("Hostname cannot be converted to IDNA safely.") from exc
        if len(ascii_host) > 253 or "." not in ascii_host:
            raise SecurityError("URL must contain a valid public domain.")
        labels = ascii_host.split(".")
        if any(not DOMAIN_LABEL_RE.fullmatch(label) for label in labels):
            raise SecurityError("Hostname contains an invalid DNS label.")
        return unicode_host, ascii_host
    else:
        if not ip.is_global:
            raise SecurityError("Local, private, reserved, and non-public IP addresses are blocked.")
        return unicode_host, ip.compressed


def analyze_https_url(value: str, *, dns_check: bool = True) -> UrlAnalysis:
    raw = reject_unsafe_unicode(value, field="URL")
    if not raw:
        raise SecurityError("URL cannot be empty.")
    if any(c.isspace() for c in raw) or "\\" in raw:
        raise SecurityError("URL cannot contain whitespace or backslashes.")
    if not URI_PREFIX_RE.match(raw):
        raw = "https://" + raw

    parsed: SplitResult = urlsplit(raw)
    scheme = parsed.scheme.lower()
    if scheme in DANGEROUS_SCHEMES:
        raise SecurityError(f"Dangerous URI scheme blocked: {scheme}")
    if scheme != "https":
        raise SecurityError("Only HTTPS URLs are allowed.")
    if parsed.username is not None or parsed.password is not None:
        raise SecurityError("URLs containing embedded usernames or passwords are blocked.")
    if not parsed.hostname:
        raise SecurityError("URL is missing a hostname.")
    try:
        port = parsed.port
    except ValueError as exc:
        raise SecurityError("URL contains an invalid port.") from exc
    if port is not None and not 1 <= port <= 65535:
        raise SecurityError("URL port must be between 1 and 65535.")

    unicode_host, ascii_host = _validate_hostname(parsed.hostname)
    display_host = f"[{ascii_host}]" if ":" in ascii_host else ascii_host
    netloc = display_host + (f":{port}" if port is not None else "")
    canonical = urlunsplit(("https", netloc, parsed.path or "", parsed.query or "", ""))
    ensure_payload_size(canonical)

    addresses: list[str] = []
    warnings: list[str] = []
    if dns_check and not _looks_like_ip(ascii_host):
        try:
            infos = socket.getaddrinfo(ascii_host, port or 443, type=socket.SOCK_STREAM)
            addresses = sorted({info[4][0] for info in infos})
            blocked = [address for address in addresses if is_non_public_ip(address)]
            if blocked:
                raise SecurityError(
                    "Hostname currently resolves to a non-public address: " + ", ".join(blocked)
                )
        except socket.gaierror:
            warnings.append("DNS resolution failed; destination reachability was not verified.")
    if unicode_host.lower() != ascii_host.lower():
        warnings.append(f"Internationalized hostname canonicalized as {ascii_host}.")

    return UrlAnalysis(canonical, unicode_host, ascii_host, tuple(addresses), tuple(warnings))


def _looks_like_ip(host: str) -> bool:
    try:
        ipaddress.ip_address(host)
        return True
    except ValueError:
        return False


def validate_plain_text(value: str, *, allow_uri_like: bool = False) -> str:
    text = reject_unsafe_unicode(value, field="text")
    if not text:
        raise SecurityError("Text cannot be empty.")
    ensure_payload_size(text)
    if URI_PREFIX_RE.match(text) and not allow_uri_like:
        raise SecurityError(
            "Text resembles a URI/action payload. Select the matching QR type or use the explicit override."
        )
    return text


def validate_output_filename(filename: str | None, extension: str) -> str:
    ext = extension.lower().lstrip(".")
    if ext not in {"png", "svg"}:
        raise SecurityError("Output format must be PNG or SVG.")
    raw = (filename or "").strip()
    if not raw:
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        return f"qr_{stamp}_{secrets.token_hex(3)}.{ext}"
    path = Path(raw)
    if path.name != raw:
        raise SecurityError("Filename must not contain a directory path.")
    stem = path.stem if path.suffix.lower() in {".png", ".svg"} else raw
    if not FILENAME_RE.fullmatch(stem) or stem in {".", ".."}:
        raise SecurityError("Unsafe filename. Use letters, numbers, dot, underscore, or hyphen.")
    return f"{stem}.{ext}"


def resolve_output_path(
    *, output_dir: Path, filename: str | None, extension: str, overwrite: bool
) -> Path:
    output_dir = output_dir.expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    target = (output_dir / validate_output_filename(filename, extension)).resolve()
    if target.parent != output_dir:
        raise SecurityError("Resolved output path escaped the output directory.")
    if target.exists() and not overwrite:
        raise SecurityError(f"Output already exists: {target}. Use --overwrite to replace it.")
    return target


def parse_color(value: str, *, name: str) -> tuple[int, int, int]:
    try:
        rgb = ImageColor.getrgb(value)
    except (ValueError, TypeError) as exc:
        raise SecurityError(f"Invalid {name} color: {value!r}.") from exc
    if len(rgb) == 4:
        rgb = rgb[:3]
    return tuple(int(channel) for channel in rgb)


def _relative_luminance(rgb: tuple[int, int, int]) -> float:
    def channel(v: int) -> float:
        s = v / 255.0
        return s / 12.92 if s <= 0.04045 else ((s + 0.055) / 1.055) ** 2.4
    r, g, b = (channel(v) for v in rgb)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def validate_color_contrast(foreground: str, background: str, minimum: float = 4.5) -> float:
    fg = parse_color(foreground, name="foreground")
    bg = parse_color(background, name="background")
    l1, l2 = sorted((_relative_luminance(fg), _relative_luminance(bg)), reverse=True)
    ratio = (l1 + 0.05) / (l2 + 0.05)
    if ratio < minimum:
        raise SecurityError(
            f"QR color contrast is too low ({ratio:.2f}:1); minimum is {minimum:.2f}:1."
        )
    return ratio


def secure_file_permissions(path: Path) -> None:
    if os.name != "nt":
        path.chmod(stat.S_IRUSR | stat.S_IWUSR)


def canonical_json(data: dict[str, Any]) -> bytes:
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def generate_signing_keypair(private_path: Path, public_path: Path, *, overwrite: bool = False) -> None:
    if not overwrite and (private_path.exists() or public_path.exists()):
        raise SecurityError("Key file already exists. Use overwrite explicitly.")
    private_key = Ed25519PrivateKey.generate()
    public_key = private_key.public_key()
    private_path.write_bytes(private_key.private_bytes(
        serialization.Encoding.PEM,
        serialization.PrivateFormat.PKCS8,
        serialization.NoEncryption(),
    ))
    public_path.write_bytes(public_key.public_bytes(
        serialization.Encoding.PEM,
        serialization.PublicFormat.SubjectPublicKeyInfo,
    ))
    secure_file_permissions(private_path)


def sign_envelope(payload: str, private_key_path: Path, *, issuer: str = "", expires_at: str = "") -> str:
    if expires_at:
        try:
            expiry = datetime.fromisoformat(expires_at.replace("Z", "+00:00"))
        except ValueError as exc:
            raise SecurityError("Expiration must be an ISO-8601 timestamp.") from exc
        if expiry.tzinfo is None:
            expiry = expiry.replace(tzinfo=timezone.utc)
        if expiry <= datetime.now(timezone.utc):
            raise SecurityError("Expiration must be in the future.")
        expires_at = expiry.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")
    private_key = serialization.load_pem_private_key(private_key_path.read_bytes(), password=None)
    if not isinstance(private_key, Ed25519PrivateKey):
        raise SecurityError("Private key is not an Ed25519 key.")
    body: dict[str, Any] = {
        "v": 1,
        "alg": "Ed25519",
        "payload": payload,
        "issuer": reject_unsafe_unicode(issuer, field="issuer") if issuer else "",
        "issued_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "expires_at": expires_at,
        "nonce": secrets.token_urlsafe(12),
    }
    signature = private_key.sign(canonical_json(body))
    body["signature"] = base64.urlsafe_b64encode(signature).decode("ascii").rstrip("=")
    envelope = "SQRS1:" + base64.urlsafe_b64encode(canonical_json(body)).decode("ascii").rstrip("=")
    ensure_payload_size(envelope)
    return envelope


def verify_signed_envelope(value: str, public_key_path: Path) -> dict[str, Any]:
    if not value.startswith("SQRS1:"):
        raise SecurityError("Payload is not a signed SQRS1 envelope.")
    raw = _urlsafe_b64decode(value[6:])
    document = json.loads(raw)
    signature_b64 = document.pop("signature", None)
    if not signature_b64:
        raise SecurityError("Signed envelope has no signature.")
    public_key = serialization.load_pem_public_key(public_key_path.read_bytes())
    if not isinstance(public_key, Ed25519PublicKey):
        raise SecurityError("Public key is not an Ed25519 key.")
    try:
        public_key.verify(_urlsafe_b64decode(signature_b64), canonical_json(document))
    except Exception as exc:
        raise SecurityError("Signature verification failed.") from exc
    document["signature_valid"] = True
    expires_at = document.get("expires_at", "")
    if expires_at:
        try:
            expiry = datetime.fromisoformat(str(expires_at).replace("Z", "+00:00"))
            if expiry.tzinfo is None:
                expiry = expiry.replace(tzinfo=timezone.utc)
            document["expired"] = expiry <= datetime.now(timezone.utc)
        except ValueError as exc:
            raise SecurityError("Signed envelope contains an invalid expiration timestamp.") from exc
    else:
        document["expired"] = False
    return document


def encrypt_payload(payload: str, password: str) -> str:
    if len(password) < 12:
        raise SecurityError("Encryption password must be at least 12 characters.")
    salt = os.urandom(16)
    nonce = os.urandom(12)
    kdf = Scrypt(salt=salt, length=32, n=2**15, r=8, p=1)
    key = kdf.derive(password.encode("utf-8"))
    ciphertext = AESGCM(key).encrypt(nonce, payload.encode("utf-8"), b"SQRE1")
    envelope = {
        "v": 1,
        "alg": "AES-256-GCM",
        "kdf": "scrypt-N32768-r8-p1",
        "salt": _b64(salt),
        "nonce": _b64(nonce),
        "ciphertext": _b64(ciphertext),
    }
    result = "SQRE1:" + _b64(canonical_json(envelope))
    ensure_payload_size(result)
    return result


def decrypt_payload(value: str, password: str) -> str:
    if not value.startswith("SQRE1:"):
        raise SecurityError("Payload is not an encrypted SQRE1 envelope.")
    document = json.loads(_urlsafe_b64decode(value[6:]))
    salt = _urlsafe_b64decode(document["salt"])
    nonce = _urlsafe_b64decode(document["nonce"])
    ciphertext = _urlsafe_b64decode(document["ciphertext"])
    kdf = Scrypt(salt=salt, length=32, n=2**15, r=8, p=1)
    key = kdf.derive(password.encode("utf-8"))
    try:
        return AESGCM(key).decrypt(nonce, ciphertext, b"SQRE1").decode("utf-8")
    except Exception as exc:
        raise SecurityError("Decryption failed; password or payload is invalid.") from exc


def decimal_amount(value: str, *, maximum: Decimal = Decimal("10000000")) -> str:
    try:
        amount = Decimal(value)
    except Exception as exc:
        raise SecurityError("Amount must be a valid decimal number.") from exc
    if amount <= 0 or amount > maximum or amount.as_tuple().exponent < -2:
        raise SecurityError(f"Amount must be greater than 0, at most {maximum}, and use at most 2 decimals.")
    return format(amount.quantize(Decimal("0.01")).normalize(), "f")


def _b64(value: bytes) -> str:
    return base64.urlsafe_b64encode(value).decode("ascii").rstrip("=")


def _urlsafe_b64decode(value: str) -> bytes:
    return base64.urlsafe_b64decode(value + "=" * (-len(value) % 4))
