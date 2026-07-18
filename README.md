# Secure QR Code Generator

<p align="center">
  <img src="assets/banner.svg" alt="Secure QR Code Generator banner" width="100%">
</p>

<p align="center">
  <strong>A security-focused QR toolkit for generating, decoding, analyzing, signing, and encrypting QR payloads.</strong>
</p>

<p align="center">
  <a href="https://github.com/D3v4nshPat3l/Secure-QR-Code-Generator/actions/workflows/test.yml">
    <img src="https://github.com/D3v4nshPat3l/Secure-QR-Code-Generator/actions/workflows/test.yml/badge.svg" alt="Tests">
  </a>
  <a href="https://github.com/D3v4nshPat3l/Secure-QR-Code-Generator/actions/workflows/security.yml">
    <img src="https://github.com/D3v4nshPat3l/Secure-QR-Code-Generator/actions/workflows/security.yml/badge.svg" alt="Security">
  </a>
  <img src="https://img.shields.io/badge/Python-3.10%2B-blue?logo=python" alt="Python 3.10+">
  <img src="https://img.shields.io/badge/Version-0.2.0-6f42c1" alt="Version 0.2.0">
  <img src="https://img.shields.io/badge/License-MIT-green" alt="MIT License">
  <img src="https://img.shields.io/badge/Platforms-Windows%20%7C%20Linux%20%7C%20Kali%20%7C%20macOS-lightgrey" alt="Supported platforms">
</p>

---

## Overview

**Secure QR Code Generator** started as a terminal utility for creating validated QR codes. It has now evolved into a broader QR security toolkit with:

- protocol-aware QR generation;
- passive QR decoding and risk analysis;
- safe handling of Wi-Fi passwords and sensitive payloads;
- PNG and SVG output;
- post-render QR decode verification;
- Ed25519 digital signatures;
- AES-256-GCM encrypted payload envelopes;
- CSV and JSON batch generation;
- automated tests, dependency auditing, CodeQL, SBOM creation, and release builds.

The project runs on **Windows, Linux, Kali Linux, and macOS** with Python 3.10 or newer.

> [!IMPORTANT]
> A QR code is a container for data. It does not make a URL, payment request, credential, or application action trustworthy. This project reduces common risks, but users must still inspect and confirm sensitive actions.

---

## What “secure” means in this project

The toolkit separates four different security controls:

| Control | What it provides | What it does not provide |
|---|---|---|
| **Validation** | Rejects malformed, deceptive, dangerous, or incorrectly structured input | It cannot prove that a valid destination is honest |
| **Rendering verification** | Decodes a generated PNG and confirms it contains the requested payload | It does not protect a printed QR from later physical replacement |
| **Digital signatures** | Proves authenticity and detects payload modification using Ed25519 | Standard camera apps do not automatically verify project signatures |
| **Encryption** | Hides content and protects integrity using AES-256-GCM and scrypt | The password must still be shared securely |

Read the complete [threat model](docs/threat-model.md) before using the tool for sensitive workflows.

---

## Major features

### QR generation

Generate QR codes for:

| Type | Example use |
|---|---|
| Safe text | Notes, IDs, controlled plain text |
| HTTPS URL | Public web destinations |
| Phone | Open the phone dialer |
| SMS | Open a prepared text message |
| Email | Open an email composer |
| WhatsApp | Open a WhatsApp chat |
| Wi-Fi | Join WPA, WEP, or open networks |
| vCard | Save contact information |
| UPI | Create an Indian UPI payment request |
| Geographic location | Open coordinates in a map application |
| Calendar event | Add an iCalendar event |
| Canonical JSON | Store normalized structured data |

### QR security and analysis

- Detects URI-like payloads hidden inside plain-text mode.
- Blocks dangerous URI schemes.
- Requires HTTPS for URL generation.
- Rejects embedded URL usernames and passwords.
- Validates ports, DNS labels, Unicode, IDNA hostnames, and literal IP addresses.
- Optionally checks current DNS answers for private or non-public addresses.
- Never automatically opens decoded URLs or application actions.
- Classifies decoded content and reports a risk level with findings.
- Highlights payment recipients, payment amounts, custom URI schemes, HTTP destinations, and private IP references.

