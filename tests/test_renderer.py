from pathlib import Path

import pytest

from secure_qr.errors import SecurityError
from secure_qr.payloads import text_payload
from secure_qr.renderer import decode_qr_image, render_qr


def test_render_decode_round_trip(tmp_path: Path) -> None:
    payload = text_payload("Hello secure QR")
    path = render_qr(payload, output_dir=tmp_path, filename="test", verify=True)
    assert path.exists()
    assert decode_qr_image(path) == payload.data


def test_no_overwrite_by_default(tmp_path: Path) -> None:
    payload = text_payload("Hello")
    render_qr(payload, output_dir=tmp_path, filename="test", verify=False)
    with pytest.raises(SecurityError):
        render_qr(payload, output_dir=tmp_path, filename="test", verify=False)
