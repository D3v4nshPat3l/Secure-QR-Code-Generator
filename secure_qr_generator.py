#!/usr/bin/env python3

import argparse
import ipaddress
import re
from datetime import datetime
from pathlib import Path
from urllib.parse import quote, urlencode, urlparse, urlunparse

import qrcode


BASE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = BASE_DIR / "output"
OUTPUT_DIR.mkdir(exist_ok=True)

MAX_PAYLOAD_LENGTH = 2048

DANGEROUS_SCHEMES = {
    "javascript",
    "data",
    "file",
    "vbscript",
    "intent",
    "market",
    "shell",
    "cmd",
    "powershell",
    "ms-excel",
    "ms-word",
    "ms-powerpoint",
}

SAFE_TEXT_PATTERN = re.compile(r"^[a-zA-Z0-9\s.,_\-@#:/()+&?=%]*$")
PHONE_PATTERN = re.compile(r"^\+?[0-9]{7,15}$")
EMAIL_PATTERN = re.compile(r"^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$")
FILENAME_PATTERN = re.compile(r"^[a-zA-Z0-9_\-]{1,80}$")
COLOR_PATTERN = re.compile(r"^([a-zA-Z]+|#[0-9a-fA-F]{6})$")


class SecurityError(Exception):
    pass


def reject_control_chars(value: str) -> str:
    if value is None:
        raise SecurityError("Input cannot be empty.")

    if any(ord(character) < 32 or ord(character) == 127 for character in value):
        raise SecurityError("Input contains unsafe control characters.")

    return value.strip()


def check_payload_length(value: str) -> None:
    if len(value) > MAX_PAYLOAD_LENGTH:
        raise SecurityError(
            f"Payload is too long. Maximum allowed length is {MAX_PAYLOAD_LENGTH}."
        )


def reject_dangerous_scheme(value: str) -> None:
    parsed = urlparse(value.strip())

    if parsed.scheme.lower() in DANGEROUS_SCHEMES:
        raise SecurityError(f"Dangerous URI scheme blocked: {parsed.scheme}")


def is_private_or_local_host(hostname: str) -> bool:
    if not hostname:
        return True

    normalized_hostname = hostname.lower().strip("[]")

    if normalized_hostname in {"localhost", "localhost.localdomain"}:
        return True

    try:
        ip_address = ipaddress.ip_address(normalized_hostname)
        return (
            ip_address.is_private
            or ip_address.is_loopback
            or ip_address.is_link_local
            or ip_address.is_multicast
            or ip_address.is_reserved
            or ip_address.is_unspecified
        )
    except ValueError:
        return False


def validate_filename(filename: str) -> str:
    filename = (filename or "").strip()

    if not filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"qr_{timestamp}.png"

    if filename.lower().endswith(".png"):
        filename = filename[:-4]

    if not FILENAME_PATTERN.fullmatch(filename):
        raise SecurityError(
            "Unsafe filename. Use only letters, numbers, underscore, or hyphen."
        )

    return f"{filename}.png"


def validate_color(color: str, default: str) -> str:
    color = (color or "").strip() or default

    if not COLOR_PATTERN.fullmatch(color):
        raise SecurityError(
            "Unsafe color. Use a color name like black or a hex value like #000000."
        )

    return color


def validate_safe_text(text: str) -> str:
    text = reject_control_chars(text)
    reject_dangerous_scheme(text)
    check_payload_length(text)

    if not text:
        raise SecurityError("Text cannot be empty.")

    if not SAFE_TEXT_PATTERN.fullmatch(text):
        raise SecurityError(
            "Unsafe text. Avoid characters like < > ` ' \" { } [ ] | \\ ;"
        )

    return text


def validate_url(url: str) -> str:
    url = reject_control_chars(url)
    reject_dangerous_scheme(url)
    check_payload_length(url)

    if not url:
        raise SecurityError("URL cannot be empty.")

    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    parsed = urlparse(url)

    if parsed.scheme != "https":
        raise SecurityError("Only HTTPS URLs are allowed.")

    if not parsed.netloc:
        raise SecurityError("Invalid URL. Missing domain.")

    hostname = parsed.hostname

    if not hostname:
        raise SecurityError("Invalid URL. Missing hostname.")

    if is_private_or_local_host(hostname):
        raise SecurityError("Localhost, private IPs, and internal addresses are blocked.")

    if "." not in hostname:
        raise SecurityError("URL must contain a valid public domain.")

    return urlunparse(
        (
            parsed.scheme,
            parsed.netloc,
            parsed.path or "",
            "",
            parsed.query or "",
            "",
        )
    )