### Safe output handling

- Prevents silent overwrite unless `--overwrite` is used.
- Uses atomic temporary-file writes.
- Restricts Unix permissions for secret and financial QR images.
- Validates foreground/background contrast.
- Requires an adequate QR quiet zone.
- Supports error-correction levels `L`, `M`, `Q`, and `H`.
- Verifies generated PNG files by decoding them and comparing the result.
- Supports PNG and SVG export.

### Cryptographic envelopes

- Generates Ed25519 private/public key pairs.
- Creates signed `SQRS1:` envelopes.
- Supports issuer names, issue timestamps, nonces, and expiration timestamps.
- Verifies signatures and reports expiration status.
- Creates encrypted `SQRE1:` envelopes with AES-256-GCM.
- Derives encryption keys using scrypt.
- Requires encryption passwords of at least 12 characters.

### Batch and automation

- Reads CSV or JSON input.
- Supports batch generation for `text`, `url`, and `wifi`.
- Limits batches to 1,000 rows.
- Detects duplicate filenames.
- Supports dry-run validation.
- Produces machine-readable JSON reports.

---

## Original features and v0.2 improvements

| Area | Original project | Enhanced v0.2 toolkit |
|---|---|---|
| Interface | Interactive terminal and legacy CLI | Structured subcommands plus backward compatibility |
| Payload types | Text, URL, phone, SMS, email, WhatsApp, Wi-Fi, vCard, UPI | All original types plus geo, calendar, and canonical JSON |
| URL safety | HTTPS and basic private-IP checks | Canonical parsing, IDNA, Unicode controls, credentials, ports, DNS labels, and DNS analysis |
| Plain text | Character filtering | Explicit URI/action detection and override |
| Wi-Fi secrets | Normal terminal input and visible preview | Hidden input, standard input/file support, and redacted preview |
| Output | PNG | PNG and SVG |
| File safety | Controlled filename | Atomic writes, no-clobber default, secure permissions |
| Scanability | High error correction | Contrast checks, quiet-zone checks, selectable correction, decode verification |
| Decoding | Not available | Passive decoder with risk analysis |
| Authenticity | Not available | Ed25519 signatures |
| Confidentiality | Not available | AES-256-GCM encrypted envelopes |
| Batch processing | Roadmap item | CSV/JSON batch generation |
| Quality controls | Basic self-test | Automated cross-platform tests, Ruff, CodeQL, pip-audit, SBOM, and release builds |

See [FEATURES.md](docs/FEATURES.md) for the detailed feature guide.

---

# Quick start

## Option A — Windows automatic setup

### Step 1: Install Python

Install **Python 3.10 or newer** and enable:

```text
Add python.exe to PATH
```

Verify it in PowerShell or Command Prompt:

```powershell
python --version
```

### Step 2: Download or clone the repository

```powershell
git clone https://github.com/D3v4nshPat3l/Secure-QR-Code-Generator.git
cd Secure-QR-Code-Generator
```

### Step 3: Run the installer

```powershell
.\install.bat
```

The installer creates a virtual environment, installs the project, and performs a generation test.

### Step 4: Start the interactive menu

```powershell
.\run.bat
```

### Step 5: Generate a URL QR directly

```powershell
.\run.bat generate --type url --url example.com --filename example --yes
```

The generated file is saved under:

```text
output\example.png
```

---

## Option B — Linux or Kali automatic setup

### Step 1: Install the required system packages

On Debian, Ubuntu, or Kali:

```bash
sudo apt update
sudo apt install -y git python3 python3-venv python3-pip
```

### Step 2: Clone the project

```bash
git clone https://github.com/D3v4nshPat3l/Secure-QR-Code-Generator.git
cd Secure-QR-Code-Generator
```

