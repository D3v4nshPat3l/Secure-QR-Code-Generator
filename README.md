# Secure QR Code Generator

<p align="center"><img src="assets/banner.svg" alt="Secure QR Code Generator" width="100%"></p>


A security-focused Python QR toolkit for generating, decoding, analyzing, signing, and encrypting QR payloads on Windows, Linux, Kali Linux, and macOS.

## What “secure” means

The project separates four controls:

- **Validation** checks payload structure and blocks deceptive or malformed input.
- **Rendering verification** decodes the generated image and compares it with the requested payload.
- **Signatures** provide authenticity and tamper detection through Ed25519.
- **Encryption** provides confidentiality and integrity through AES-256-GCM with a scrypt-derived key.

No QR tool can guarantee that a destination remains trustworthy. Read [the threat model](docs/threat-model.md).

## Major protections

- Plain-text mode rejects URI/action payloads unless explicitly overridden.
- HTTPS URLs are canonicalized and checked for credentials, malformed ports, invalid DNS labels, private literal IPs, Unicode controls, and current private DNS answers.
- Wi-Fi passwords use hidden interactive input and redacted previews.
- Existing files are not overwritten without `--overwrite`.
- Secret and financial images receive restrictive Unix file permissions.
- Foreground/background contrast and quiet-zone requirements are enforced.
- PNG output is decoded after rendering by default.
- Decoder mode never opens the decoded destination.

## Installation

```bash
python -m venv venv
# Linux/macOS
source venv/bin/activate
# Windows
# venv\Scripts\activate

python -m pip install --upgrade pip
python -m pip install -e .
```

For a reproducible runtime install, use `python -m pip install -r requirements.lock`.

The installed command is `secure-qr`. The existing `secure_qr_generator.py` entry point and legacy `--type` syntax remain supported.

## Generate examples

```bash
secure-qr generate --type url --url example.com --filename example --yes
secure-qr generate --type text --text "Hello" --yes
secure-qr generate --type upi --upi-id person@bank --name "Receiver" --amount 100 --yes
```

### Wi-Fi without exposing the password in shell history

```bash
secure-qr generate --type wifi --ssid Office --security WPA --yes
```

The tool prompts with hidden input. Automation can use standard input or a protected file:

```bash
printf '%s\n' 'correct-password' | secure-qr generate --type wifi --ssid Office --yes
secure-qr generate --type wifi --ssid Office --password-file ./wifi.secret --yes
```

## Decode and analyze safely

```bash
secure-qr decode output/example.png
```

The command prints the payload, classification, risk level, and findings. It does not launch a browser or application.

## Signed QR envelopes

```bash
secure-qr keygen --private-key issuer-private.pem --public-key issuer-public.pem
secure-qr sign 'https://example.com' --private-key issuer-private.pem --issuer example.org
secure-qr verify 'SQRS1:...' --public-key issuer-public.pem
```

Do not commit private keys.

## Encrypted QR envelopes

```bash
secure-qr encrypt 'confidential payload'
secure-qr decrypt 'SQRE1:...'
```

Project envelopes require this project's verifier/decrypter; standard scanner apps display them as text.

## Batch mode

CSV columns for the initial batch schemas include `type`, `filename`, and the fields required by `text`, `url`, or `wifi`.

```bash
secure-qr batch examples.csv --dry-run
secure-qr batch examples.csv --output-dir output --report batch-report.json
```

Batch mode caps input at 1,000 rows, detects duplicate filenames, validates every record, and returns per-row errors.

## Output controls

```bash
secure-qr generate --type text --text Hello \
  --output-dir output --filename hello --format png \
  --error-correction H --fill-color black --back-color white --yes
```

Use `--overwrite` only when replacement is intentional. Use `--no-verify` only when OpenCV is unavailable or verification is intentionally disabled.

## Development

```bash
python -m pip install -e ".[dev]"
pytest --cov=secure_qr
ruff check .
```

CI tests Python 3.10 and 3.12 on Linux, Windows, and macOS. Separate workflows run dependency auditing, CodeQL, and release builds for Python distributions and a Windows executable.

## Documentation

- [Threat model](docs/threat-model.md)
- [Payload and envelope formats](docs/payload-formats.md)
- [Security reporting](SECURITY.md)
- [Contributing](CONTRIBUTING.md)

## License

MIT
