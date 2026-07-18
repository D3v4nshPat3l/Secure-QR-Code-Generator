# Command Reference

The installed command is:

```bash
secure-qr
```

Alternative:

```bash
python -m secure_qr.cli
```

---

# General help

```bash
secure-qr --help
```

Commands:

```text
generate
decode
batch
keygen
sign
verify
encrypt
decrypt
self-test
interactive
```

---

# Interactive mode

```bash
secure-qr interactive
```

Running without arguments in a normal interactive terminal also starts the menu:

```bash
secure-qr
```

---

# Generate

General form:

```bash
secure-qr generate --type TYPE [TYPE OPTIONS] [OUTPUT OPTIONS]
```

Supported types:

```text
text
url
phone
sms
email
whatsapp
wifi
vcard
upi
geo
calendar
json
```

Common output options:

```text
--filename NAME
--output-dir DIRECTORY
--format png|svg
--fill-color COLOR
--back-color COLOR
--error-correction L|M|Q|H
--overwrite
--no-verify
--yes
```

## Text

```bash
secure-qr generate \
  --type text \
  --text "Hello" \
  --filename hello \
  --yes
```

URI-like override:

```bash
secure-qr generate \
  --type text \
  --text "custom:example" \
  --allow-uri-like-text \
  --yes
```

## URL

```bash
secure-qr generate \
  --type url \
  --url https://example.com/path?value=1 \
  --filename example \
  --yes
```

Offline/no-DNS mode:

```bash
secure-qr generate \
  --type url \
  --url example.com \
  --no-dns-check \
  --yes
```

## Phone

```bash
secure-qr generate \
  --type phone \
  --phone +919876543210 \
  --yes
```

## SMS

```bash
secure-qr generate \
  --type sms \
  --phone +919876543210 \
  --message "Hello" \
  --yes
```

## Email

```bash
secure-qr generate \
  --type email \
  --email user@example.com \
  --subject "Subject" \
  --body "Message body" \
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

## Wi-Fi with hidden prompt

```bash
secure-qr generate \
  --type wifi \
  --ssid "Office WiFi" \
  --security WPA \
  --yes
```

Password file:

```bash
secure-qr generate \
  --type wifi \
  --ssid "Office WiFi" \
  --security WPA \
  --password-file ./wifi.secret \
  --yes
```

Hidden network:

```bash
secure-qr generate \
  --type wifi \
  --ssid "Hidden WiFi" \
  --security WPA \
  --hidden \
  --yes
```

Open network:

```bash
secure-qr generate \
  --type wifi \
  --ssid "Guest WiFi" \
  --security nopass \
  --yes
```

Reveal the secret in the preview only when necessary:

```text
--show-secrets
```

## vCard

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

## UPI

```bash
secure-qr generate \
  --type upi \
  --upi-id person@bank \
  --name "Receiver Name" \
  --amount 100.50 \
  --note "Invoice payment" \
  --reference "INV-1001" \
  --yes
```

## Geo

```bash
secure-qr generate \
  --type geo \
  --latitude 23.0225 \
  --longitude 72.5714 \
  --label Ahmedabad \
  --yes
```

## Calendar

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

## JSON

```bash
secure-qr generate \
  --type json \
  --text '{"active":true,"role":"tester"}' \
  --yes
```

---

# Decode

```bash
secure-qr decode PATH_TO_IMAGE
```

Example:

```bash
secure-qr decode output/example.png
```

Output fields:

```text
kind
risk
payload
findings
```

The command does not open the decoded target.

---

# Batch

Dry run:

```bash
secure-qr batch examples.csv --dry-run
```

Generate:

```bash
secure-qr batch examples.csv --output-dir output
```

Save report:

```bash
secure-qr batch examples.csv \
  --output-dir output \
  --report batch-report.json
```

JSON input:

```bash
secure-qr batch examples.json --output-dir output
```

Supported batch types:

```text
text
url
wifi
```

---

# Key generation

```bash
secure-qr keygen
```

Defaults:

```text
secure-qr-private.pem
secure-qr-public.pem
```

Custom paths:

```bash
secure-qr keygen \
  --private-key issuer-private.pem \
  --public-key issuer-public.pem
```

Replace existing keys intentionally:

```text
--overwrite
```

Never commit private keys.

---

# Sign

```bash
secure-qr sign "PAYLOAD" \
  --private-key issuer-private.pem
```

With issuer:

```bash
secure-qr sign "https://example.com" \
  --private-key issuer-private.pem \
  --issuer example.org
```

With expiration:

```bash
secure-qr sign "https://example.com" \
  --private-key issuer-private.pem \
  --issuer example.org \
  --expires-at "2026-12-31T23:59:59Z"
```

Output prefix:

```text
SQRS1:
```

---

# Verify

```bash
secure-qr verify \
  "SQRS1:SIGNED_VALUE" \
  --public-key issuer-public.pem
```

Output includes:

```text
signature_valid
expired
payload
issuer
issued_at
expires_at
nonce
```

---

# Encrypt

Interactive password prompt:

```bash
secure-qr encrypt "Confidential payload"
```

Output prefix:

```text
SQRE1:
```

A password can be passed explicitly:

```bash
secure-qr encrypt "Confidential payload" \
  --password "a-strong-password"
```

Avoid this on shared systems because command-line passwords may be visible in history or process listings.

---

# Decrypt

```bash
secure-qr decrypt "SQRE1:ENCRYPTED_VALUE"
```

Explicit password:

```bash
secure-qr decrypt "SQRE1:ENCRYPTED_VALUE" \
  --password "a-strong-password"
```

---

# Self-test

```bash
secure-qr self-test
```

The self-test performs an isolated text-QR generation and decode round trip inside a temporary directory.

---

# Output examples

## SVG

```bash
secure-qr generate \
  --type url \
  --url example.com \
  --format svg \
  --yes
```

## Custom output directory

```bash
secure-qr generate \
  --type text \
  --text "Example" \
  --output-dir generated \
  --yes
```

## Custom colors

```bash
secure-qr generate \
  --type text \
  --text "Example" \
  --fill-color navy \
  --back-color white \
  --yes
```

## Maximum error correction

```bash
secure-qr generate \
  --type text \
  --text "Example" \
  --error-correction H \
  --yes
```

## Noninteractive generation

```text
--yes
```

Without `--yes`, the toolkit asks for confirmation.

---

# Legacy commands

Legacy entry point:

```bash
python secure_qr_generator.py \
  --type url \
  --url example.com \
  --filename example \
  --yes
```

Legacy self-test:

```bash
python secure_qr_generator.py --self-test
```

Windows launcher:

```powershell
.\run.bat generate --type url --url example.com --yes
```

Linux/Kali/macOS launcher:

```bash
./run.sh generate --type url --url example.com --yes
```

---

# Exit codes

| Code | Meaning |
|---:|---|
| 0 | Successful operation |
| 1 | Validation, security, batch-row, or processing failure |
| 2 | Invalid or missing command arguments |
| 130 | Cancelled with Ctrl+C |

Batch mode returns code `1` when any row reports an error.
