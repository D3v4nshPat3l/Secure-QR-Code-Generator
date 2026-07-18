"""Command-line interface for generation, decoding, batch use, signing, and encryption."""

from __future__ import annotations

import argparse
import getpass
import json
import sys
import tempfile
from pathlib import Path

from .batch import generate_batch
from .decoder import decode_and_analyze
from .errors import SecurityError
from .models import Payload
from .payloads import (
    calendar_payload,
    email_payload,
    geo_payload,
    json_payload,
    phone_payload,
    sms_payload,
    text_payload,
    upi_payload,
    url_payload,
    vcard_payload,
    whatsapp_payload,
    wifi_payload,
)
from .renderer import decode_qr_image, render_qr
from .security import (
    decrypt_payload,
    encrypt_payload,
    generate_signing_keypair,
    sign_envelope,
    verify_signed_envelope,
)

DEFAULT_OUTPUT = Path("output")
COMMANDS = {
    "generate",
    "decode",
    "batch",
    "keygen",
    "sign",
    "verify",
    "encrypt",
    "decrypt",
    "self-test",
    "interactive",
}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="secure-qr",
        description="Security-focused QR generator and passive analyzer",
    )
    sub = parser.add_subparsers(dest="command")

    gen = sub.add_parser("generate", help="Generate a QR code")
    gen.add_argument(
        "--type",
        required=True,
        choices=[
            "text",
            "url",
            "phone",
            "sms",
            "email",
            "whatsapp",
            "wifi",
            "vcard",
            "upi",
            "geo",
            "calendar",
            "json",
        ],
    )
    value_arguments = [
        "text",
        "url",
        "phone",
        "message",
        "email",
        "subject",
        "body",
        "ssid",
        "password",
        "password-file",
        "security",
        "name",
        "company",
        "title",
        "upi-id",
        "amount",
        "note",
        "reference",
        "latitude",
        "longitude",
        "label",
        "start",
        "end",
        "location",
        "description",
    ]
    for name in value_arguments:
        gen.add_argument(f"--{name}", default="")
    gen.add_argument("--hidden", action="store_true")
    gen.add_argument("--allow-uri-like-text", action="store_true")
    gen.add_argument("--no-dns-check", action="store_true")
    gen.add_argument("--show-secrets", action="store_true")
    gen.add_argument("--filename", default="")
    gen.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    gen.add_argument("--format", choices=["png", "svg"], default="png")
    gen.add_argument("--fill-color", default="black")
    gen.add_argument("--back-color", default="white")
    gen.add_argument("--error-correction", choices=["L", "M", "Q", "H"], default="H")
    gen.add_argument("--overwrite", action="store_true")
    gen.add_argument("--no-verify", action="store_true")
    gen.add_argument("--yes", action="store_true")

    dec = sub.add_parser("decode", help="Decode and analyze a QR image without opening it")
    dec.add_argument("image", type=Path)

    batch = sub.add_parser("batch", help="Generate QR codes from CSV or JSON")
    batch.add_argument("input", type=Path)
    batch.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    batch.add_argument("--dry-run", action="store_true")
    batch.add_argument("--report", type=Path)

    keys = sub.add_parser("keygen", help="Generate an Ed25519 signing key pair")
    keys.add_argument("--private-key", type=Path, default=Path("secure-qr-private.pem"))
    keys.add_argument("--public-key", type=Path, default=Path("secure-qr-public.pem"))
    keys.add_argument("--overwrite", action="store_true")

    sign = sub.add_parser("sign", help="Create a signed QR envelope")
    sign.add_argument("payload")
    sign.add_argument("--private-key", required=True, type=Path)
    sign.add_argument("--issuer", default="")
    sign.add_argument("--expires-at", default="")

    verify = sub.add_parser("verify", help="Verify a signed QR envelope")
    verify.add_argument("payload")
    verify.add_argument("--public-key", required=True, type=Path)

    enc = sub.add_parser("encrypt", help="Encrypt a payload using AES-256-GCM and scrypt")
    enc.add_argument("payload")
    enc.add_argument("--password", default="")

    decrypt = sub.add_parser("decrypt", help="Decrypt an SQRE1 payload")
    decrypt.add_argument("payload")
    decrypt.add_argument("--password", default="")

    sub.add_parser("self-test", help="Run an isolated generation and decode round-trip test")
    sub.add_parser("interactive", help="Start the terminal menu")
    return parser


