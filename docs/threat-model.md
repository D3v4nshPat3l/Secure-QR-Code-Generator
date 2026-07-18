# Threat Model

## Security goals

The project aims to prevent accidental generation of malformed or deceptive action payloads, reduce disclosure of secrets during generation, verify that rendered QR images decode to the intended value, and provide optional authenticity and confidentiality envelopes.

## In scope

- URI parser confusion and dangerous schemes
- Local/private destination detection for literal IPs and current DNS answers
- Unicode control and bidirectional-formatting attacks
- Secret disclosure through terminal previews and output permissions
- Output path traversal, silent overwrite, and unreadable color combinations
- Tamper detection through Ed25519 signatures
- Confidential payloads through authenticated AES-256-GCM encryption

## Out of scope

- A trusted QR can still point to a site that becomes malicious later.
- DNS answers can change after generation.
- Standard scanner apps do not understand project-specific signed or encrypted envelopes.
- The tool does not guarantee safety of external payment, browser, messaging, or scanner applications.
- A compromised local machine can capture input, keys, passwords, or output images.

## Trust boundaries

Generation and decoding are local. The decoder never opens a destination automatically. DNS validation performs name resolution only; it does not make an HTTP request. Private signing keys must remain outside source control and should be protected by operating-system controls.
