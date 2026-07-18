# Feature Guide

This document explains the original QR generator functionality and the enhanced security-toolkit features introduced in version 0.2.

---

# 1. Payload generation

## Safe text

Stores plain text while blocking content that resembles a URI or application action.

Protected by:

- Unicode NFC normalization;
- control-character rejection;
- invisible-format-character rejection;
- payload-size limits;
- URI-prefix detection.

Use `--allow-uri-like-text` only when the URI-like text is intentional.

## HTTPS URL

Generates public HTTPS URLs.

Checks include:

- scheme must be HTTPS;
- no embedded username or password;
- valid port;
- public literal IP requirement;
- IDNA conversion;
- valid DNS labels;
- no whitespace or backslashes;
- optional DNS resolution;
- rejection of current private/non-public DNS answers.

The canonical output excludes URL fragments.

## Phone, SMS, email, and WhatsApp

These builders validate:

- international-style phone number length;
- optional leading `+`;
- email syntax and length;
- correct URI encoding of messages, subjects, and bodies.

They are marked as personal-data payloads.

## Wi-Fi

Supports:

- WPA;
- WEP;
- open networks (`nopass`);
- hidden networks;
- 8–63-byte WPA passphrases;
- 64-character hexadecimal WPA PSKs;
- WEP key validation;
- escaped QR Wi-Fi delimiters.

Security behavior:

- password is hidden during interactive input;
- preview is redacted;
- standard input and password files are supported;
- output receives restrictive Unix permissions.

## vCard

Creates vCard 3.0 contacts with optional:

- phone;
- email;
- company;
- job title;
- HTTPS website.

Values are escaped for commas, semicolons, backslashes, and line breaks.

## UPI payment

Supports:

- UPI ID;
- receiver name;
- optional positive amount;
- optional transaction note;
- optional transaction reference;
- INR currency declaration.

Amounts are limited to two decimal places and a maximum of 10,000,000.

Payment payloads are marked as financial and receive stricter output permissions.

## Geographic location

Creates:

```text
geo:latitude,longitude
```

Optional labels are encoded into the query.

Ranges:

- latitude: -90 to 90;
- longitude: -180 to 180.

## Calendar event

Creates iCalendar data with:

- title;
- ISO-8601 start;
- ISO-8601 end;
- optional location;
- optional description.

The end must be later than the start, and both values must use compatible timezone forms.

## Canonical JSON

Parses JSON and serializes it with:

- sorted keys;
- compact separators;
- preserved Unicode;
- stable output formatting.

Invalid JSON is rejected.

---

# 2. Passive decoder and risk analyzer

The decoder never launches a destination.

It reports:

```json
{
  "kind": "url",
  "risk": "low",
  "payload": "https://example.com",
  "findings": []
}
```

Recognized categories:

- text;
- URL;
- custom URI;
- phone/SMS/email action URI;
- Wi-Fi;
- UPI payment;
- signed envelope;
- encrypted envelope.

Analysis examples:

- dangerous URI schemes become `critical`;
- HTTP destinations become `high`;
- Wi-Fi credentials become `high`;
- payments become `high`;
- phone/message/email actions become `medium`;
- internationalized hostnames receive additional findings;
- private IP references are highlighted;
- `@` in URI data is flagged for userinfo/hostname confusion.

---

# 3. Rendering safeguards

## Atomic writes

The image is first written to a temporary file in the destination directory.

Only after successful generation and verification is it moved into the requested final path. This reduces incomplete or partially written files.

## No-clobber default

Existing files are not replaced unless:

```text
--overwrite
```

is supplied.

## Path containment

The filename cannot contain a directory path. The resolved output must remain inside the selected output directory.

## Automatic filenames

When no filename is supplied, the toolkit creates a UTC timestamp plus a random suffix.

## Contrast validation

Foreground and background colors must reach a contrast ratio of at least 4.5:1.

## Quiet zone

The renderer requires at least four modules of blank border around the QR.

## Error correction

Supported levels:

- L;
- M;
- Q;
- H.

H is the default.

