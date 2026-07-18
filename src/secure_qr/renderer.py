"""QR rendering with atomic writes, secure permissions, and scanability checks."""

from __future__ import annotations

import os
import tempfile
from pathlib import Path

import qrcode
from PIL import ImageColor
from qrcode.image.svg import SvgPathFillImage

from .errors import SecurityError
from .models import Payload, Sensitivity
from .security import resolve_output_path, secure_file_permissions, validate_color_contrast

ERROR_LEVELS = {
    "L": qrcode.constants.ERROR_CORRECT_L,
    "M": qrcode.constants.ERROR_CORRECT_M,
    "Q": qrcode.constants.ERROR_CORRECT_Q,
    "H": qrcode.constants.ERROR_CORRECT_H,
}


def render_qr(
    payload: Payload,
    *,
    output_dir: Path,
    filename: str | None = None,
    fmt: str = "png",
    foreground: str = "black",
    background: str = "white",
    error_correction: str = "H",
    box_size: int = 10,
    border: int = 4,
    overwrite: bool = False,
    verify: bool = True,
) -> Path:
    fmt = fmt.lower()
    if error_correction.upper() not in ERROR_LEVELS:
        raise SecurityError("Error correction must be L, M, Q, or H.")
    if not 2 <= box_size <= 50:
        raise SecurityError("Box size must be between 2 and 50.")
    if border < 4:
        raise SecurityError("QR quiet-zone border must be at least 4 modules.")
    validate_color_contrast(foreground, background)
    target = resolve_output_path(
        output_dir=output_dir, filename=filename, extension=fmt, overwrite=overwrite
    )

    qr = qrcode.QRCode(
        version=None,
        error_correction=ERROR_LEVELS[error_correction.upper()],
        box_size=box_size,
        border=border,
    )
    qr.add_data(payload.data)
    try:
        qr.make(fit=True)
    except Exception as exc:
        raise SecurityError("Payload cannot fit in a QR code with the selected settings.") from exc

    fd, temp_name = tempfile.mkstemp(prefix=".secure-qr-", suffix=f".{fmt}", dir=target.parent)
    os.close(fd)
    temp_path = Path(temp_name)
    try:
        if fmt == "png":
            image = qr.make_image(fill_color=foreground, back_color=background).convert("RGB")
            image.save(temp_path, format="PNG")
        elif fmt == "svg":
            image = qr.make_image(image_factory=SvgPathFillImage)
            image.save(temp_path)
            # qrcode's SVG factory uses fixed black/white styles; replace only those
            # generated attributes after validating both colors with Pillow.
            fg = "#%02x%02x%02x" % ImageColor.getrgb(foreground)[:3]
            bg = "#%02x%02x%02x" % ImageColor.getrgb(background)[:3]
            svg = temp_path.read_text(encoding="utf-8")
            svg = svg.replace('fill="white"', f'fill="{bg}"', 1)
            svg = svg.replace('fill="#000000"', f'fill="{fg}"', 1)
            temp_path.write_text(svg, encoding="utf-8")
        else:
            raise SecurityError("Output format must be PNG or SVG.")

        if verify and fmt == "png":
            decoded = decode_qr_image(temp_path)
            if decoded != payload.data:
                raise SecurityError("Rendered QR failed round-trip decode verification.")
        os.replace(temp_path, target)
        if payload.sensitivity in {Sensitivity.SECRET, Sensitivity.FINANCIAL}:
            secure_file_permissions(target)
        return target
    finally:
        temp_path.unlink(missing_ok=True)


def decode_qr_image(path: Path) -> str:
    try:
        import cv2
    except ImportError as exc:
        raise SecurityError(
            "QR verification/decoding requires opencv-python-headless. Install the decoder dependency."
        ) from exc
    image = cv2.imread(str(path))
    if image is None:
        raise SecurityError(f"Could not read image: {path}")
    detector = cv2.QRCodeDetector()
    data, _points, _straight = detector.detectAndDecode(image)
    if not data:
        raise SecurityError("No decodable QR code was found in the image.")
    return data