### Step 3: Make the scripts executable

```bash
chmod +x install.sh run.sh
```

### Step 4: Install the project

```bash
./install.sh
```

### Step 5: Start the menu

```bash
./run.sh
```

---

## Option C — Manual installation on any platform

```bash
git clone https://github.com/D3v4nshPat3l/Secure-QR-Code-Generator.git
cd Secure-QR-Code-Generator

python -m venv venv
```

Activate the environment:

**Windows PowerShell**

```powershell
.\venv\Scripts\Activate.ps1
```

**Windows Command Prompt**

```bat
venv\Scripts\activate.bat
```

**Linux, Kali, or macOS**

```bash
source venv/bin/activate
```

Install:

```bash
python -m pip install --upgrade pip
python -m pip install -e .
```

Verify:

```bash
secure-qr --help
secure-qr self-test
```

A more detailed platform-by-platform guide is available in [INSTALLATION.md](docs/INSTALLATION.md).

---

# First-use walkthrough

## 1. Start the menu

```bash
secure-qr interactive
```

Running `secure-qr` without arguments in an interactive terminal also opens the menu.

## 2. Select a QR type

For example:

```text
2. HTTPS URL
```

## 3. Enter the requested information

Example:

```text
HTTPS URL: example.com
Filename, optional: example
```

## 4. Review the payload preview

The toolkit displays the exact data that will be encoded.

## 5. Confirm generation

```text
Generate this QR? yes/no: yes
```

## 6. Find the file

By default, files are saved in:

```text
output/
```

---

# Common commands

## Safe text

```bash
secure-qr generate --type text --text "Hello from Secure QR" --filename hello --yes
```

Text that looks like a URI is rejected by default. To encode URI-like text intentionally:

```bash
secure-qr generate \
  --type text \
  --text "custom:example" \
  --allow-uri-like-text \
  --yes
```

## HTTPS URL

```bash
secure-qr generate --type url --url example.com --filename website --yes
```

Disable live DNS analysis only when required:

```bash
secure-qr generate \
  --type url \
  --url https://example.com \
  --no-dns-check \
  --yes
```

## Phone

```bash
secure-qr generate --type phone --phone +919876543210 --yes
```

## SMS

```bash
secure-qr generate \
  --type sms \
  --phone +919876543210 \
  --message "Hello from QR" \
  --yes
```

## Email

```bash
secure-qr generate \
  --type email \
  --email user@example.com \
  --subject "Hello" \
  --body "Generated with Secure QR" \
  --yes
```

## WhatsApp

```bash
secure-qr generate \
  --type whatsapp \
  --phone +919876543210 \
  --message "Hello" \
  --yes
```

## Wi-Fi

The safest interactive command does not place the password in shell history:

```bash
secure-qr generate \
  --type wifi \
  --ssid "Office WiFi" \
  --security WPA \
  --filename office_wifi \
  --yes
```

The program then prompts securely:

```text
Wi-Fi password:
```

Automation can read the password from standard input:

```bash
printf '%s\n' 'correct-password' |
  secure-qr generate --type wifi --ssid "Office WiFi" --security WPA --yes
```

Or from a protected file:

```bash
secure-qr generate \
  --type wifi \
  --ssid "Office WiFi" \
  --security WPA \
  --password-file ./wifi.secret \
  --yes
```

## vCard contact

```bash
secure-qr generate \
  --type vcard \
  --name "Devansh Patel" \
  --phone +919876543210 \
  --email user@example.com \
  --company "Example Labs" \
  --title "Security Researcher" \
  --url https://example.com \
  --yes
```

## UPI payment

```bash
secure-qr generate \
  --type upi \
  --upi-id person@bank \
  --name "Receiver Name" \
  --amount 100.50 \
  --note "Invoice 1001" \
  --reference "INV-1001" \
  --yes
```

Always verify the recipient and amount inside the payment application before authorizing payment.

## Geographic coordinates