## Round-trip PNG verification

After PNG generation, the toolkit:

1. reads the image;
2. detects the QR;
3. decodes the payload;
4. compares it byte-for-byte with the requested text;
5. rejects the image when they differ.

SVG output is generated securely but does not currently receive the same automatic decode verification.

## PNG and SVG

PNG is suitable for general use and automatic decode verification.

SVG is suitable for scalable printing and design workflows.

---

# 4. Digital signatures

Signed envelopes use:

- prefix: `SQRS1:`;
- Ed25519 signatures;
- canonical JSON;
- version field;
- algorithm field;
- payload;
- issuer;
- issued timestamp;
- optional expiration;
- random nonce;
- signature.

Signing answers:

```text
Was this payload created by the holder of the trusted private key?
Was the signed content modified?
Has the envelope expired?
```

Signing does not hide the content.

Trust still depends on obtaining the correct public key through an independent trusted channel.

---

# 5. Encryption

Encrypted envelopes use:

- prefix: `SQRE1:`;
- AES-256-GCM;
- scrypt key derivation;
- random 16-byte salt;
- random 12-byte nonce;
- authenticated associated data;
- minimum 12-character password.

Encryption provides:

- confidentiality;
- integrity;
- wrong-password detection;
- payload-modification detection.

Encryption does not prove who created the message.

---

# 6. Batch processing

Inputs:

- CSV;
- JSON array of objects.

Supported types:

- text;
- URL;
- Wi-Fi.

Controls:

- 1,000-row maximum;
- duplicate filename detection;
- per-row validation;
- dry-run mode;
- JSON report;
- nonzero exit code when any row fails.

Batch Wi-Fi input may contain plaintext passwords in the source file. Protect and delete such files appropriately.

---

# 7. Interactive and automated operation

Interfaces:

- interactive menu;
- modern subcommands;
- legacy `--type` compatibility;
- Windows launcher;
- Linux/macOS launcher;
- Python module invocation;
- packaged console command;
- Windows executable release builds.

Equivalent examples:

```bash
secure-qr generate --type url --url example.com --yes
```

```bash
python -m secure_qr.cli generate --type url --url example.com --yes
```

```bash
python secure_qr_generator.py --type url --url example.com --yes
```

---

# 8. Security automation and repository quality

The repository includes:

## Cross-platform tests

Matrix:

- Ubuntu;
- Windows;
- macOS;
- Python 3.10;
- Python 3.12.

Checks:

- pytest;
- coverage;
- Ruff.

## Dependency auditing

`pip-audit` checks installed dependencies for known published vulnerabilities.

## CodeQL

GitHub CodeQL scans the Python codebase.

## SBOM

CycloneDX creates a software bill of materials artifact.

## Dependabot

Monitors:

- Python dependencies;
- GitHub Actions.

## Release builds

Tag pushes build:

- Python wheel;
- source distribution;
- Windows `secure-qr.exe`.

---

# 9. Security model summary

| Data type | Sensitivity | Main controls |
|---|---|---|
| Plain text | General | URI detection, Unicode validation |
| URL | Active destination | HTTPS, parsing, DNS/IP checks |
| Phone/SMS/email | Personal | Syntax checks, encoding |
| Wi-Fi | Secret | Hidden input, redaction, secure permissions |
| vCard/calendar/JSON | Personal | Structured validation and escaping |
| UPI | Financial | ID/amount validation, secure permissions |
| Signed envelope | Authenticity metadata | Ed25519 verification |
| Encrypted envelope | Secret | AES-GCM and scrypt |

---

# 10. Known limitations

- DNS checks are a point-in-time observation.
- URL validation is not a reputation service.
- QR readers differ in protocol interpretation.
- A physical QR label can be replaced.
- Signed envelopes require the correct public key.
- Encrypted envelopes depend on password secrecy and strength.
- Project envelopes are not automatically understood by ordinary scanners.
- Batch mode currently supports only text, URL, and Wi-Fi.
- SVG output is not currently round-trip decoded.
- File permission hardening is stronger on Unix-like systems than Windows.