def validate_phone(phone: str) -> str:
    phone = reject_control_chars(phone)
    phone = phone.replace(" ", "").replace("-", "")

    if not PHONE_PATTERN.fullmatch(phone):
        raise SecurityError(
            "Invalid phone number. Use 7 to 15 digits, optionally starting with +."
        )

    return f"tel:{phone}"


def validate_sms(phone: str, message: str) -> str:
    phone = reject_control_chars(phone)
    phone = phone.replace(" ", "").replace("-", "")

    if not PHONE_PATTERN.fullmatch(phone):
        raise SecurityError("Invalid phone number.")

    message = validate_safe_text(message)
    encoded_message = quote(message, safe="")

    return f"sms:{phone}?body={encoded_message}"


def validate_email_qr(email: str, subject: str, body: str) -> str:
    email = reject_control_chars(email)

    if not EMAIL_PATTERN.fullmatch(email):
        raise SecurityError("Invalid email address.")

    subject = validate_safe_text(subject)
    body = validate_safe_text(body)

    query = urlencode(
        {
            "subject": subject,
            "body": body,
        }
    )

    return f"mailto:{email}?{query}"


def validate_whatsapp(phone: str, message: str) -> str:
    phone = reject_control_chars(phone)
    phone = phone.replace("+", "").replace(" ", "").replace("-", "")

    if not re.fullmatch(r"^[0-9]{7,15}$", phone):
        raise SecurityError("Invalid WhatsApp number. Use country code and digits only.")

    message = validate_safe_text(message)
    encoded_message = quote(message, safe="")

    return f"https://wa.me/{phone}?text={encoded_message}"


def escape_wifi_value(value: str) -> str:
    value = reject_control_chars(value)
    value = value.replace("\\", "\\\\")
    value = value.replace(";", "\\;")
    value = value.replace(",", "\\,")
    value = value.replace(":", "\\:")

    return value


def validate_wifi(ssid: str, password: str, security: str, hidden: str) -> str:
    raw_ssid = reject_control_chars(ssid)

    if not raw_ssid:
        raise SecurityError("Wi-Fi SSID cannot be empty.")

    if len(raw_ssid) > 32:
        raise SecurityError(
            "Wi-Fi SSID is too long. Maximum common SSID length is 32 characters."
        )

    ssid = escape_wifi_value(raw_ssid)
    password = reject_control_chars(password or "")
    security = (security or "").strip().upper() or "WPA"
    hidden_value = "true" if (hidden or "").strip().lower() == "yes" else "false"

    if security not in {"WPA", "WEP", "NOPASS"}:
        raise SecurityError("Security type must be WPA, WEP, or nopass.")

    if security == "NOPASS":
        return f"WIFI:T:nopass;S:{ssid};H:{hidden_value};;"

    if security == "WPA" and not (8 <= len(password) <= 63):
        raise SecurityError("WPA password should be 8 to 63 characters.")

    if security == "WEP" and len(password) not in {5, 13, 16, 29}:
        raise SecurityError("WEP password length is unusual. Use 5, 13, 16, or 29 characters.")

    password = escape_wifi_value(password)

    return f"WIFI:T:{security};S:{ssid};P:{password};H:{hidden_value};;"


def validate_vcard(
    name: str,
    phone: str,
    email: str,
    company: str,
    website: str,
) -> str:
    name = validate_safe_text(name)
    company = validate_safe_text(company) if (company or "").strip() else ""

    phone = reject_control_chars(phone)
    phone = phone.replace(" ", "").replace("-", "")

    if not PHONE_PATTERN.fullmatch(phone):
        raise SecurityError("Invalid phone number in contact card.")

    email = reject_control_chars(email or "")

    if email and not EMAIL_PATTERN.fullmatch(email):
        raise SecurityError("Invalid email in contact card.")

    website = validate_url(website) if (website or "").strip() else ""

    vcard = f"""BEGIN:VCARD
VERSION:3.0
FN:{name}
ORG:{company}
TEL:{phone}
EMAIL:{email}
URL:{website}
END:VCARD"""

    check_payload_length(vcard)

    return vcard


