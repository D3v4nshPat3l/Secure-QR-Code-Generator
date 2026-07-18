import pytest

from secure_qr.errors import SecurityError
from secure_qr.payloads import upi_payload, vcard_payload, wifi_payload


def test_wifi_redacts_password() -> None:
    payload = wifi_payload("Office", "correct-password", "WPA", False)
    assert "correct-password" in payload.data
    assert "correct-password" not in payload.preview()
    assert "********" in payload.preview()


def test_wifi_accepts_hex_psk() -> None:
    payload = wifi_payload("Office", "a" * 64, "WPA", False)
    assert "a" * 64 in payload.data


def test_wifi_rejects_long_utf8_ssid() -> None:
    with pytest.raises(SecurityError):
        wifi_payload("é" * 32, "correct-password", "WPA", False)


def test_vcard_escapes_delimiters() -> None:
    payload = vcard_payload("Doe, Jane; CEO", company="Example, Inc")
    assert "Doe\\, Jane\\; CEO" in payload.data
    assert "Example\\, Inc" in payload.data


def test_upi_normalizes_amount() -> None:
    payload = upi_payload("person@bank", "Person", "100.50")
    assert "am=100.5" in payload.data


@pytest.mark.parametrize("amount", ["0", "-1", "1.001", "999999999"])
def test_upi_rejects_invalid_amount(amount: str) -> None:
    with pytest.raises(SecurityError):
        upi_payload("person@bank", "Person", amount)
