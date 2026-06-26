# Secure QR Code Generator

A Linux/Kali-compatible Python QR Code Generator with built-in security validation.

## Features

- Safe text QR
- HTTPS URL QR
- Phone call QR
- SMS QR
- Email QR
- WhatsApp QR
- Wi-Fi QR
- Contact / vCard QR
- UPI payment QR

## Project Structure

```text
secure-qr-code-generator/
├── secure_qr_generator.py
├── requirements.txt
├── install.sh
├── run.sh
├── README.md
├── .gitignore
└── output/
```

## Kali/Linux Installation

```bash
git clone <your-repo-url>
cd secure-qr-code-generator
bash install.sh
```

## Manual Installation

```bash
sudo apt update
sudo apt install -y python3 python3-venv python3-pip

python3 -m venv venv
source venv/bin/activate

pip install --upgrade pip
pip install -r requirements.txt

python secure_qr_generator.py --self-test
```

## Interactive Usage

```bash
source venv/bin/activate
python secure_qr_generator.py
```

Or:

```bash
./run.sh
```

## CLI Usage

### Phone QR

```bash
python secure_qr_generator.py --type phone --phone 9754485390 --filename phone_qr --yes
```

### HTTPS URL QR

```bash
python secure_qr_generator.py --type url --url github.com --filename github_qr --yes
```

### Text QR

```bash
python secure_qr_generator.py --type text --text "Hello Cyber World" --filename text_qr --yes
```

### WhatsApp QR

```bash
python secure_qr_generator.py --type whatsapp --phone 919754485390 --message "Hello from QR" --filename whatsapp_qr --yes
```

### SMS QR

```bash
python secure_qr_generator.py --type sms --phone 9754485390 --message "Hello from QR" --filename sms_qr --yes
```

### Email QR

```bash
python secure_qr_generator.py \
  --type email \
  --email test@example.com \
  --subject "Hello" \
  --body "This is a test email from QR" \
  --filename email_qr \
  --yes
```

### Wi-Fi QR

```bash
python secure_qr_generator.py \
  --type wifi \
  --ssid "MyWiFi" \
  --password "password123" \
  --security WPA \
  --hidden no \
  --filename wifi_qr \
  --yes
```

### UPI QR

```bash
python secure_qr_generator.py \
  --type upi \
  --upi-id username@upi \
  --name "Receiver Name" \
  --amount 100 \
  --filename upi_qr \
  --yes
```

## Self-Test

```bash
python secure_qr_generator.py --self-test
```

Expected output:

```text
Self-test passed.
Generated: /path/to/repo/output/self_test_phone_9754485390.png
```

## View Output

```bash
ls -lh output/
xdg-open output/phone_qr.png
```

## Security Features

The project blocks risky URI schemes such as:

```text
javascript:
data:
file:
vbscript:
intent:
market:
shell:
cmd:
powershell:
ms-excel:
ms-word:
ms-powerpoint:
```

It also validates:

- URLs
- Phone numbers
- Email addresses
- Wi-Fi payloads
- UPI IDs
- Output filenames
- Payload length
- QR colors

Only HTTPS URLs are allowed. Localhost, loopback, private IPs, link-local addresses, multicast addresses, reserved addresses, and unspecified addresses are blocked.

## Dependencies

```text
qrcode[pil]
pillow
```