def _secret_password(args: argparse.Namespace) -> str:
    if args.password_file:
        path = Path(args.password_file)
        return path.read_text(encoding="utf-8").rstrip("\r\n")
    if args.password:
        print(
            "Warning: --password may be exposed in shell history/process listings; "
            "prefer --password-file or interactive input.",
            file=sys.stderr,
        )
        return args.password
    if not sys.stdin.isatty():
        return sys.stdin.readline().rstrip("\r\n")
    return getpass.getpass("Wi-Fi password: ")


def _build_payload(args: argparse.Namespace) -> Payload:
    kind = args.type
    if kind == "text":
        return text_payload(args.text, allow_uri_like=args.allow_uri_like_text)
    if kind == "url":
        return url_payload(args.url, dns_check=not args.no_dns_check)
    if kind == "phone":
        return phone_payload(args.phone)
    if kind == "sms":
        return sms_payload(args.phone, args.message)
    if kind == "email":
        return email_payload(args.email, args.subject, args.body)
    if kind == "whatsapp":
        return whatsapp_payload(args.phone, args.message)
    if kind == "wifi":
        return wifi_payload(
            args.ssid,
            _secret_password(args),
            args.security or "WPA",
            args.hidden,
        )
    if kind == "vcard":
        return vcard_payload(
            args.name,
            args.phone,
            args.email,
            args.company,
            args.url,
            args.title,
        )
    if kind == "upi":
        return upi_payload(args.upi_id, args.name, args.amount, args.note, args.reference)
    if kind == "geo":
        return geo_payload(args.latitude, args.longitude, args.label)
    if kind == "calendar":
        return calendar_payload(
            args.title,
            args.start,
            args.end,
            args.location,
            args.description,
        )
    if kind == "json":
        return json_payload(args.text)
    raise SecurityError(f"Unsupported QR type: {kind}")


def _legacy_to_command(argv: list[str]) -> list[str]:
    if "--self-test" in argv:
        return ["self-test"]
    if "--type" in argv and (not argv or argv[0] not in COMMANDS):
        return ["generate", *argv]
    return argv


def _interactive_argv() -> list[str]:
    print(
        """
=================================
 Secure QR Security Toolkit
=================================
1. Safe text
2. HTTPS URL
3. Phone
4. SMS
5. Email
6. WhatsApp
7. Wi-Fi
8. Contact / vCard
9. UPI payment
10. Geographic location
11. Calendar event
12. Canonical JSON
"""
    )
    choice = input("Choose QR type: ").strip()
    values: dict[str, list[str]] = {
        "1": ["--type", "text", "--text", input("Text: ")],
        "2": ["--type", "url", "--url", input("HTTPS URL: ")],
        "3": ["--type", "phone", "--phone", input("Phone number: ")],
        "4": [
            "--type",
            "sms",
            "--phone",
            input("Phone number: "),
            "--message",
            input("Message: "),
        ],
        "5": [
            "--type",
            "email",
            "--email",
            input("Email: "),
            "--subject",
            input("Subject, optional: "),
            "--body",
            input("Body, optional: "),
        ],
        "6": [
            "--type",
            "whatsapp",
            "--phone",
            input("WhatsApp number with country code: "),
            "--message",
            input("Message, optional: "),
        ],
        "7": [
            "--type",
            "wifi",
            "--ssid",
            input("Wi-Fi SSID: "),
            "--security",
            input("Security WPA/WEP/nopass [WPA]: ") or "WPA",
        ],
        "8": [
            "--type",
            "vcard",
            "--name",
            input("Full name: "),
            "--phone",
            input("Phone, optional: "),
            "--email",
            input("Email, optional: "),
            "--company",
            input("Company, optional: "),
            "--url",
            input("Website, optional: "),
        ],
        "9": [
            "--type",
            "upi",
            "--upi-id",
            input("UPI ID: "),
            "--name",
            input("Receiver name: "),
            "--amount",
            input("Amount, optional: "),
        ],
        "10": [
            "--type",
            "geo",
            "--latitude",
            input("Latitude: "),
            "--longitude",
            input("Longitude: "),
            "--label",
            input("Label, optional: "),
        ],
        "11": [
            "--type",
            "calendar",
            "--title",
            input("Event title: "),
            "--start",
            input("Start ISO-8601: "),
            "--end",
            input("End ISO-8601: "),
            "--location",
            input("Location, optional: "),
        ],
        "12": ["--type", "json", "--text", input("JSON: ")],
    }
    if choice not in values:
        raise SecurityError("Invalid menu choice.")
    argv = ["generate", *values[choice]]
    if choice == "7" and input("Hidden network? yes/no: ").strip().lower() == "yes":
        argv.append("--hidden")
    filename = input("Filename, optional: ").strip()
    if filename:
        argv += ["--filename", filename]
    return argv