```bash
secure-qr generate \
  --type geo \
  --latitude 23.0225 \
  --longitude 72.5714 \
  --label "Ahmedabad" \
  --yes
```

## Calendar event

Use ISO-8601 timestamps:

```bash
secure-qr generate \
  --type calendar \
  --title "Security Review" \
  --start "2026-08-01T10:00:00+05:30" \
  --end "2026-08-01T11:00:00+05:30" \
  --location "Conference Room" \
  --description "Quarterly security review" \
  --yes
```

## Canonical JSON

```bash
secure-qr generate \
  --type json \
  --text '{"role":"tester","active":true}' \
  --yes
```

The JSON is parsed, sorted, and serialized into a stable compact representation.

See [COMMANDS.md](docs/COMMANDS.md) for the complete command guide.

---

# Decode and analyze a QR safely

The decoder reads the QR but **does not open its destination**:

```bash
secure-qr decode output/example.png
```

Example result:

```json
{
  "kind": "url",
  "risk": "low",
  "payload": "https://example.com",
  "findings": [
    "Canonical hostname: example.com"
  ]
}
```

Possible classifications include:

- text;
- URL;
- custom URI;
- action URI;
- Wi-Fi;
- payment;
- signed envelope;
- encrypted envelope.

Possible risk levels include:

```text
low
medium
high
critical
```

The report is advisory. It does not replace human review, browser protections, payment confirmation, or endpoint security.

---

# Signed QR envelopes

Signatures provide authenticity and tamper detection.

## Step 1: Generate a key pair

```bash
secure-qr keygen \
  --private-key issuer-private.pem \
  --public-key issuer-public.pem
```

> [!CAUTION]
> Never commit or share the private key. Keep it in a protected location.

## Step 2: Sign a payload

```bash
secure-qr sign "https://example.com" \
  --private-key issuer-private.pem \
  --issuer example.org \
  --expires-at "2026-12-31T23:59:59Z"
```

The output begins with:

```text
SQRS1:
```

## Step 3: Put the signed envelope into a QR

```bash
secure-qr generate \
  --type text \
  --text "SQRS1:PASTE_THE_SIGNED_VALUE_HERE" \
  --allow-uri-like-text \
  --yes
```

## Step 4: Verify it

```bash
secure-qr verify \
  "SQRS1:PASTE_THE_SIGNED_VALUE_HERE" \
  --public-key issuer-public.pem
```

Verification reports whether the signature is valid and whether the envelope has expired.

Standard phone scanners treat the envelope as text. They do not perform this project-specific verification automatically.

---

# Encrypted QR envelopes

Encryption hides a payload from anyone who does not have the password.

## Encrypt

```bash
secure-qr encrypt "Confidential message"
```

You will be prompted for a password of at least 12 characters.

The result begins with:

```text
SQRE1:
```

## Decrypt

```bash
secure-qr decrypt "SQRE1:PASTE_THE_ENCRYPTED_VALUE_HERE"
```

> [!WARNING]
> Do not provide the password through `--password` on shared systems unless necessary. It may remain in shell history or process listings.

Encrypted envelopes require this toolkit for decryption. Ordinary camera applications display them as text.

---

# Batch generation

Batch mode currently supports:

```text
text
url
wifi
```

## CSV example

Create `examples.csv`:

```csv
type,filename,text,url,ssid,password,security,hidden
text,welcome,Welcome to the event,,,,,
url,website,,https://example.com,,,,
wifi,guest_wifi,,,Guest Network,guest-password,WPA,false
```

Validate without writing files:

```bash
secure-qr batch examples.csv --dry-run
```

Generate the QR files:

```bash
secure-qr batch examples.csv \
  --output-dir output \
  --report batch-report.json
```

## JSON example

Create `examples.json`:

```json
[
  {
    "type": "text",
    "filename": "welcome",
    "text": "Welcome"
  },
  {
    "type": "url",
    "filename": "website",
    "url": "https://example.com"
  }
]
```

Run:

