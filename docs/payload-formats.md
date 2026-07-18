# Payload Formats

The generator supports plain text, HTTPS URLs, phone, SMS, email, WhatsApp, Wi-Fi, vCard 3.0, UPI, geographic coordinates, iCalendar events, and canonical JSON.

## Signed envelope

`SQRS1:` is followed by URL-safe Base64 JSON. The JSON includes a version, algorithm, payload, issuer, issuance time, optional expiration, nonce, and Ed25519 signature. Verification requires the corresponding public key.

## Encrypted envelope

`SQRE1:` is followed by URL-safe Base64 JSON containing an AES-256-GCM ciphertext, nonce, and scrypt salt. The password-derived key uses scrypt parameters N=32768, r=8, p=1. Authentication failure is treated as decryption failure.

These formats are project-specific. Ordinary scanner applications will display them as text; use `secure-qr verify` or `secure-qr decrypt` to interpret them.