def _run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="secure-qr-self-test-") as temp_dir:
        payload = text_payload("Secure QR round-trip self-test")
        path = render_qr(
            payload,
            output_dir=Path(temp_dir),
            filename="self_test",
            verify=True,
        )
        decoded = decode_qr_image(path)
        if decoded != payload.data:
            raise SecurityError("Self-test decode did not match the source payload.")
    print("Self-test passed: generation, atomic write, and decode verification succeeded.")
    return 0


def main(argv: list[str] | None = None) -> int:
    argv = _legacy_to_command(list(sys.argv[1:] if argv is None else argv))
    if not argv:
        argv = ["interactive"] if sys.stdin.isatty() else ["--help"]
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        if args.command == "interactive":
            return main(_interactive_argv())
        if args.command == "self-test":
            return _run_self_test()
        if args.command == "generate":
            payload = _build_payload(args)
            print("Payload preview:")
            print(payload.preview(reveal_secrets=args.show_secrets))
            for warning in payload.warnings:
                print(f"Warning: {warning}", file=sys.stderr)
            if not args.yes:
                answer = input("Generate this QR? yes/no: ").strip().lower()
                if answer != "yes":
                    print("QR generation cancelled.")
                    return 0
            path = render_qr(
                payload,
                output_dir=args.output_dir,
                filename=args.filename or None,
                fmt=args.format,
                foreground=args.fill_color,
                background=args.back_color,
                error_correction=args.error_correction,
                overwrite=args.overwrite,
                verify=not args.no_verify,
            )
            print(f"QR code saved: {path}")
            return 0
        if args.command == "decode":
            report = decode_and_analyze(args.image)
            print(
                json.dumps(
                    {
                        "kind": report.kind,
                        "risk": report.risk,
                        "payload": report.payload,
                        "findings": report.findings,
                    },
                    indent=2,
                )
            )
            return 0
        if args.command == "batch":
            report = generate_batch(args.input, args.output_dir, dry_run=args.dry_run)
            rendered = json.dumps(report, indent=2)
            print(rendered)
            if args.report:
                args.report.write_text(rendered + "\n", encoding="utf-8")
            return 1 if any(row["status"] == "error" for row in report) else 0
        if args.command == "keygen":
            generate_signing_keypair(
                args.private_key,
                args.public_key,
                overwrite=args.overwrite,
            )
            print(f"Private key: {args.private_key}\nPublic key: {args.public_key}")
            return 0
        if args.command == "sign":
            print(
                sign_envelope(
                    args.payload,
                    args.private_key,
                    issuer=args.issuer,
                    expires_at=args.expires_at,
                )
            )
            return 0
        if args.command == "verify":
            print(
                json.dumps(
                    verify_signed_envelope(args.payload, args.public_key),
                    indent=2,
                )
            )
            return 0
        if args.command == "encrypt":
            password = args.password or getpass.getpass("Encryption password: ")
            print(encrypt_payload(args.payload, password))
            return 0
        if args.command == "decrypt":
            password = args.password or getpass.getpass("Decryption password: ")
            print(decrypt_payload(args.payload, password))
            return 0
        parser.print_help()
        return 2
    except SecurityError as exc:
        print(f"Security error: {exc}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print("Cancelled.", file=sys.stderr)
        return 130


if __name__ == "__main__":
    raise SystemExit(main())