```bash
secure-qr batch examples.json --output-dir output
```

Batch mode:

- accepts up to 1,000 rows;
- validates every row;
- blocks duplicate filenames;
- reports individual row errors;
- returns a nonzero exit code if any row fails.

---

# Output customization

## SVG output

```bash
secure-qr generate \
  --type url \
  --url example.com \
  --format svg \
  --filename example_vector \
  --yes
```

## Custom colors

```bash
secure-qr generate \
  --type text \
  --text "High contrast QR" \
  --fill-color "#111111" \
  --back-color "#FFFFFF" \
  --yes
```

Low-contrast combinations are rejected.

## Error correction

```bash
secure-qr generate \
  --type text \
  --text "Important payload" \
  --error-correction H \
  --yes
```

Levels:

| Level | Approximate recovery | Typical use |
|---|---:|---|
| L | 7% | Maximum capacity |
| M | 15% | General use |
| Q | 25% | Damaged or printed labels |
| H | 30% | Highest resilience; default |

## Replace an existing output intentionally

```bash
secure-qr generate \
  --type text \
  --text "Updated value" \
  --filename example \
  --overwrite \
  --yes
```

## Disable PNG round-trip verification

```bash
secure-qr generate \
  --type text \
  --text "Example" \
  --no-verify \
  --yes
```

Use `--no-verify` only when OpenCV is unavailable or verification is intentionally disabled.

---

# Legacy compatibility

Older commands remain supported:

```bash
python secure_qr_generator.py --type url --url example.com --filename example --yes
```

The preferred modern form is:

```bash
secure-qr generate --type url --url example.com --filename example --yes
```

The launcher scripts also forward arguments:

**Windows**

```powershell
.\run.bat generate --type url --url example.com --yes
```

**Linux/Kali/macOS**

```bash
./run.sh generate --type url --url example.com --yes
```

---

# Security protections

## Unicode and parser protections

The toolkit:

- normalizes text to Unicode NFC;
- blocks ASCII control characters;
- blocks invisible and bidirectional formatting characters;
- rejects whitespace and backslashes in URLs;
- converts internationalized hostnames to IDNA form;
- validates every DNS label;
- rejects malformed and out-of-range ports.

## URL protections

URL generation:

- allows only HTTPS;
- rejects embedded usernames and passwords;
- rejects local, private, reserved, link-local, multicast, and other non-public literal IPs;
- can resolve DNS and reject current non-public answers;
- strips URL fragments during canonicalization;
- preserves paths and query strings.

DNS results can change after QR creation. A URL that is public and safe-looking now may become unsafe later.

## Sensitive-data protections

- Wi-Fi previews hide passwords by default.
- Secret and financial PNG/SVG outputs receive restrictive permissions on Unix-like systems.
- Output filenames cannot escape the selected output directory.
- Existing files are protected from accidental replacement.
- Private keys are generated with restrictive permissions on Unix-like systems.

Windows file permissions follow the permissions of the current directory and user account.

---

# Limitations

This project cannot guarantee:

- that a website remains safe;
- that a DNS record will not change;
- that a payment application displays the intended recipient correctly;
- that a physical QR label has not been replaced;
- that every scanner interprets every QR payload identically;
- that an encrypted payload is safe if the password is weak or leaked;
- that a signed payload is trusted without independently trusting the public key;
- that SVG output has been round-trip decoded—the automatic decode check applies to PNG output.

The decoder never opens destinations, but viewing or copying decoded content still requires care.

---

# Project structure