def validate_upi(upi_id: str, receiver_name: str, amount: str) -> str:
    upi_id = reject_control_chars(upi_id)
    receiver_name = validate_safe_text(receiver_name)

    if not re.fullmatch(r"^[a-zA-Z0-9.\-_]{2,256}@[a-zA-Z]{2,64}$", upi_id):
        raise SecurityError("Invalid UPI ID format.")

    params = {
        "pa": upi_id,
        "pn": receiver_name,
        "cu": "INR",
    }

    amount = (amount or "").strip()

    if amount:
        if not re.fullmatch(r"^[0-9]+(\.[0-9]{1,2})?$", amount):
            raise SecurityError(
                "Invalid amount. Use numbers only, example: 100 or 100.50."
            )

        params["am"] = amount

    return "upi://pay?" + urlencode(params)


def generate_qr(
    data: str,
    filename: str = "",
    fill_color: str = "black",
    back_color: str = "white",
) -> Path:
    reject_dangerous_scheme(data)
    check_payload_length(data)

    output_filename = validate_filename(filename)
    fill_color = validate_color(fill_color, "black")
    back_color = validate_color(back_color, "white")

    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4,
    )

    qr.add_data(data)
    qr.make(fit=True)

    image = qr.make_image(
        fill_color=fill_color,
        back_color=back_color,
    ).convert("RGB")

    output_path = OUTPUT_DIR / output_filename
    image.save(output_path)

    return output_path


def print_menu() -> None:
    print(
        """
=================================
 Secure QR Code Generator
 Windows / Linux / Kali Compatible
=================================

1. Safe Text QR
2. HTTPS URL QR
3. Phone Call QR
4. SMS QR
5. Email QR
6. WhatsApp QR
7. Wi-Fi QR
8. Contact / vCard QR
9. UPI Payment QR
"""
    )


def build_payload_interactive(choice: str) -> str:
    if choice == "1":
        return validate_safe_text(input("Enter safe text: "))

    if choice == "2":
        return validate_url(input("Enter HTTPS URL: "))

    if choice == "3":
        return validate_phone(input("Enter phone number: "))

    if choice == "4":
        phone = input("Enter phone number: ")
        message = input("Enter SMS message: ")
        return validate_sms(phone, message)

    if choice == "5":
        email = input("Enter email address: ")
        subject = input("Enter subject: ")
        body = input("Enter body: ")
        return validate_email_qr(email, subject, body)

    if choice == "6":
        phone = input("Enter WhatsApp number with country code: ")
        message = input("Enter WhatsApp message: ")
        return validate_whatsapp(phone, message)

    if choice == "7":
        ssid = input("Enter Wi-Fi SSID/name: ")
        password = input("Enter Wi-Fi password: ")
        security = input("Security type WPA/WEP/nopass: ")
        hidden = input("Is network hidden? yes/no: ")
        return validate_wifi(ssid, password, security, hidden)

    if choice == "8":
        name = input("Enter full name: ")
        phone = input("Enter phone number: ")
        email = input("Enter email: ")
        company = input("Enter company, optional: ")
        website = input("Enter website, optional: ")
        return validate_vcard(name, phone, email, company, website)

    if choice == "9":
        upi_id = input("Enter UPI ID: ")
        receiver_name = input("Enter receiver name: ")
        amount = input("Enter amount, optional: ")
        return validate_upi(upi_id, receiver_name, amount)

    raise SecurityError("Invalid menu choice.")


