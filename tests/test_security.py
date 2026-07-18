from pathlib import Path

import pytest

from secure_qr.errors import SecurityError
from secure_qr.security import (
    analyze_https_url,
    decrypt_payload,
    encrypt_payload,
    generate_signing_keypair,
    sign_envelope,
    validate_color_contrast,
    validate_plain_text,
    verify_signed_envelope,
)


@pytest.mark.parametrize("value", ["http://example.com", "upi://pay?pa=x@y", "tel:+15551234567", "geo:1,2"])
def test_plain_text_rejects_uri_like_values(value: str) -> None:
    with pytest.raises(SecurityError):
        validate_plain_text(value)


@pytest.mark.parametrize("value", [
    "https://exa mple.com", "https://.com", "https://example..com",
    "https://example.com:abc", "https://user@example.com", "http://example.com",
    "https://127.0.0.1",
])
def test_url_rejects_parser_confusion(value: str) -> None:
    with pytest.raises(SecurityError):
        analyze_https_url(value, dns_check=False)


def test_url_canonicalizes_domain() -> None:
    result = analyze_https_url("EXAMPLE.COM/path#fragment", dns_check=False)
    assert result.canonical_url == "https://example.com/path"


def test_color_contrast_rejects_unreadable_qr() -> None:
    with pytest.raises(SecurityError):
        validate_color_contrast("white", "white")


def test_encryption_round_trip() -> None:
    value = encrypt_payload("secret", "correct horse battery staple")
    assert decrypt_payload(value, "correct horse battery staple") == "secret"
    with pytest.raises(SecurityError):
        decrypt_payload(value, "wrong password indeed")


def test_signature_round_trip(tmp_path: Path) -> None:
    private = tmp_path / "private.pem"
    public = tmp_path / "public.pem"
    generate_signing_keypair(private, public)
    envelope = sign_envelope("https://example.com", private, issuer="test")
    result = verify_signed_envelope(envelope, public)
    assert result["payload"] == "https://example.com"
    assert result["signature_valid"] is True