```text
Secure-QR-Code-Generator/
├── .github/
│   ├── workflows/
│   │   ├── test.yml
│   │   ├── security.yml
│   │   └── release-build.yml
│   └── dependabot.yml
├── assets/
│   ├── banner.svg
│   ├── security.svg
│   └── workflow.svg
├── docs/
│   ├── INSTALLATION.md
│   ├── FEATURES.md
│   ├── COMMANDS.md
│   ├── threat-model.md
│   └── payload-formats.md
├── output/
│   └── .gitkeep
├── src/
│   └── secure_qr/
│       ├── batch.py
│       ├── cli.py
│       ├── decoder.py
│       ├── models.py
│       ├── payloads.py
│       ├── renderer.py
│       └── security.py
├── tests/
│   ├── test_decoder.py
│   ├── test_payloads.py
│   ├── test_renderer.py
│   └── test_security.py
├── install.bat
├── install.sh
├── run.bat
├── run.sh
├── pyproject.toml
├── requirements.txt
├── requirements.lock
├── secure_qr_generator.py
├── SECURITY.md
├── CONTRIBUTING.md
├── CHANGELOG.md
└── LICENSE
```

---

# Development

Create and activate a virtual environment, then install the development dependencies:

```bash
python -m pip install -e ".[dev]"
```

Run tests:

```bash
python -m pytest -q
```

Run coverage:

```bash
pytest --cov=secure_qr --cov-report=term-missing
```

Run linting:

```bash
ruff check .
```

Run the isolated self-test:

```bash
secure-qr self-test
```

CI tests Python 3.10 and 3.12 on Windows, Linux, and macOS. Separate workflows run:

- dependency auditing;
- CodeQL analysis;
- CycloneDX SBOM generation;
- Python package builds;
- Windows executable builds.

---

# Troubleshooting

## `python` is not recognized

Install Python 3.10 or newer and enable:

```text
Add python.exe to PATH
```

Close and reopen your terminal afterward.

## PowerShell blocks virtual-environment activation

Run this for the current window only:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\venv\Scripts\Activate.ps1
```

## `secure-qr` is not recognized

Activate the project environment first.

Windows:

```powershell
.\venv\Scripts\Activate.ps1
```

Linux, Kali, or macOS:

```bash
source venv/bin/activate
```

Then reinstall:

```bash
python -m pip install -e .
```

## QR decoding or verification fails because OpenCV is missing

```bash
python -m pip install opencv-python-headless
```

## Output already exists

Choose another filename or intentionally add:

```text
--overwrite
```

## A valid internal URL is rejected

The default URL policy intentionally blocks private or non-public destinations. This tool is designed for public HTTPS QR generation.

## DNS lookup fails

The QR may still be generated with a warning when resolution fails. For offline use, explicitly add:

```text
--no-dns-check
```

More troubleshooting is available in [INSTALLATION.md](docs/INSTALLATION.md).

---

# Documentation

- [Step-by-step installation](docs/INSTALLATION.md)
- [Detailed feature guide](docs/FEATURES.md)
- [Command reference and examples](docs/COMMANDS.md)
- [Threat model](docs/threat-model.md)
- [Payload and envelope formats](docs/payload-formats.md)
- [Security policy](SECURITY.md)
- [Contributing guide](CONTRIBUTING.md)
- [Changelog](CHANGELOG.md)

---

# Roadmap

Potential future work:

- graphical desktop interface;
- camera/webcam scanning;
- more batch payload types;
- trusted issuer/key registry;
- signed QR verification inside the decoder;
- dynamic and revocable QR service;
- PDF and print-sheet export;
- logo placement with automatic scanability limits;
- hardware-backed key storage;
- broader scanner compatibility test vectors.

---

# Responsible use

Use the project only with data, systems, identities, payment details, and networks you are authorized to manage.

Do not use it to:

- impersonate another person or organization;
- hide malicious links;
- redirect users deceptively;
- steal credentials;
- replace payment recipients;
- distribute malware or harmful application actions.

Report vulnerabilities privately according to [SECURITY.md](SECURITY.md).

---

# Contributing

Contributions are welcome. Read [CONTRIBUTING.md](CONTRIBUTING.md), create a feature branch, add tests, run the quality checks, and open a pull request.

---

# License

Released under the [MIT License](LICENSE).

---

# Author

**Devansh Patel**

GitHub: [D3v4nshPat3l](https://github.com/D3v4nshPat3l)