def build_payload_cli(args: argparse.Namespace) -> str:
    if args.type == "text":
        return validate_safe_text(args.text)

    if args.type == "url":
        return validate_url(args.url)

    if args.type == "phone":
        return validate_phone(args.phone)

    if args.type == "sms":
        return validate_sms(args.phone, args.message)

    if args.type == "email":
        return validate_email_qr(args.email, args.subject, args.body)

    if args.type == "whatsapp":
        return validate_whatsapp(args.phone, args.message)

    if args.type == "wifi":
        return validate_wifi(args.ssid, args.password, args.security, args.hidden)

    if args.type == "vcard":
        return validate_vcard(args.name, args.phone, args.email, args.company, args.url)

    if args.type == "upi":
        return validate_upi(args.upi_id, args.name, args.amount)

    raise SecurityError("Unsupported QR type.")


def run_self_test() -> None:
    payload = validate_phone("9754485390")
    output_path = generate_qr(payload, "self_test_phone_9754485390", "black", "white")

    if not output_path.exists() or output_path.stat().st_size == 0:
        raise RuntimeError("Self-test failed. QR file was not created correctly.")

    print("Self-test passed.")
    print(f"Generated: {output_path}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Secure Windows/Linux/Kali-compatible QR Code Generator"
    )

    parser.add_argument(
        "--type",
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
        ],
        help="QR type for CLI mode.",
    )

    parser.add_argument("--text", default="", help="Text payload for text QR.")
    parser.add_argument("--url", default="", help="URL for URL/vCard website QR.")
    parser.add_argument("--phone", default="", help="Phone number.")
    parser.add_argument("--message", default="", help="SMS or WhatsApp message.")
    parser.add_argument("--email", default="", help="Email address.")
    parser.add_argument("--subject", default="", help="Email subject.")
    parser.add_argument("--body", default="", help="Email body.")
    parser.add_argument("--ssid", default="", help="Wi-Fi SSID.")
    parser.add_argument("--password", default="", help="Wi-Fi password.")
    parser.add_argument("--security", default="WPA", help="Wi-Fi security: WPA, WEP, or nopass.")
    parser.add_argument("--hidden", default="no", help="Wi-Fi hidden network: yes or no.")
    parser.add_argument("--name", default="", help="Name for vCard/UPI receiver.")
    parser.add_argument("--company", default="", help="Company for vCard.")
    parser.add_argument("--upi-id", default="", help="UPI ID.")
    parser.add_argument("--amount", default="", help="UPI amount.")
    parser.add_argument("--filename", default="", help="Output filename without path.")
    parser.add_argument("--fill-color", default="black", help="QR foreground color.")
    parser.add_argument("--back-color", default="white", help="QR background color.")
    parser.add_argument("--yes", action="store_true", help="Skip confirmation in CLI mode.")
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="Generate a test phone QR and exit.",
    )

    return parser.parse_args()


def interactive_mode() -> None:
    print_menu()
    choice = input("Choose QR type: ").strip()
    payload = build_payload_interactive(choice)

    print("\nPayload preview:")
    print(payload)

    confirm = input("\nGenerate this QR? yes/no: ").strip().lower()

    if confirm != "yes":
        print("QR generation cancelled.")
        return

    filename = input("Enter filename, leave blank for auto-name: ")
    fill_color = input("QR color, default black: ")
    back_color = input("Background color, default white: ")

    output_path = generate_qr(payload, filename, fill_color, back_color)

    print("\nSecurity check passed.")
    print(f"QR Code saved successfully: {output_path}")


def cli_mode(args: argparse.Namespace) -> None:
    payload = build_payload_cli(args)

    print("Payload preview:")
    print(payload)

    if not args.yes:
        confirm = input("\nGenerate this QR? yes/no: ").strip().lower()

        if confirm != "yes":
            print("QR generation cancelled.")
            return

    output_path = generate_qr(
        payload,
        args.filename,
        args.fill_color,
        args.back_color,
    )

    print("\nSecurity check passed.")
    print(f"QR Code saved successfully: {output_path}")


def main() -> None:
    args = parse_args()

    try:
        if args.self_test:
            run_self_test()
            return

        if args.type:
            cli_mode(args)
            return

        interactive_mode()

    except SecurityError as error:
        print(f"\nSecurity Error: {error}")
        raise SystemExit(1)

    except KeyboardInterrupt:
        print("\nCancelled by user.")
        raise SystemExit(130)

    except Exception as error:
        print(f"\nUnexpected Error: {error}")
        raise SystemExit(1)


if __name__ == "__main__":
    main()
